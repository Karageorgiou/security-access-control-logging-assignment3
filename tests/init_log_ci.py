#!/usr/bin/env python3
"""Verify Makefile log provisioning using only a CI-created audit-log fixture."""

import os
import concurrent.futures
import glob
from pathlib import Path
import stat
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LOG = Path('/tmp/access_audit.log')
DEMO_DIRECTORY = Path('/tmp/security_a3_tests')
BINARIES = ('audit_logger.so', 'audit_monitor', 'test_audit')
TEMP_PATTERN = '/tmp/.access_audit.log.*'
owned = {}


def Run(*args, success=True, env=None):
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True,
                            timeout=45, env=env)
    if success:
        assert result.returncode == 0, (args, result.stdout, result.stderr)
    else:
        assert result.returncode != 0, (args, result.stdout, result.stderr)
        assert 'Audit log setup failed' in result.stderr, result.stderr
    assert 'DEMO_DIR=' not in result.stdout, result.stdout
    return result


def Remember():
    details = LOG.lstat()
    owned[(details.st_dev, details.st_ino)] = stat.S_IFMT(details.st_mode)
    return details


def RemoveOwned():
    if not os.path.lexists(LOG):
        return
    details = LOG.lstat()
    identity = (details.st_dev, details.st_ino)
    assert identity in owned, 'Refusing to remove an unrecognized audit-log path'
    assert owned[identity] == stat.S_IFMT(details.st_mode), 'Audit-log fixture type changed'
    if stat.S_ISDIR(details.st_mode):
        LOG.rmdir()
    else:
        LOG.unlink()
    del owned[identity]


def Snapshot():
    details = LOG.lstat()
    assert stat.S_ISREG(details.st_mode)
    return (details.st_dev, details.st_ino, details.st_uid, details.st_gid,
            details.st_mode, details.st_nlink, details.st_size,
            details.st_mtime_ns, details.st_ctime_ns, LOG.read_bytes())


def TempNames():
    return set(glob.glob(TEMP_PATTERN))


def AssertNoTemporaryFiles(before):
    assert TempNames() == before, 'Temporary log files leaked from init-log'


def TestInitialization():
    assert not os.path.lexists(LOG), 'Refusing to touch a pre-existing audit log'
    demo_before = (tuple(sorted(os.listdir(DEMO_DIRECTORY)))
                   if DEMO_DIRECTORY.is_dir() else None)
    dry_run = Run('make', '-n', 'all').stdout
    assert '\n./test_audit' not in dry_run and '\n./audit_monitor' not in dry_run

    temporary_before = TempNames()
    result = Run('make', 'clean', 'all')
    AssertNoTemporaryFiles(temporary_before)
    assert 'Audit log created:' in result.stdout, result.stdout
    for filename in BINARIES:
        assert (ROOT / filename).is_file(), filename
    created = Remember()
    assert stat.S_ISREG(created.st_mode)
    assert stat.S_IMODE(created.st_mode) == 0o666
    assert created.st_uid == os.geteuid()
    assert created.st_size == 0
    demo_after = (tuple(sorted(os.listdir(DEMO_DIRECTORY)))
                  if DEMO_DIRECTORY.is_dir() else None)
    assert demo_after == demo_before, 'Build unexpectedly changed demonstration data'

    marker = b'pre-existing audit record\nsecond preserved record\n'
    descriptor = os.open(LOG, os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW)
    try:
        assert os.write(descriptor, marker) == len(marker)
    finally:
        os.close(descriptor)
    before = Snapshot()

    result = Run('make', 'init-log')
    AssertNoTemporaryFiles(temporary_before)
    assert 'Audit log validated:' in result.stdout
    assert Snapshot() == before, 'init-log modified an existing valid audit log'

    result = Run('make', 'all')
    AssertNoTemporaryFiles(temporary_before)
    assert 'Audit log validated:' in result.stdout
    assert Snapshot() == before, 'make all modified an existing valid audit log'
    demo_after = (tuple(sorted(os.listdir(DEMO_DIRECTORY)))
                  if DEMO_DIRECTORY.is_dir() else None)
    assert demo_after == demo_before, 'make all changed demonstration data'

    Run('make', 'clean')
    assert all(not (ROOT / file).exists() for file in BINARIES)
    assert Snapshot() == before, 'make clean modified the audit log'
    Run('make', 'init-log')
    assert all(not (ROOT / file).exists() for file in BINARIES)
    assert Snapshot() == before, 'init-log depended on a compiled binary'
    RemoveOwned()


