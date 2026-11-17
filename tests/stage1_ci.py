#!/usr/bin/env python3
"""Assertion-based integration tests for the Stage 1 fopen interceptor."""

import concurrent.futures
import datetime
import hashlib
import os
import pathlib
import re
import stat
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROBE = ROOT / "tests" / "fopen_probe"
LOGGER = ROOT / "audit_logger.so"
LOG = pathlib.Path("/tmp/access_audit.log")


def run_probe(path, mode, preload=True):
    env = os.environ.copy()
    env.pop("LD_PRELOAD", None)
    if preload:
        env["LD_PRELOAD"] = str(LOGGER)
    command = [str(PROBE), str(path), mode]
    result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=8)
    assert result.returncode == 0, (command, result)
    match = re.fullmatch(r"success=([01]) errno=(\d+) pid=(\d+)\n", result.stdout)
    assert match, result.stdout
    return (int(match.group(1)), int(match.group(2)), int(match.group(3))), result.stderr


def read_records():
    lines = LOG.read_text(encoding="utf-8").splitlines()
    entries = []
    for line in lines:
        fields = line.split("\t")
        assert len(fields) == 19, (len(fields), line)
        assert fields[0] == "v1", line
        assert fields[1] == str(os.getuid()), line
        assert fields[6] in ("0", "1", "2", "3"), line
        assert fields[7] in ("0", "1"), line
        assert fields[9] in ("success", "failure", "partial"), line
        if fields[6] in ("0", "1"):
            assert fields[11] in ("absent", "present", "unknown"), line
        else:
            assert fields[11] == "-", line
        assert fields[12] in ("0", "1"), line
        assert fields[14] in ("visible", "post-close", "unavailable"), line
        if fields[6] == "2":
            assert all(re.fullmatch(r"\d+", value) for value in fields[15:18]), line
        else:
            assert fields[15:18] == ["-", "-", "-"], line
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", fields[4]), line
        assert re.fullmatch(r"\d{2}:\d{2}:\d{2}\.\d{9}Z", fields[5]), line
        moment = datetime.datetime.fromisoformat(fields[4] + "T" + fields[5][:-1] + "+00:00")
        assert abs((datetime.datetime.now(datetime.timezone.utc) - moment).total_seconds()) < 120
        assert re.fullmatch(r"[0-9a-f]{64}|N/A", fields[8]), line
        assert (fields[14] in ("visible", "post-close")) == (fields[8] != "N/A"), line
        entries.append(fields)
    return entries


def require_event(path, probe_result, operation, denied, outcome, prior=None, digest=None):
    result, _ = probe_result
    records = [item for item in read_records()
               if item[3] == str(path) and int(item[2]) == result[2]
               and item[6] in ("0", "1")]
    assert len(records) == 1, (path, result, records)
    event = records[0]
    assert int(event[6]) == operation, event
    assert int(event[7]) == denied, event
    assert event[9] == outcome, event
    if prior is not None:
        assert event[11] == prior, event
    if digest is not None:
        assert event[8] == digest, event
    return event


def compare_with_normal(path, mode):
    expected, _ = run_probe(path, mode, preload=False)
    observed, stderr = run_probe(path, mode, preload=True)
    assert observed[:2] == expected[:2], (path, expected, observed)
    assert "audit_logger: could not append" in stderr, stderr


