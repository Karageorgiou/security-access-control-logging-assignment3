#!/usr/bin/env python3
"""Assert the real professor demo, two ordinary UIDs and exact six-file ZIP."""

import concurrent.futures
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import unquote_to_bytes
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LOG = Path("/tmp/access_audit.log")
PACKAGE = "2015030123_2006030122_assign3"
USERS = ("a3ciuser1", "a3ciuser2")
REQUIRED = (
    "README", "Makefile", "audit_logger.c", "audit_logger.so",
    "audit_monitor.c", "test_audit.c",
)


def Run(command, *, directory=None, expected=0, timeout=35):
    result = subprocess.run(command, cwd=directory, capture_output=True,
                            text=True, timeout=timeout)
    assert result.returncode == expected, (command, result)
    return result


def AsUser(username, command, directory):
    return Run(["runuser", "-u", username, "--", *command], directory=directory)


def UserId(username):
    return int(Run(["id", "-u", username]).stdout.strip())


def ParseDemo(output):
    fields = {}
    for line in output.splitlines():
        assert "=" in line, output
        name, value = line.split("=", 1)
        assert name not in fields, output
        fields[name] = value
    assert set(fields) == {
        "DEMO_DIR", "ANALYZE_FILE", "EXPECTED_MODIFICATIONS",
        "EXPECTED_DISTINCT_DENIALS",
    }, fields
    directory = fields["DEMO_DIR"]
    assert re.fullmatch(r"/tmp/a3-assignment-[A-Za-z0-9]{6}", directory), fields
    assert fields["ANALYZE_FILE"] == directory + "/example.txt"
    assert fields["EXPECTED_MODIFICATIONS"] == "3"
    assert fields["EXPECTED_DISTINCT_DENIALS"] == "6"
    example = Path(fields["ANALYZE_FILE"])
    assert example.is_file() and example.read_bytes() == b"changed line\nappended line\n"
    assert (Path(directory) / "notes.txt").read_bytes() == b"notes\n"
    assert (Path(directory) / "activity.txt").read_bytes() == b"activity\nlater\n"
    assert not any(Path(directory).glob("denied_*.txt"))
    return example


def DecodeField(value):
    return os.fsdecode(unquote_to_bytes(value))


def ReadRecords():
    raw = LOG.read_bytes()
    assert raw and raw.endswith(b"\n"), "Missing or incomplete audit records"
    assert b"\x00" not in raw
    records = []
    for row in raw.decode("utf-8").splitlines():
        fields = row.split("\t")
        assert len(fields) == 19 and fields[0] == "v1", row
        assert fields[1].isdigit() and fields[2].isdigit(), row
        assert fields[6] in ("0", "1", "2", "3"), row
        assert fields[7] in ("0", "1"), row
        assert fields[9] in ("success", "partial", "failure"), row
        assert fields[8] == "N/A" or re.fullmatch("[0-9a-f]{64}", fields[8]), row
        assert DecodeField(fields[18]).startswith("/"), row
        records.append(fields)
    return records


def CheckResults(user_ids, examples, shared):
    rows = ReadRecords()
    assert len(rows) >= 90, f"Too few records: {len(rows)}"

    expected_suspicious = {
        f"UID {uid}: 6 distinct denied files" for uid in user_ids.values()
    }
    for username in USERS:
        output = AsUser(username, ["./audit_monitor", "-s"], shared).stdout
        assert set(output.splitlines()) == expected_suspicious, output
        for other in USERS:
            filename = examples[other]
            target_uid = user_ids[other]
            expected = (f"File: {filename}\n"
                        f"UID {target_uid}: 3 modifications\n"
                        "Total modifications: 3\n")
            found = AsUser(username, ["./audit_monitor", "-i", str(filename)],
                           shared).stdout
            assert found == expected, (username, other, found)

    for username in USERS:
        uid = str(user_ids[username])
        filename = str(examples[username])
        own = [row for row in rows if row[1] == uid]
        denied = {DecodeField(row[18]) for row in own
                  if row[6] in ("0", "1") and row[7] == "1"}
        assert len(denied) == 6 and all("/denied_" in p for p in denied), denied
        example_rows = [row for row in own if DecodeField(row[18]) == filename]
        assert any(row[6] == "0" and row[9] == "success" for row in example_rows)
        assert any(row[6] == "1" and row[9] == "success" for row in example_rows)
        writes = [row for row in example_rows if row[6] == "2"]
        assert len(writes) == 3 and all(row[9] == "success" and
                    int(row[15]) > 0 and int(row[16]) > 0 and
                    int(row[17]) > 0 for row in writes), writes
        closes = [row for row in example_rows if row[6] == "3"]
        assert len(closes) >= 3 and all(row[9] == "success" for row in closes)
        actual_hash = hashlib.sha256(examples[username].read_bytes()).hexdigest()
        assert closes[-1][8] == actual_hash, (closes[-1][8], actual_hash)
        # Both UIDs must genuinely emit records, not just execute the same binary.
        assert len(own) >= 45

    # Additional operations from both accounts must still form complete records.
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        futures = []
        for username in USERS:
            for _ in range(8):
                futures.append(pool.submit(AsUser, username,
                    ["env", "LD_PRELOAD=./audit_logger.so", "./fopen_probe",
                     str(examples[username]), "r"], shared))
        for future in futures:
            response = future.result()
            assert "success=1" in response.stdout, response
    second_rows = ReadRecords()
    assert len(second_rows) == len(rows) + 32, (len(second_rows), len(rows))
    assert {int(row[1]) for row in second_rows} == set(user_ids.values())


