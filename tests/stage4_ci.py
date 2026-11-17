#!/usr/bin/env python3
"""Assert the approved two-UID demonstration and exact six-file candidate ZIP."""

import concurrent.futures
import hashlib
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
from urllib.parse import unquote_to_bytes
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LOG = Path('/tmp/access_audit.log')
DATA_ROOT = Path('/tmp/security_a3_tests')
PACKAGE = '2015030123_2006030122_assign3'
USERS = ('a3ciuser1', 'a3ciuser2')
REQUIRED = ('README', 'Makefile', 'audit_logger.c', 'audit_logger.so',
            'audit_monitor.c', 'test_audit.c')


def Run(args, *, directory=None, expected=0, timeout=90):
    result = subprocess.run(args, cwd=directory, capture_output=True,
                            text=True, timeout=timeout)
    assert result.returncode == expected, (args, result)
    return result


def AsUser(user, args, directory):
    return Run(['runuser', '-u', user, '--', *args], directory=directory)


def UserId(user):
    return int(Run(['id', '-u', user]).stdout.strip())


def CreateUsers():
    created = []
    try:
        for user in USERS:
            # Refuse to borrow or delete an account that existed before this run.
            assert subprocess.run(['id', user], capture_output=True).returncode != 0, user
            Run(['useradd', '--no-create-home', '--shell', '/bin/bash', user])
            created.append(user)
        ids = {user: UserId(user) for user in USERS}
        assert len(set(ids.values())) == 2 and all(value != 0 for value in ids.values())
        for uid in ids.values():
            assert not (DATA_ROOT / f'a3_test_files_{uid}').exists(), 'Refusing existing UID test data'
        return created, ids
    except BaseException:
        for user in reversed(created):
            Run(['userdel', user])
        raise


def Decode(value):
    return os.fsdecode(unquote_to_bytes(value))


def Records():
    raw = LOG.read_bytes()
    assert raw and raw.endswith(b'\n') and b'\0' not in raw
    result = []
    for line in raw.decode('utf-8').splitlines():
        row = line.split('\t')
        assert len(row) == 19 and row[0] == 'v1', line
        assert row[1].isdigit() and row[2].isdigit()
        assert row[6] in ('0', '1', '2', '3') and row[7] in ('0', '1')
        assert row[9] in ('success', 'partial', 'failure')
        assert row[8] == 'N/A' or re.fullmatch('[0-9a-f]{64}', row[8])
        assert Decode(row[18]).startswith('/')
        result.append(row)
    return result


def ParseDemo(output, mode, uid):
    lines = output.splitlines()
    assert len(lines) == 21, lines
    for number in range(1, 16):
        writes = 2 * number if number <= 9 else (1 if number >= 13 else 0)
        assert lines[number - 1] == f'a3_test_file_{number:02d}: {writes} successful writes'
    fields = dict(line.split(': ', 1) for line in lines[15:])
    assert set(fields) == {'Mode', 'Run directory', 'Successful ordinary writes',
                           'Genuine denied attempts', 'Analyze file', 'Analyzer command'}
    assert fields['Mode'] == mode
    assert fields['Successful ordinary writes'] == '93'
    assert fields['Genuine denied attempts'] == ('4' if mode == 'normal' else '10')
    directory = Path(fields['Run directory'])
    assert directory.parent == DATA_ROOT / f'a3_test_files_{uid}'
    assert re.fullmatch(r'run_\d{2,}', directory.name)
    assert directory.is_dir() and directory.stat().st_uid == uid
    assert stat.S_IMODE(directory.stat().st_mode) == 0o700
    assert fields['Analyze file'] == str(directory / 'a3_test_file_09')
    assert fields['Analyzer command'] == f'./audit_monitor -i {directory / "a3_test_file_09"}'
    assert sorted(p.name for p in directory.iterdir()) == [
        f'a3_test_file_{n:02d}' for n in range(1, 16)]
    for n in range(1, 16):
        writes = 2 * n if n <= 9 else (1 if n >= 13 else 0)
        expected = ''.join(f'File {n:02d} - Write {i:02d}\n' for i in range(1, writes + 1))
        assert (directory / f'a3_test_file_{n:02d}').read_bytes() == expected.encode()
    return directory


