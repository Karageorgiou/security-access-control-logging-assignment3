CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -O2

# Keep the audit log setup in this Makefile so the submitted ZIP has six files.
define INIT_LOG_PY
import os
import stat
import sys

path = "/tmp/access_audit.log"
mode = 0o666
flags = os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC

try:
    try:
        fd = os.open(path, flags | os.O_CREAT | os.O_EXCL, mode)
        created = True
    except FileExistsError:
        fd = os.open(path, flags)
        created = False

    try:
        if created:
            os.fchmod(fd, mode)
        details = os.fstat(fd)
        if not stat.S_ISREG(details.st_mode):
            raise ValueError("audit log must be a regular file")
        if stat.S_IMODE(details.st_mode) != mode:
            raise ValueError("audit log permissions must be 0666 (found %04o)" % stat.S_IMODE(details.st_mode))
    finally:
        os.close(fd)
except (OSError, ValueError) as error:
    print("Audit log setup failed for %s: %s" % (path, error), file=sys.stderr)
    sys.exit(1)

print("Audit log %s: %s" % ("created" if created else "validated", path))
endef
export INIT_LOG_PY

.PHONY: all init-log clean
all: audit_logger.so audit_monitor test_audit
	@$(MAKE) --no-print-directory init-log

init-log:
	@python3 -c "$$INIT_LOG_PY"

audit_logger.so: audit_logger.c
	$(CC) $(CFLAGS) -fPIC -pthread -shared -o $@ $< -lcrypto -ldl

audit_monitor: audit_monitor.c
	$(CC) $(CFLAGS) -o $@ $<

test_audit: test_audit.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f audit_logger.so audit_monitor test_audit
