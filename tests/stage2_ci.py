#!/usr/bin/env python3
"""Real-process regression assertions for fwrite/fclose and stream attribution."""

import concurrent.futures
import hashlib
import os
import pathlib
import re
import stat
import subprocess
import tempfile

from stage1_ci import LOG, LOGGER, ROOT, read_records

PROBE = ROOT / "tests" / "stream_probe"


def run_probe(action, *paths, preload=True):
    env = os.environ.copy()
    env.pop("LD_PRELOAD", None)
    if preload:
        env["LD_PRELOAD"] = str(LOGGER)
    result = subprocess.run([str(PROBE), action, *map(str, paths)], env=env,
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, (action, result)
    pid = re.search(r"^pid=(\d+)$", result.stdout, flags=re.MULTILINE)
    assert pid, result.stdout
    return int(pid.group(1)), result.stdout, result.stderr


def for_pid(pid):
    return [line for line in read_records() if int(line[2]) == pid]


def event(records, operation, path):
    matches = [line for line in records if line[6] == str(operation) and line[3] == str(path)]
    assert len(matches) == 1, (operation, path, records)
    return matches[0]


def compare_with_normal(action, *paths, diagnostic=None):
    normal = run_probe(action, *paths, preload=False)
    if action in ("basic", "reassociate", "reuse"):
        for path in paths:
            pathlib.Path(path).unlink()
    logged = run_probe(action, *paths)
    # Compare every completed count, return code and errno without comparing PIDs.
    assert normal[1].split("pid=")[0] == logged[1].split("pid=")[0], (normal, logged)
    if diagnostic:
        assert diagnostic in logged[2], logged[2]
    return logged


def main():
    assert os.geteuid() != 0, "Tests must run as an ordinary UID"
    assert LOGGER.is_file() and PROBE.is_file()
    assert not LOG.exists() and not LOG.is_symlink()
    fd = os.open(LOG, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o666)
    os.close(fd)
    LOG.chmod(0o666)
    try:
        assert stat.S_ISREG(LOG.stat().st_mode)
        with tempfile.TemporaryDirectory(prefix="a3-stage2-") as directory:
            work = pathlib.Path(directory)
            single = work / "basic.txt"
            pid, output, stderr = compare_with_normal("basic", single)
            assert "write=5" in output and stderr == "", (output, stderr)
            events = for_pid(pid)
            assert [int(e[6]) for e in events] == [0, 2, 3], events
            assert event(events, 2, single)[15:18] == ["1", "5", "5"]
            assert event(events, 2, single)[9] == "success"
            assert event(events, 3, single)[14] == "post-close"
            assert event(events, 3, single)[8] == hashlib.sha256(b"hello").hexdigest()
            assert single.read_bytes() == b"hello"

            first, second = work / "first.txt", work / "second.txt"
            pid, stdout, stderr = run_probe("multi", first, second)
            assert stderr == "", stderr
            records = for_pid(pid)
            writes = [e for e in records if e[6] == "2"]
            assert [e[3] for e in writes] == [str(first), str(first), str(second), str(first)]
            assert [e[15:18] for e in writes] == [
                ["1", "5", "5"], ["0", "5", "0"], ["1", "4", "4"], ["1", "5", "5"]]
            assert all(e[9] == "success" for e in writes)
            assert sum(e[15] != "0" and e[16] != "0" and int(e[17]) > 0 for e in writes) == 3
            # These digest observations occur before fclose, without a forced flush.
            assert all(e[8] == hashlib.sha256(b"").hexdigest() for e in writes), writes
            assert [e[3] for e in records if e[6] == "3"] == [str(second), str(first)]
            assert event(records, 3, first)[8] == hashlib.sha256(b"alphaalpha").hexdigest()
            assert event(records, 3, second)[8] == hashlib.sha256(b"beta").hexdigest()
            assert first.read_bytes() == b"alphaalpha" and second.read_bytes() == b"beta"

            orphan = work / "fdopen.txt"
            pid, stdout, stderr = compare_with_normal("unregistered", orphan,
                                                       diagnostic="stream identity unavailable")
            assert orphan.read_bytes() == b"orphan"
            assert for_pid(pid) == [], for_pid(pid)
            assert stderr.count("stream identity unavailable") == 1, stderr

            old, new = work / "old.txt", work / "new.txt"
            pid, stdout, stderr = compare_with_normal("reassociate", old, new,
                                                       diagnostic="stream identity unavailable")
            assert new.read_bytes() == b"newfile"
            assert [(e[6], e[3]) for e in for_pid(pid)] == [("0", str(old))]
            assert stderr.count("stream identity unavailable") == 1, stderr

            reuse_old, reuse_new = work / "reuse_old.txt", work / "reuse_new.txt"
            pid, _, stderr = compare_with_normal("reuse", reuse_old, reuse_new)
            assert stderr == "", stderr
            assert [(e[6], e[3]) for e in for_pid(pid)] == [
                ("0", str(reuse_old)), ("3", str(reuse_old)),
                ("0", str(reuse_new)), ("2", str(reuse_new)), ("3", str(reuse_new))]

            pid, stdout, stderr = compare_with_normal("failed-write", "unused")
            events = for_pid(pid)
            write = event(events, 2, "/dev/full")
            assert re.search(r"write=0 errno=28", stdout), stdout
            assert write[15:18] == ["1", "5", "0"] and write[9] == "failure", write
            assert write[8] == "N/A" and write[14] == "unavailable"

            pid, stdout, stderr = compare_with_normal("failed-close", "unused")
            assert re.search(r"close=-1 errno=28", stdout), stdout
            assert event(for_pid(pid), 3, "/dev/full")[9] == "failure"
            assert event(for_pid(pid), 3, "/dev/full")[14] == "unavailable"

            pid, stdout, stderr = run_probe("stdout", "unused")
            assert "stream identity unavailable" in stderr, stderr
            assert for_pid(pid) == []

            # Independent application processes share the same flock-protected log.
            paths = [work / f"parallel-{i}.txt" for i in range(16)]
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(lambda p: run_probe("basic", p), paths))
            for path, result in zip(paths, results):
                pid, _, stderr = result
                assert stderr == "", stderr
                assert [(e[6], e[3]) for e in for_pid(pid)] == [
                    ("0", str(path)), ("2", str(path)), ("3", str(path))]
            assert all(len(line.split("\t")) == 19 for line in LOG.read_text().splitlines())

            # Persistence errors cannot alter the real fwrite/fclose results or errno.
            LOG.unlink()
            compare_with_normal("basic", work / "no-log.txt",
                                diagnostic="could not append")
            compare_with_normal("failed-write", "unused",
                                diagnostic="could not append")
            compare_with_normal("failed-close", "unused",
                                diagnostic="could not append")
            assert not LOG.exists()

            destination = work / "untouched"
            destination.write_bytes(b"sentinel")
            LOG.symlink_to(destination)
            compare_with_normal("basic", work / "symlink.txt",
                                diagnostic="could not append")
            assert destination.read_bytes() == b"sentinel"
            LOG.unlink()

            os.mkfifo(LOG)
            compare_with_normal("basic", work / "fifo.txt",
                                diagnostic="could not append")
            LOG.unlink()

            LOG.write_bytes(b"")
            LOG.chmod(0o444)
            compare_with_normal("basic", work / "no-write-perm.txt",
                                diagnostic="could not append")
            LOG.chmod(0o666)
    finally:
        if LOG.is_symlink() or LOG.exists():
            LOG.unlink()

    print("PASS: three hooks, open regressions, cross-stream tracking, multiple/zero writes,")
    print("      failed write/close, stale/unregistered diagnostics, genuine buffered hashes,")
    print("      stream reuse, concurrent records, libc errno and log failure preservation")


if __name__ == "__main__":
    main()
