CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -O2

.PHONY: all init-log clean
all: audit_logger.so audit_monitor test_audit
	@$(MAKE) --no-print-directory init-log

# Provision the shared log only during explicit build/setup, never in the logger.
init-log:
	@set -eu; \
	log=/tmp/access_audit.log; \
	tmp=; status=validated; \
	trap 'if [ -n "$$tmp" ]; then rm -f -- "$$tmp" || { echo "Audit log setup failed: cannot remove temporary file $$tmp" >&2; exit 1; }; fi' 0; \
	trap 'exit 1' 1 2 3 15; \
	if [ ! -e "$$log" ] && [ ! -L "$$log" ]; then \
		tmp=$$(mktemp /tmp/.access_audit.log.XXXXXXXXXX) || { echo "Audit log setup failed: mktemp" >&2; exit 1; }; \
		chmod 0666 "$$tmp" || { echo "Audit log setup failed: chmod $$tmp" >&2; exit 1; }; \
		if ln -T -- "$$tmp" "$$log" 2>/dev/null; then \
			status=created; \
		elif [ ! -e "$$log" ] && [ ! -L "$$log" ]; then \
			echo "Audit log setup failed: cannot create $$log with a hard link" >&2; exit 1; \
		fi; \
	fi; \
	if [ -L "$$log" ]; then \
		echo "Audit log setup failed: $$log is a symlink" >&2; exit 1; \
	fi; \
	if [ ! -f "$$log" ]; then \
		echo "Audit log setup failed: $$log is not a regular file" >&2; exit 1; \
	fi; \
	mode=$$(stat -c '%a' -- "$$log") || { echo "Audit log setup failed: cannot inspect $$log" >&2; exit 1; }; \
	if [ "$$mode" != 666 ]; then \
		echo "Audit log setup failed: $$log permissions must be 0666 (found $$mode)" >&2; exit 1; \
	fi; \
	if [ -n "$$tmp" ]; then \
		rm -f -- "$$tmp" || { echo "Audit log setup failed: cannot remove temporary file $$tmp" >&2; exit 1; }; \
		tmp=; \
	fi; \
	printf 'Audit log %s: %s\n' "$$status" "$$log"

audit_logger.so: audit_logger.c
	$(CC) $(CFLAGS) -fPIC -pthread -shared -o $@ $< -lcrypto -ldl

audit_monitor: audit_monitor.c
	$(CC) $(CFLAGS) -o $@ $<

test_audit: test_audit.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f audit_logger.so audit_monitor test_audit
