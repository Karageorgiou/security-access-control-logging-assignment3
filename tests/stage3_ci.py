#!/usr/bin/env python3
"""Assertion-based integration tests for the real Stage 3 audit_monitor."""

import errno
import hashlib
import os
import pathlib
import posixpath
import stat
import subprocess
import tempfile

from stage1_ci import LOG, LOGGER, ROOT

MONITOR = ROOT / "audit_monitor"
STREAM_PROBE = ROOT / "tests" / "stream_probe"
OPEN_PROBE = ROOT / "tests" / "fopen_probe"
DATE = "2026-11-17"
TIME = "12:00:00.000000000Z"
SAME_HASH = hashlib.sha256(b"same content").hexdigest()


def encode_field(value):
    encoded = []
    for byte in os.fsencode(value):
        if 0x21 <= byte <= 0x7E and byte != ord("%"):
            encoded.append(chr(byte))
        else:
            encoded.append(f"%{byte:02X}")
    return "".join(encoded)


def make_record(uid, filename, operation=1, outcome="failure", *, denied=False,
                size=0, requested=0, completed=0, prior="present", mode="r",
                digest=SAME_HASH):
    assert filename.startswith("/")
    prior = "absent" if operation == 0 else prior
    mode = "w" if operation == 0 else mode
    if operation < 2:
        mode_field = encode_field(mode)
        prior_field = prior
        creation = "1" if operation == 0 else "0"
    else:
        mode_field = prior_field = "-"
        creation = "0"
    number = str(errno.EACCES if denied else errno.EIO) if outcome == "failure" else "0"
    if operation == 2:
        size_fields = [str(size), str(requested), str(completed)]
    else:
        size_fields = ["-", "-", "-"]
    fields = [
        "v1", str(uid), "4242", encode_field(filename), DATE, TIME,
        str(operation), "1" if denied else "0", digest, outcome,
        mode_field, prior_field, creation, number,
        "unavailable" if digest == "N/A" else "post-close" if operation == 3 else "visible",
        *size_fields, encode_field(posixpath.normpath(filename)),
    ]
    assert len(fields) == 19
    return "\t".join(fields) + "\n"


def monitor(*args):
    env = os.environ.copy()
    env.pop("LD_PRELOAD", None)
    return subprocess.run([str(MONITOR), *map(str, args)], env=env,
                          capture_output=True, text=True, timeout=12)


def require_success(*args):
    result = monitor(*args)
    assert result.returncode == 0, (args, result)
    assert result.stderr == "", result
    return result.stdout


def set_records(lines):
    LOG.write_text("".join(lines), encoding="utf-8")
    LOG.chmod(0o666)


def check_cli_and_log_failures(work):
    for args in ((), ("-i",), ("-s", "extra"), ("-i", "a", "b"),
                 ("-x",), ("-i", ""), ("-s", "-i", "x")):
        response = monitor(*args)
        assert response.returncode == 2 and "Usage:" in response.stderr, (args, response)
    assert "Usage:" in require_success("-h")

    assert not LOG.exists()
    for flag in ("-s", "-i"):
        response = monitor(flag, "missing" if flag == "-i" else "") if flag == "-i" else monitor(flag)
        assert response.returncode == 1 and "cannot read a regular audit log" in response.stderr
    target = work / "safe.txt"
    target.write_text("safe", encoding="utf-8")
    LOG.symlink_to(target)
    assert monitor("-s").returncode == 1
    assert target.read_text(encoding="utf-8") == "safe"
    LOG.unlink()
    os.mkfifo(LOG)
    assert monitor("-s").returncode == 1
    LOG.unlink()
    LOG.mkdir()
    assert monitor("-s").returncode == 1
    LOG.rmdir()
    set_records([])
    LOG.chmod(0o000)
    assert monitor("-s").returncode == 1, "Unreadable log must fail for ordinary UID"
    LOG.chmod(0o666)


def check_suspicious_users():
    lines = []
    for index in range(5):
        lines.append(make_record(100, f"/tmp/a3-five/{index}", denied=True))
    lines.extend(make_record(100, "/tmp/a3-five/./0", denied=True) for _ in range(12))
    for index in range(6):
        lines.append(make_record(101, f"/tmp/a3-six/{index}", denied=True))
        lines.append(make_record(102, f"/tmp/a3-other-six/{index}", denied=True))
        lines.append(make_record(106, f"/tmp/a3-creation/{index}", operation=0, denied=True))
        lines.append(make_record(104, f"/tmp/a3-other-error/{index}", denied=False))
        lines.append(make_record(105, f"/tmp/a3-write-only/{index}", operation=2,
                                 denied=True, outcome="failure", size=1, requested=1))
    lines.extend(make_record(103, "/tmp/a3-duplicate/one", denied=True) for _ in range(7))
    lines.append(make_record(107, "/tmp/a3-success-not-denied", outcome="success"))
    set_records(lines)
    assert require_success("-s").splitlines() == [
        "UID 101: 6 distinct denied files",
        "UID 102: 6 distinct denied files",
        "UID 106: 6 distinct denied files",
    ]
    set_records([make_record(100, f"/tmp/a3-five/{index}", denied=True) for index in range(5)])
    assert require_success("-s") == "No suspicious users found.\n"