def CheckUnloggedLibcBehavior(username, example, shared):
    LOG.unlink()
    args = ["./fopen_probe", str(example), "r"]
    normal = AsUser(username, args, shared)
    audited = AsUser(username, ["env", "LD_PRELOAD=./audit_logger.so", *args],
                     shared)
    pattern = r"success=([01]) errno=(\d+) pid=(\d+)\n"
    baseline = re.fullmatch(pattern, normal.stdout)
    modified = re.fullmatch(pattern, audited.stdout)
    assert baseline and modified
    assert baseline.groups()[:2] == modified.groups()[:2], (normal, audited)
    assert baseline.group(1) == "1"
    assert "could not append" in audited.stderr
    assert not LOG.exists(), "Logger must not recreate an unavailable audit log"


def BuildCandidate():
    destination = ROOT / "artifacts" / f"{PACKAGE}.zip"
    destination.parent.mkdir(exist_ok=True)
    assert (ROOT / "audit_logger.so").read_bytes().startswith(b"\x7fELF")
    Run(["ldd", "-r", str(ROOT / "audit_logger.so")])

    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(PACKAGE + "/", "")
        for filename in REQUIRED:
            archive.write(ROOT / filename, arcname=f"{PACKAGE}/{filename}")
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None
        expected = {f"{PACKAGE}/"} | {f"{PACKAGE}/{name}" for name in REQUIRED}
        assert set(archive.namelist()) == expected, archive.namelist()
        assert len(archive.namelist()) == len(expected), "Duplicate archive entries"
        assert archive.read(f"{PACKAGE}/audit_logger.so").startswith(b"\x7fELF")
        for name in REQUIRED:
            original = (ROOT / name).read_bytes()
            assert archive.read(f"{PACKAGE}/{name}") == original
        with tempfile.TemporaryDirectory(prefix="a3-stage4-extract-") as directory:
            archive.extractall(directory)
            extracted = Path(directory) / PACKAGE
            assert {p.name for p in extracted.iterdir()} == set(REQUIRED)
            assert set(p.name for p in extracted.iterdir() if p.is_file()) == set(REQUIRED)
            Run(["make", "clean", "all"], directory=extracted, timeout=60)
            assert (extracted / "audit_logger.so").read_bytes().startswith(b"\x7fELF")
            Run(["ldd", "-r", str(extracted / "audit_logger.so")])
            assert os.access(extracted / "audit_monitor", os.X_OK)
            assert os.access(extracted / "test_audit", os.X_OK)
    return destination


def main():
    assert os.geteuid() == 0, "This test needs root only to switch to two ordinary UIDs"
    user_ids = {name: UserId(name) for name in USERS}
    assert len(set(user_ids.values())) == 2 and all(uid != 0 for uid in user_ids.values())
    assert not LOG.exists() and not LOG.is_symlink(), "Use an unused audit-log path"

    with tempfile.TemporaryDirectory(prefix="a3-stage4-share-") as temporary:
        shared = Path(temporary)
        shared.chmod(0o755)
        for name in ("test_audit", "audit_monitor", "audit_logger.so"):
            shutil.copyfile(ROOT / name, shared / name)
            (shared / name).chmod(0o755)
        shutil.copyfile(ROOT / "tests" / "fopen_probe", shared / "fopen_probe")
        (shared / "fopen_probe").chmod(0o755)

        descriptor = os.open(LOG, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o666)
        try:
            os.fchmod(descriptor, 0o666)
        finally:
            os.close(descriptor)
        assert LOG.stat().st_mode & 0o777 == 0o666

        examples = {}
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                futures = {name: pool.submit(AsUser, name,
                    ["env", "LD_PRELOAD=./audit_logger.so", "./test_audit"], shared)
                    for name in USERS}
                for name, future in futures.items():
                    examples[name] = ParseDemo(future.result().stdout)
            assert examples[USERS[0]] != examples[USERS[1]]
            CheckResults(user_ids, examples, shared)
            CheckUnloggedLibcBehavior(USERS[0], examples[USERS[0]], shared)
        finally:
            if LOG.is_file() or LOG.is_symlink():
                LOG.unlink()
            # Only paths returned by this exact demo are cleaned; never use wildcards.
            for name, example in examples.items():
                directory = example.parent
                if re.fullmatch(r"/tmp/a3-assignment-[A-Za-z0-9]{6}", str(directory)):
                    for filename in ("example.txt", "notes.txt", "activity.txt"):
                        subprocess.run(["runuser", "-u", name, "--", "rm", "-f",
                                        str(directory / filename)], check=True)
                    subprocess.run(["runuser", "-u", name, "--", "rmdir",
                                    str(directory)], check=True)

    candidate = BuildCandidate()
    print("PASS: genuine two-UID concurrent fopen/fwrite/fclose, six real denials each,")
    print("      both UIDs append/read the shared log, -s/-i, genuine hashes, errno,")
    print("      complete noninterleaved records, no-log behavior, six-file ZIP and rebuild")
    print(f"CANDIDATE_PACKAGE={candidate}")


if __name__ == "__main__":
    main()