def TestUnsafeTargets():
    with tempfile.TemporaryDirectory(prefix='a3-make-log-target-') as workspace:
        target = Path(workspace) / 'unrelated.txt'
        target.write_bytes(b'Do not change this target\n')
        LOG.symlink_to(target)
        Remember()
        Run('make', 'init-log', success=False)
        assert LOG.is_symlink() and target.read_bytes() == b'Do not change this target\n'
        RemoveOwned()

        os.mkfifo(LOG, 0o600)
        Remember()
        Run('make', 'init-log', success=False)
        assert stat.S_ISFIFO(LOG.lstat().st_mode)
        RemoveOwned()

        LOG.mkdir(mode=0o700)
        Remember()
        Run('make', 'init-log', success=False)
        assert LOG.is_dir()
        RemoveOwned()

    descriptor = os.open(LOG, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600)
    try:
        os.write(descriptor, b'preserve permissions and contents\n')
    finally:
        os.close(descriptor)
    Remember()
    original = Snapshot()
    Run('make', 'init-log', success=False)
    assert Snapshot() == original

    LOG.chmod(0o444)
    readonly = Snapshot()
    Run('make', 'init-log', success=False)
    assert Snapshot() == readonly

    LOG.chmod(0o666)
    valid = Snapshot()
    Run('make', 'init-log')
    assert Snapshot() == valid
    RemoveOwned()


def TestConcurrentInitialization():
    assert not os.path.lexists(LOG), 'Refusing to replace an existing audit log'
    before = TempNames()
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(lambda _: Run('make', 'init-log'), range(24)))
    assert sum('Audit log created:' in result.stdout for result in results) == 1, results
    assert sum('Audit log validated:' in result.stdout for result in results) == 23, results
    AssertNoTemporaryFiles(before)
    state = Remember()
    assert stat.S_ISREG(state.st_mode)
    assert stat.S_IMODE(state.st_mode) == 0o666 and state.st_size == 0
    marker = b'original records remain untouched\n'
    LOG.write_bytes(marker)
    snapshot = Snapshot()
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        results = list(pool.map(lambda _: Run('make', 'init-log'), range(24)))
    assert all('Audit log validated:' in result.stdout for result in results)
    assert Snapshot() == snapshot
    AssertNoTemporaryFiles(before)
    RemoveOwned()


def TestTemporaryCleanupOnFailure():
    assert not os.path.lexists(LOG), 'Refusing an existing audit log'
    before = TempNames()
    with tempfile.TemporaryDirectory(prefix='a3-make-command-failure-') as workspace:
        for command in ('ln', 'chmod'):
            stub = Path(workspace) / command
            stub.write_text('#!/bin/sh\nexit 1\n', encoding='utf-8')
            stub.chmod(0o755)
            env = os.environ.copy()
            env['PATH'] = workspace + os.pathsep + os.environ['PATH']
            result = Run('make', 'init-log', success=False, env=env)
            assert 'Audit log setup failed' in result.stderr
            assert not os.path.lexists(LOG), 'Failed creation unexpectedly installed a log'
            AssertNoTemporaryFiles(before)
            stub.unlink()


def main():
    assert os.geteuid() != 0, 'Provisioning must also work as an ordinary user'
    assert not os.path.lexists(LOG), 'Refusing an existing audit log'
    try:
        TestInitialization()
        TestUnsafeTargets()
        TestConcurrentInitialization()
        TestTemporaryCleanupOnFailure()
        assert not os.path.lexists(LOG)
    finally:
        if os.path.lexists(LOG):
            RemoveOwned()
    print('PASS: make all builds three binaries and safely creates 0666 log')
    print('PASS: independent init-log and repeated setup preserve records and metadata')
    print('PASS: symlink, FIFO, directory and unsuitable modes rejected without changes')
    print('PASS: concurrent setup preserves one log identity and leaves no temporary files')
    print('PASS: failed ln/chmod cleanup removes temporary files')
    print('PASS: make clean leaves log unchanged; no demo or analyzer execution')


if __name__ == '__main__':
    main()