def CheckResults(ids, directories, shared):
    rows = Records()
    assert {int(r[1]) for r in rows} == set(ids.values())
    suspicious = f'UID {ids[USERS[1]]}: 10 distinct denied files\n'
    for user in USERS:
        assert AsUser(user, ['./audit_monitor', '-s'], shared).stdout == suspicious
        for other in USERS:
            path = directories[other] / 'a3_test_file_09'
            expected = (f'File: {path}\nUID {ids[other]}: 18 modifications\n'
                        'Total modifications: 18\n')
            assert AsUser(user, ['./audit_monitor', '-i', str(path)], shared).stdout == expected

    for user in USERS:
        uid = ids[user]
        directory = directories[user]
        own = [r for r in rows if int(r[1]) == uid]
        expected_denials = 4 if user == USERS[0] else 10
        actual_denials = {Decode(r[18]) for r in own
                          if r[6] in ('0', '1') and r[7] == '1'}
        assert actual_denials == {str(directory / f'a3_protected_file_{n:02d}')
                                  for n in range(1, expected_denials + 1)}
        highlighted = str(directory / 'a3_test_file_09')
        example_rows = [r for r in own if Decode(r[18]) == highlighted]
        assert [r[6] for r in example_rows].count('0') == 1
        assert [r[6] for r in example_rows].count('1') == 1
        writes = [r for r in example_rows if r[6] == '2']
        assert len(writes) == 18
        assert all(r[9] == 'success' and int(r[15]) > 0 and
                   int(r[16]) > 0 and int(r[17]) > 0 for r in writes)
        closes = [r for r in example_rows if r[6] == '3']
        assert len(closes) == 2 and all(r[9] == 'success' for r in closes)
        digest = hashlib.sha256((directory / 'a3_test_file_09').read_bytes()).hexdigest()
        assert closes[-1][8] == digest
        assert sum(r[6] == '2' and Decode(r[18]).startswith(str(directory) + '/')
                   and '/a3_test_file_' in Decode(r[18]) for r in own) == 93
        assert sum(r[6] == '2' for r in own) == 93 + expected_denials

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(AsUser, user,
                    ['env', 'LD_PRELOAD=./audit_logger.so', './fopen_probe',
                     str(directories[user] / 'a3_test_file_09'), 'r'], shared)
                   for user in USERS for _ in range(8)]
        for future in futures:
            assert 'success=1' in future.result().stdout
    later = Records()
    assert len(later) == len(rows) + 32
    assert {int(r[1]) for r in later} == set(ids.values())


def CheckMissingLog(user, example, shared):
    LOG.unlink()
    arguments = ['./fopen_probe', str(example), 'r']
    plain = AsUser(user, arguments, shared)
    preloaded = AsUser(user, ['env', 'LD_PRELOAD=./audit_logger.so', *arguments], shared)
    pattern = r'success=([01]) errno=(\d+) pid=(\d+)\n'
    normal = re.fullmatch(pattern, plain.stdout)
    modified = re.fullmatch(pattern, preloaded.stdout)
    assert normal and modified and normal.groups()[:2] == modified.groups()[:2]
    assert normal.group(1) == '1'
    assert 'could not append' in preloaded.stderr
    assert not LOG.exists(), 'Logger must not recreate an unavailable audit log'


def Candidate():
    destination = ROOT / 'artifacts' / f'{PACKAGE}.zip'
    destination.parent.mkdir(exist_ok=True)
    assert (ROOT / 'audit_logger.so').read_bytes().startswith(b'\x7fELF')
    Run(['ldd', '-r', str(ROOT / 'audit_logger.so')])
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(PACKAGE + '/', '')
        for filename in REQUIRED:
            archive.write(ROOT / filename, arcname=f'{PACKAGE}/{filename}')
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None
        expected = {f'{PACKAGE}/'} | {f'{PACKAGE}/{name}' for name in REQUIRED}
        assert set(archive.namelist()) == expected
        assert len(archive.namelist()) == 7
        for filename in REQUIRED:
            assert archive.read(f'{PACKAGE}/{filename}') == (ROOT / filename).read_bytes()
        with tempfile.TemporaryDirectory(prefix='a3-professor-extract-') as temporary:
            archive.extractall(temporary)
            extracted = Path(temporary) / PACKAGE
            assert {p.name for p in extracted.iterdir()} == set(REQUIRED)
            Run(['make', 'clean', 'all'], directory=extracted)
            assert (extracted / 'audit_logger.so').read_bytes().startswith(b'\x7fELF')
            assert os.access(extracted / 'audit_monitor', os.X_OK)
            assert os.access(extracted / 'test_audit', os.X_OK)
    return destination


