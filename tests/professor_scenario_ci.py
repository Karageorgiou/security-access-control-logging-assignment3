#!/usr/bin/env python3
"""Verify the human-approved professor demonstration using genuine logger records."""

import hashlib
import os
from pathlib import Path
import re
import stat
import subprocess
from urllib.parse import unquote_to_bytes

ROOT = Path(__file__).resolve().parents[1]
LOG = Path("/tmp/access_audit.log")
DIRECTORY = Path("/tmp/security_a3_tests")


def Run(args, *, expected=0):
    result = subprocess.run(args, cwd=ROOT, capture_output=True,
                            text=True, timeout=60)
    assert result.returncode == expected, (args, result)
    return result


def Decode(value):
    return os.fsdecode(unquote_to_bytes(value))


def ReadRecords():
    raw = LOG.read_bytes()
    assert raw and raw.endswith(b"\n") and b"\0" not in raw
    records = []
    for line in raw.decode("utf-8").splitlines():
        row = line.split("\t")
        assert len(row) == 19 and row[0] == "v1", line
        assert row[6] in ("0", "1", "2", "3") and row[7] in ("0", "1"), row
        assert row[9] in ("success", "partial", "failure"), row
        assert row[8] == "N/A" or re.fullmatch("[0-9a-f]{64}", row[8]), row
        assert Decode(row[18]).startswith("/"), row
        records.append(row)
    return records


def ProvisionLog():
    assert not LOG.exists() and not LOG.is_symlink(), "Refusing an existing audit log"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    fd = os.open(LOG, flags, 0o666)
    try:
        os.fchmod(fd, 0o666)
        status = os.fstat(fd)
    finally:
        os.close(fd)
    return (status.st_dev, status.st_ino)


def RemoveOwnedLog(identity):
    status = LOG.lstat()
    assert stat.S_ISREG(status.st_mode)
    assert (status.st_dev, status.st_ino) == identity
    LOG.unlink()


def ParseSummary(output, mode, uid):
    lines = output.splitlines()
    assert len(lines) == 21, lines
    expected_writes = [2 * n if n <= 9 else (1 if n >= 13 else 0)
                       for n in range(1, 16)]
    for number, writes in enumerate(expected_writes, 1):
        assert lines[number - 1] == (f"a3_test_file_{number:02d}: "
                                      f"{writes} successful writes"), lines
    fields = dict(line.split(": ", 1) for line in lines[15:])
    assert set(fields) == {
        "Mode", "Run directory", "Successful ordinary writes",
        "Genuine denied attempts", "Analyze file", "Analyzer command"
    }, fields
    assert fields["Mode"] == mode
    assert fields["Successful ordinary writes"] == "93"
    assert fields["Genuine denied attempts"] == ("4" if mode == "normal" else "10")
    directory = Path(fields["Run directory"])
    expected_base = DIRECTORY / f"a3_test_files_{uid}"
    assert directory.parent == expected_base
    assert re.fullmatch(r"run_\d{2,}", directory.name), directory
    assert directory.is_dir() and stat.S_IMODE(directory.stat().st_mode) == 0o700
    assert directory.stat().st_uid == uid
    assert stat.S_IMODE(expected_base.stat().st_mode) == 0o700
    assert expected_base.stat().st_uid == uid
    assert stat.S_IMODE(DIRECTORY.stat().st_mode) == 0o1777
    highlighted = directory / "a3_test_file_09"
    assert fields["Analyze file"] == str(highlighted)
    assert fields["Analyzer command"] == f"./audit_monitor -i {highlighted}"
    assert sorted(p.name for p in directory.iterdir()) == [
        f"a3_test_file_{n:02d}" for n in range(1, 16)]
    for number, writes in enumerate(expected_writes, 1):
        name = directory / f"a3_test_file_{number:02d}"
        expected = "".join(f"File {number:02d} - Write {index:02d}\n"
                           for index in range(1, writes + 1))
        assert name.read_bytes() == expected.encode(), (name, name.read_bytes())
    return directory


