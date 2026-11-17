CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -O2 -fPIC -pthread
LDLIBS = -lcrypto -ldl

.PHONY: all clean
all: audit_logger.so audit_monitor

audit_logger.so: audit_logger.c
	$(CC) $(CFLAGS) -shared -o $@ $< $(LDLIBS)

audit_monitor: audit_monitor.c
	$(CC) -Wall -Wextra -std=c11 -O2 -o $@ $<

clean:
	rm -f audit_logger.so audit_monitor