def check_file_activity():
    filename = "/tmp/a3-special %\tname"
    alias = "/tmp/a3-alias/../a3-special %\tname"
    records = [
        make_record(210, alias, outcome="success", mode="w+"),
        make_record(210, filename, operation=2, outcome="success",
                    size=1, requested=4, completed=4),
        make_record(210, filename, operation=2, outcome="success",
                    size=1, requested=4, completed=4),
        make_record(210, filename, operation=2, outcome="success",
                    size=0, requested=4, completed=0),
        make_record(210, filename, operation=2, outcome="success",
                    size=1, requested=0, completed=0),
        make_record(210, filename, operation=2, outcome="failure",
                    size=1, requested=5, completed=0),
        make_record(210, filename, operation=3, outcome="success"),
        make_record(211, filename, outcome="success"),
        make_record(211, filename, operation=2, outcome="partial",
                    size=2, requested=5, completed=2, digest="N/A"),
        make_record(212, filename, denied=True),
        make_record(213, filename, outcome="success"),
        make_record(214, filename, operation=3, outcome="success"),
        make_record(215, "/tmp/a3-other", operation=2, outcome="success",
                    size=1, requested=1, completed=1),
    ]
    set_records(records)
    assert require_success("-i", alias).splitlines() == [
        "File: " + filename,
        "UID 210: 2 modifications",
        "UID 211: 1 modifications",
        "UID 213: 0 modifications",
        "Total modifications: 3",
    ]
    assert require_success("-i", "/tmp/a3-absent").splitlines() == [
        "File: /tmp/a3-absent", "Total modifications: 0"]
    # A relative argument must resolve to the same lexical key as the producer.
    relative = os.path.relpath(filename, os.getcwd())
    assert require_success("-i", relative).splitlines() == require_success("-i", filename).splitlines()
    # Denied-only users must not be reported as successful access.
    assert "UID 212:" not in require_success("-i", filename)
    assert require_success("-s") == "No suspicious users found.\n"


def check_invalid_records():
    valid = make_record(800, "/tmp/valid", outcome="success")
    bad_variants = [
        valid.replace("v1\t", "v2\t", 1),
        valid.replace("\t", " ", 1),
        valid.replace("%", "%Q", 1) if "%" in valid else valid.replace("/tmp/valid", "%Q"),
        valid.replace("\t/tmp/valid\n", "\t/tmp/wrong\n"),
        valid.replace("\t1\t0\t", "\t3\t0\t", 1),
        make_record(800, "/tmp/valid", operation=2, outcome="success",
                    size=1, requested=3, completed=1),
        valid.rstrip("\n"),
        valid.replace("\tvisible\t", "\tunavailable\t"),
        valid.replace("\t4242\t", "\tbogus\t"),
        valid.replace("2026-11-17", "2026-99-17"),
        valid.rstrip("\n") + "\textra\tfield\n",
    ]
    for bad in bad_variants:
        # Put a legitimate record first to confirm no partial results are printed.
        set_records([valid, bad])
        response = monitor("-i", "/tmp/valid")
        assert response.returncode == 1, (bad, response)
        assert "invalid record on line 2" in response.stderr, (bad, response)
        assert response.stdout == "", (bad, response)
    set_records([])
    assert require_success("-s") == "No suspicious users found.\n"


def check_real_logger_end_to_end(work):
    set_records([])
    first = work / "end to end %\tfirst.txt"
    second = work / "second.txt"
    env = os.environ.copy()
    env["LD_PRELOAD"] = str(LOGGER)
    result = subprocess.run([str(STREAM_PROBE), "multi", str(first), str(second)],
                            env=env, capture_output=True, text=True, timeout=10)
    assert result.returncode == 0 and result.stderr == "", result
    user = os.getuid()
    assert require_success("-i", first).splitlines() == [
        "File: " + str(first), f"UID {user}: 2 modifications", "Total modifications: 2"]
    assert require_success("-i", second).splitlines() == [
        "File: " + str(second), f"UID {user}: 1 modifications", "Total modifications: 1"]
    assert require_success("-s") == "No suspicious users found.\n"

    denied = [work / f"denied-{index}.txt" for index in range(6)]
    for pathname in denied:
        pathname.write_text("private", encoding="utf-8")
        pathname.chmod(0o000)
        trial = subprocess.run([str(OPEN_PROBE), str(pathname), "r"], env=env,
                               capture_output=True, text=True, timeout=8)
        assert trial.returncode == 0 and "success=0" in trial.stdout, trial
    assert require_success("-s") == f"UID {user}: 6 distinct denied files\n"
    assert require_success("-i", denied[0]).splitlines() == [
        "File: " + str(denied[0]), "Total modifications: 0"]


def main():
    assert os.geteuid() != 0, "Tests must run as an ordinary user"
    assert MONITOR.is_file() and LOGGER.is_file() and STREAM_PROBE.is_file()
    assert not LOG.exists() and not LOG.is_symlink(), "Stage 3 requires an unused audit-log path"
    with tempfile.TemporaryDirectory(prefix="a3-stage3-") as temporary:
        work = pathlib.Path(temporary)
        try:
            check_cli_and_log_failures(work)
            check_suspicious_users()
            check_file_activity()
            check_invalid_records()
            check_real_logger_end_to_end(work)
        finally:
            if LOG.is_symlink() or LOG.is_file() or LOG.exists():
                LOG.unlink()
    print("PASS: monitor -s/-i, strict >5 distinct denied paths, UID isolation,")
    print("      successful-access membership, positive/partial/zero/failed write counts,")
    print("      lexical paths, escaped producer fields, invalid records/arguments/logs,")
    print("      and real LD_PRELOAD logger -> analyzer end-to-end assertions")


if __name__ == "__main__":
    main()