def CheckAudit(directory, uid, denied_count):
    records = ReadRecords()
    assert {int(r[1]) for r in records} == {uid}
    for number in range(1, 16):
        name = str(directory / f"a3_test_file_{number:02d}")
        own = [r for r in records if Decode(r[18]) == name]
        writes = 2 * number if number <= 9 else (1 if number >= 13 else 0)
        creation = [r for r in own if r[6] == "0"]
        openings = [r for r in own if r[6] == "1"]
        modifications = [r for r in own if r[6] == "2"]
        closes = [r for r in own if r[6] == "3"]
        assert len(creation) == 1 and creation[0][9] == "success", (name, own)
        assert len(modifications) == writes, (name, own)
        assert all(r[9] == "success" and int(r[15]) > 0 and
                   int(r[16]) > 0 and int(r[17]) > 0 for r in modifications)
        expected_openings = writes if number <= 9 and number % 2 == 0 else 1
        assert len(openings) == expected_openings, (name, own)
        assert all(r[7] == "0" and r[9] == "success" for r in openings)
        assert len(closes) == expected_openings + 1, (name, own)
        assert all(r[9] == "success" for r in closes)
        digest = hashlib.sha256(Path(name).read_bytes()).hexdigest()
        assert closes[-1][8] == digest, (name, closes[-1][8], digest)
    denied = {Decode(r[18]) for r in records if r[6] in ("0", "1") and r[7] == "1"}
    assert denied == {str(directory / f"a3_protected_file_{n:02d}")
                      for n in range(1, denied_count + 1)}, denied
    for number in range(1, denied_count + 1):
        name = str(directory / f"a3_protected_file_{number:02d}")
        own = [r for r in records if Decode(r[18]) == name]
        assert [r[6] for r in own] == ["0", "2", "3", "1"], (name, own)
        assert own[-1][7] == "1" and own[-1][9] == "failure"
        assert own[1][9] == "success" and int(own[1][17]) > 0
        assert not Path(name).exists()
    for record in records:
        assert len(record) == 19
    return records


def CheckAnalyzer(directory, uid, suspicious_count):
    result = Run(["./audit_monitor", "-s"])
    expected = (f"UID {uid}: {suspicious_count} distinct denied files\n"
                if suspicious_count > 5 else "No suspicious users found.\n")
    assert result.stdout == expected, (result.stdout, expected)
    target = directory / "a3_test_file_09"
    result = Run(["./audit_monitor", "-i", str(target)])
    assert result.stdout == (f"File: {target}\n"
                             f"UID {uid}: 18 modifications\n"
                             "Total modifications: 18\n"), result.stdout


def main():
    assert os.geteuid() != 0, "Real denial tests require a non-root UID"
    assert not LOG.exists() and not LOG.is_symlink(), "Refusing an existing log"
    uid = os.geteuid()
    baseline_runs = (set((DIRECTORY / f"a3_test_files_{uid}").glob("run_*"))
                     if (DIRECTORY / f"a3_test_files_{uid}").is_dir() else set())
    identity = ProvisionLog()
    try:
        result = Run(["env", "LD_PRELOAD=./audit_logger.so", "./test_audit", "--normal"])
        first = ParseSummary(result.stdout, "normal", uid)
        assert first not in baseline_runs
        CheckAudit(first, uid, 4)
        CheckAnalyzer(first, uid, 4)
        invalid = Run(["./test_audit", "--invalid"], expected=1)
        assert "Usage:" in invalid.stderr
        assert first.is_dir(), "Invalid arguments must not delete a prior run"
        RemoveOwnedLog(identity)
        identity = ProvisionLog()
        result = Run(["env", "LD_PRELOAD=./audit_logger.so", "./test_audit"])
        second = ParseSummary(result.stdout, "default", uid)
        assert second != first and int(second.name[4:]) > int(first.name[4:])
        assert first.is_dir() and first not in baseline_runs
        CheckAudit(second, uid, 10)
        CheckAnalyzer(second, uid, 10)
    finally:
        if LOG.exists() or LOG.is_symlink():
            RemoveOwnedLog(identity)
    print("PASS: professor scenario both modes, 15 exclusive files, 93 actual writes,")
    print("      4/10 genuine denials, exact contents, safe run numbering, SHA-256,")
    print("      fopen/fwrite/fclose evidence, and real audit_monitor -s/-i output")


if __name__ == "__main__":
    main()
