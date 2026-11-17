CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -O2

.PHONY: all clean
all: audit_logger.so audit_monitor test_audit

audit_logger.so: audit_logger.c
	$(CC) $(CFLAGS) -fPIC -pthread -shared -o $@ $< -lcrypto -ldl

audit_monitor: audit_monitor.c
	$(CC) $(CFLAGS) -o $@ $<

test_audit: test_audit.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f audit_logger.so audit_monitor test_audit