def SafeCleanupDirectories(ids):
    # Each UID directory was verified absent before these users were created.
    # Restrict cleanup to their new, owned, precisely named demonstration files.
    permitted = {f'a3_test_file_{n:02d}' for n in range(1, 16)} | {
        f'a3_protected_file_{n:02d}' for n in range(1, 11)}
    for uid in ids.values():
        parent = DATA_ROOT / f'a3_test_files_{uid}'
        if not parent.exists():
            continue
        status = parent.lstat()
        assert stat.S_ISDIR(status.st_mode) and status.st_uid == uid
        for directory in parent.iterdir():
            info = directory.lstat()
            assert re.fullmatch(r'run_\d{2,}', directory.name)
            assert stat.S_ISDIR(info.st_mode) and info.st_uid == uid
            for item in directory.iterdir():
                state = item.lstat()
                assert item.name in permitted
                assert stat.S_ISREG(state.st_mode) and state.st_uid == uid
                item.unlink()
            directory.rmdir()
        parent.rmdir()


def main():
    assert os.geteuid() == 0, 'Root required only in the CI script to set up two real ordinary UIDs'
    assert not LOG.exists() and not LOG.is_symlink(), 'Refusing pre-existing audit log'
    created = []
    ids = {}
    directories = {}
    log_identity = None
    try:
        created, ids = CreateUsers()
        with tempfile.TemporaryDirectory(prefix='a3-professor-shared-') as temporary:
            shared = Path(temporary)
            shared.chmod(0o755)
            for filename in ('test_audit', 'audit_monitor', 'audit_logger.so'):
                shutil.copyfile(ROOT / filename, shared / filename)
                (shared / filename).chmod(0o755)
            shutil.copyfile(ROOT / 'tests/fopen_probe', shared / 'fopen_probe')
            (shared / 'fopen_probe').chmod(0o755)
            descriptor = os.open(LOG, os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_WRONLY,
                                 0o666)
            try:
                os.fchmod(descriptor, 0o666)
                st = os.fstat(descriptor)
                log_identity = (st.st_dev, st.st_ino)
            finally:
                os.close(descriptor)
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                futures = {
                    USERS[0]: pool.submit(AsUser, USERS[0],
                        ['env', 'LD_PRELOAD=./audit_logger.so', './test_audit', '--normal'], shared),
                    USERS[1]: pool.submit(AsUser, USERS[1],
                        ['env', 'LD_PRELOAD=./audit_logger.so', './test_audit'], shared)
                }
                for user, future in futures.items():
                    mode = 'normal' if user == USERS[0] else 'default'
                    directories[user] = ParseDemo(future.result().stdout, mode, ids[user])
            CheckResults(ids, directories, shared)
            CheckMissingLog(USERS[0], directories[USERS[0]] / 'a3_test_file_09', shared)
        candidate = Candidate()
    finally:
        if log_identity is not None and (LOG.exists() or LOG.is_symlink()):
            st = LOG.lstat()
            assert stat.S_ISREG(st.st_mode) and (st.st_dev, st.st_ino) == log_identity
            LOG.unlink()
        try:
            if ids:
                SafeCleanupDirectories(ids)
        finally:
            for user in reversed(created):
                Run(['userdel', user])
    print('PASS: two distinct ordinary UIDs, normal/default scenarios, shared audit log,')
    print('      exact per-user denied/write counts, both users analyze both records,')
    print('      concurrent noninterleaved records, errno, six-file ZIP and extracted build')
    print(f'CANDIDATE_PACKAGE={candidate}')


if __name__ == '__main__':
    main()