def main():
    assert os.geteuid() != 0, "Permission-denial tests must execute as an ordinary UID"
    assert LOGGER.is_file() and PROBE.is_file()
    assert not LOG.exists() and not LOG.is_symlink(), "CI must start with an unused audit-log path"
    descriptor = os.open(LOG, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
    os.close(descriptor)
    os.chmod(LOG, 0o666)
    try:
        assert stat.S_ISREG(LOG.stat().st_mode)
        assert stat.S_IMODE(LOG.stat().st_mode) == 0o666

        with tempfile.TemporaryDirectory(prefix="a3-stage1-") as directory:
            work = pathlib.Path(directory)
            created = work / "created.txt"
            opened = work / "existing.txt"
            opened.write_bytes(b"stage one open digest\n")
            expected_hash = hashlib.sha256(opened.read_bytes()).hexdigest()

            created_result = run_probe(created, "w")
            assert created_result[0][0] == 1 and created.exists()
            require_event(created, created_result, 0, 0, "success", prior="absent",
                          digest=hashlib.sha256(b"").hexdigest())

            opened_result = run_probe(opened, "r")
            assert opened_result[0][0] == 1
            require_event(opened, opened_result, 1, 0, "success", prior="present", digest=expected_hash)

            existing_write = run_probe(created, "w")
            require_event(created, existing_write, 1, 0, "success", prior="present")

            appended = work / "append-new.txt"
            append_result = run_probe(appended, "a")
            require_event(appended, append_result, 0, 0, "success", prior="absent")

            denied = work / "denied.txt"
            denied.write_bytes(b"private")
            denied.chmod(0o000)
            denied_result = run_probe(denied, "r")
            assert denied_result[0][:2] == (0, 13), denied_result
            require_event(denied, denied_result, 1, 1, "failure", prior="present", digest="N/A")
            denied.chmod(0o600)

            nonwritable = work / "read-only-dir"
            nonwritable.mkdir(mode=0o555)
            nonwritable.chmod(0o555)
            attempted = nonwritable / "new.txt"
            attempt_result = run_probe(attempted, "w")
            assert attempt_result[0][:2] == (0, 13), attempt_result
            attempted_event = require_event(attempted, attempt_result, 0, 1, "failure", prior="absent")
            assert attempted_event[12] == "1"
            nonwritable.chmod(0o700)

            missing = work / "missing.txt"
            missing_result = run_probe(missing, "r")
            assert missing_result[0][:2] == (0, 2)
            require_event(missing, missing_result, 1, 0, "failure", prior="absent")

            device_result = run_probe(pathlib.Path("/dev/null"), "r")
            require_event(pathlib.Path("/dev/null"), device_result, 1, 0, "success", digest="N/A")
            proc_result = run_probe(pathlib.Path("/proc/self/stat"), "r")
            require_event(pathlib.Path("/proc/self/stat"), proc_result, 1, 0, "success", digest="N/A")

            # All callers have independent processes and a shared provisioned log.
            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
                results = list(pool.map(lambda _: run_probe(opened, "r"), range(24)))
            for result in results:
                require_event(opened, result, 1, 0, "success", digest=expected_hash)
            assert len([e for e in read_records() if e[6] in ("0", "1")]) == 33

            nested = work / "nested"
            nested.mkdir()
            lexical = str(work) + "/nested/../existing.txt"
            lexical_result = run_probe(lexical, "r")
            lexical_events = [entry for entry in read_records()
                              if int(entry[2]) == lexical_result[0][2]
                              and entry[6] in ("0", "1")]
            assert len(lexical_events) == 1
            assert lexical_events[0][3] == lexical
            assert lexical_events[0][18] == str(opened)
            assert lexical_events[0][8] == expected_hash

            # An unavailable log must not rewrite a successful or denied libc result.
            LOG.unlink()
            compare_with_normal(opened, "r")
            denied.chmod(0o000)
            compare_with_normal(denied, "r")
            denied.chmod(0o600)
            assert not LOG.exists(), "Logger must not recreate the audit log"

            # Symlink substitution is rejected, leaving the destination unchanged.
            destination = work / "must-stay-unchanged.txt"
            destination.write_text("sentinel", encoding="utf-8")
            LOG.symlink_to(destination)
            compare_with_normal(opened, "r")
            assert destination.read_text(encoding="utf-8") == "sentinel"
            LOG.unlink()

            # O_NONBLOCK prevents the audit helper from blocking on an unserved FIFO.
            os.mkfifo(LOG)
            compare_with_normal(opened, "r")
            LOG.unlink()

            LOG.write_bytes(b"")
            LOG.chmod(0o444)
            compare_with_normal(opened, "r")
            LOG.chmod(0o666)
    finally:
        if LOG.is_symlink() or LOG.exists():
            LOG.unlink()

    print("PASS: assertions for fopen outcomes, creation/open categories, permission denial,")
    print("      UTC/UID/PID/paths, independent SHA-256, concurrency and log failures")


if __name__ == "__main__":
    main()
