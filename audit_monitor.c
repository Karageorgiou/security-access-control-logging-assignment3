#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <unistd.h>

#define AUDIT_LOG_PATH "/tmp/access_audit.log"
#define FIELD_COUNT 19

typedef struct
{
    unsigned long uid;
    int operation;
    int denied;
    int successful_open;
    size_t size;
    size_t requested;
    size_t completed;
    char *key;
} AuditEvent;

typedef struct
{
    AuditEvent *events;
    size_t count;
    size_t capacity;
} AuditLog;

typedef struct
{
    unsigned long uid;
    const char *path;
} DeniedFile;

typedef struct
{
    unsigned long uid;
    size_t modifications;
} FileUser;

static void PrintUsage(FILE *stream, const char *program)
{
    fprintf(stream, "Usage: %s -s\n", program);
    fprintf(stream, "       %s -i filename\n", program);
    fprintf(stream, "       %s -h\n", program);
    fprintf(stream, "  -s           Show UIDs denied access to more than five distinct files\n");
    fprintf(stream, "  -i filename  Show successful-access users and modification counts\n");
}

static int ParseNumber(const char *text, unsigned long long *value)
{
    unsigned long long number;
    char *end;

    if (*text == '\0')
        return -1;
    for (const char *cursor = text; *cursor != '\0'; cursor++)
    {
        if (*cursor < '0' || *cursor > '9')
            return -1;
    }
    errno = 0;
    number = strtoull(text, &end, 10);
    if (errno == ERANGE || *end != '\0')
        return -1;
    *value = number;
    return 0;
}

static int ParseSize(const char *text, size_t *value)
{
    unsigned long long number;

    if (ParseNumber(text, &number) != 0 || number > SIZE_MAX)
        return -1;
    *value = (size_t)number;
    return 0;
}

static int HexDigit(char digit)
{
    if (digit >= '0' && digit <= '9') return digit - '0';
    if (digit >= 'A' && digit <= 'F') return digit - 'A' + 10;
    return -1;
}

static char *UnescapeField(const char *encoded)
{
    size_t length = strlen(encoded);
    char *decoded = malloc(length + 1);
    size_t used = 0;

    if (decoded == NULL)
        return NULL;
    for (size_t i = 0; i < length; i++)
    {
        unsigned char byte = (unsigned char)encoded[i];
        if (byte == '%')
        {
            int high;
            int low;

            if (i + 2 >= length || (high = HexDigit(encoded[i + 1])) < 0 ||
                (low = HexDigit(encoded[i + 2])) < 0)
                goto invalid;
            byte = (unsigned char)(high * 16 + low);
            i += 2;
        }
        else if (byte < 0x21 || byte > 0x7e)
        {
            goto invalid;
        }
        if (byte == '\0')
            goto invalid;
        decoded[used++] = (char)byte;
    }
    decoded[used] = '\0';
    return decoded;

invalid:
    free(decoded);
    return NULL;
}

static char *MakeAbsolutePath(const char *path)
{
    char *directory;
    char *absolute;
    size_t length;

    if (path == NULL)
        return NULL;
    if (path[0] == '/')
        return strdup(path);
    directory = getcwd(NULL, 0);
    if (directory == NULL)
        return NULL;
    if (strlen(directory) > SIZE_MAX - strlen(path) - 2)
    {
        free(directory);
        return NULL;
    }
    length = strlen(directory) + strlen(path) + 2;
    absolute = malloc(length);
    if (absolute != NULL)
        snprintf(absolute, length, "%s/%s", directory, path);
    free(directory);
    return absolute;
}

// Keep lexical normalization identical to the logger, without resolving symlinks.
static char *NormalizePath(const char *absolute)
{
    size_t length = strlen(absolute);
    char *key = malloc(length + 2);
    size_t used = 1;
    size_t offset = 0;

    if (key == NULL)
        return NULL;
    key[0] = '/';
    while (offset < length)
    {
        size_t start;
        size_t segment;

        while (absolute[offset] == '/')
            offset++;
        start = offset;
        while (absolute[offset] != '\0' && absolute[offset] != '/')
            offset++;
        segment = offset - start;
        if (segment == 0 || (segment == 1 && absolute[start] == '.'))
            continue;
        if (segment == 2 && absolute[start] == '.' && absolute[start + 1] == '.')
        {
            if (used > 1)
            {
                while (used > 1 && key[used - 1] != '/')
                    used--;
                if (used > 1)
                    used--;
            }
            continue;
        }
        if (used > 1)
            key[used++] = '/';
        memcpy(key + used, absolute + start, segment);
        used += segment;
    }
    key[used] = '\0';
    return key;
}

static int ValidTimestamp(const char *date, const char *clock_text)
{
    int year, month, day, hour, minute, second;

    if (strlen(date) != 10 || strlen(clock_text) != 19 ||
        date[4] != '-' || date[7] != '-' || clock_text[2] != ':' ||
        clock_text[5] != ':' || clock_text[8] != '.' || clock_text[18] != 'Z')
        return 0;
    for (size_t i = 0; i < 10; i++)
    {
        if (i != 4 && i != 7 && (date[i] < '0' || date[i] > '9'))
            return 0;
    }
    for (size_t i = 0; i < 18; i++)
    {
        if (i != 2 && i != 5 && i != 8 &&
            (clock_text[i] < '0' || clock_text[i] > '9'))
            return 0;
    }
    year = atoi(date);
    month = atoi(date + 5);
    day = atoi(date + 8);
    hour = atoi(clock_text);
    minute = atoi(clock_text + 3);
    second = atoi(clock_text + 6);
    return year >= 1 && month >= 1 && month <= 12 && day >= 1 && day <= 31 &&
           hour <= 23 && minute <= 59 && second <= 60;
}

static int ValidHash(const char *hash, const char *status, int operation)
{
    if (strcmp(hash, "N/A") == 0)
        return strcmp(status, "unavailable") == 0;
    if (strlen(hash) != 64 ||
        (operation == 3 ? strcmp(status, "post-close") != 0 :
                          strcmp(status, "visible") != 0))
        return 0;
    for (size_t i = 0; i < 64; i++)
    {
        if (!((hash[i] >= '0' && hash[i] <= '9') ||
              (hash[i] >= 'a' && hash[i] <= 'f')))
            return 0;
    }
    return 1;
}

static int ParseRecord(char *line, AuditEvent *event)
{
    char *fields[FIELD_COUNT];
    char *original = NULL;
    char *key = NULL;
    char *normalized = NULL;
    char *mode = NULL;
    unsigned long long value;
    int operation, denied, success, partial, failure;

    memset(event, 0, sizeof(*event));
    fields[0] = line;
    for (size_t i = 1; i < FIELD_COUNT; i++)
    {
        char *separator = strchr(fields[i - 1], '\t');
        if (separator == NULL)
            return -1;
        *separator = '\0';
        fields[i] = separator + 1;
    }
    if (strchr(fields[FIELD_COUNT - 1], '\t') != NULL ||
        strcmp(fields[0], "v1") != 0 ||
        ParseNumber(fields[1], &value) != 0 || value > ULONG_MAX)
        return -1;
    event->uid = (unsigned long)value;
    if (ParseNumber(fields[2], &value) != 0 || value == 0 || value > LONG_MAX ||
        ParseNumber(fields[6], &value) != 0 || value > 3)
        return -1;
    operation = (int)value;
    if (ParseNumber(fields[7], &value) != 0 || value > 1)
        return -1;
    denied = (int)value;
    success = strcmp(fields[9], "success") == 0;
    partial = strcmp(fields[9], "partial") == 0;
    failure = strcmp(fields[9], "failure") == 0;
    if ((!success && !partial && !failure) || !ValidTimestamp(fields[4], fields[5]) ||
        !ValidHash(fields[8], fields[14], operation) ||
        ParseNumber(fields[12], &value) != 0 || value > 1)
        return -1;
    if ((operation <= 1 && partial) || (operation == 3 && partial) ||
        (operation >= 2 && value != 0))
        return -1;
    if (operation <= 1)
    {
        if (operation == 0 && (value != 1 || strcmp(fields[11], "absent") != 0))
            return -1;
        if (strcmp(fields[11], "absent") != 0 &&
            strcmp(fields[11], "present") != 0 &&
            strcmp(fields[11], "unknown") != 0)
            return -1;
        mode = UnescapeField(fields[10]);
        if (mode == NULL)
            goto invalid;
    }
    else if (strcmp(fields[10], "-") != 0 || strcmp(fields[11], "-") != 0)
    {
        return -1;
    }
    if (ParseNumber(fields[13], &value) != 0 || value > INT_MAX ||
        ((!failure && value != 0) ||
         (denied != (failure && (value == EACCES || value == EPERM)))))
        goto invalid;
    if (operation == 2)
    {
        if (ParseSize(fields[15], &event->size) != 0 ||
            ParseSize(fields[16], &event->requested) != 0 ||
            ParseSize(fields[17], &event->completed) != 0 ||
            event->completed > event->requested)
            goto invalid;
        if ((success != (event->size == 0 || event->requested == 0 ||
                        event->completed == event->requested)) ||
            (partial != (event->size > 0 && event->requested > 0 &&
                         event->completed > 0 && event->completed < event->requested)))
            goto invalid;
    }
    else if (strcmp(fields[15], "-") != 0 || strcmp(fields[16], "-") != 0 ||
             strcmp(fields[17], "-") != 0)
    {
        goto invalid;
    }
    original = UnescapeField(fields[3]);
    key = UnescapeField(fields[18]);
    if (original == NULL || original[0] != '/' || key == NULL || key[0] != '/')
        goto invalid;
    normalized = NormalizePath(original);
    if (normalized == NULL || strcmp(key, normalized) != 0)
        goto invalid;
    event->operation = operation;
    event->denied = denied;
    event->successful_open = operation <= 1 && success;
    event->key = key;
    free(normalized);
    free(original);
    free(mode);
    return 0;

invalid:
    free(normalized);
    free(original);
    free(key);
    free(mode);
    return -1;
}

static void FreeLog(AuditLog *log)
{
    for (size_t i = 0; i < log->count; i++)
        free(log->events[i].key);
    free(log->events);
}

static int AddEvent(AuditLog *log, AuditEvent *event)
{
    if (log->count == log->capacity)
    {
        size_t next = log->capacity == 0 ? 64 : log->capacity * 2;
        AuditEvent *grown;

        if (next < log->capacity || next > SIZE_MAX / sizeof(*grown))
            return -1;
        grown = realloc(log->events, next * sizeof(*grown));
        if (grown == NULL)
            return -1;
        log->events = grown;
        log->capacity = next;
    }
    log->events[log->count++] = *event;
    return 0;
}

static int ReadLog(AuditLog *log)
{
    struct stat metadata;
    char *line = NULL;
    size_t capacity = 0;
    size_t line_number = 0;
    FILE *stream = NULL;
    int fd = -1;
    int result = -1;
    ssize_t length;

    fd = open(AUDIT_LOG_PATH, O_RDONLY | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK);
    if (fd < 0 || fstat(fd, &metadata) != 0 || !S_ISREG(metadata.st_mode))
    {
        fprintf(stderr, "audit_monitor: cannot read a regular audit log at %s\n", AUDIT_LOG_PATH);
        goto cleanup;
    }
    if (flock(fd, LOCK_SH) != 0)
    {
        perror("audit_monitor: cannot lock audit log");
        goto cleanup;
    }
    stream = fdopen(fd, "r");
    if (stream == NULL)
    {
        perror("audit_monitor: fdopen");
        goto cleanup;
    }
    fd = -1;
    while ((length = getline(&line, &capacity, stream)) >= 0)
    {
        AuditEvent event;

        line_number++;
        if (length < 2 || line[length - 1] != '\n' ||
            memchr(line, '\0', (size_t)length) != NULL)
        {
            fprintf(stderr, "audit_monitor: invalid record on line %zu\n", line_number);
            goto cleanup;
        }
        line[length - 1] = '\0';
        if (ParseRecord(line, &event) != 0)
        {
            fprintf(stderr, "audit_monitor: invalid record on line %zu\n", line_number);
            goto cleanup;
        }
        if (AddEvent(log, &event) != 0)
        {
            free(event.key);
            fprintf(stderr, "audit_monitor: out of memory\n");
            goto cleanup;
        }
    }
    if (ferror(stream))
    {
        perror("audit_monitor: reading audit log");
        goto cleanup;
    }
    result = 0;

cleanup:
    free(line);
    if (stream != NULL)
    {
        if (fclose(stream) != 0)
        {
            perror("audit_monitor: closing audit log");
            result = -1;
        }
    }
    else if (fd >= 0)
        close(fd);
    return result;
}

static int CompareDeniedFile(const void *left, const void *right)
{
    const DeniedFile *a = left;
    const DeniedFile *b = right;

    if (a->uid != b->uid)
        return a->uid < b->uid ? -1 : 1;
    return strcmp(a->path, b->path);
}

static int ListSuspiciousUsers(const AuditLog *log)
{
    DeniedFile *denials = calloc(log->count == 0 ? 1 : log->count, sizeof(*denials));
    size_t count = 0;
    int found = 0;

    if (denials == NULL)
        return -1;
    for (size_t i = 0; i < log->count; i++)
    {
        const AuditEvent *event = &log->events[i];
        if (event->operation <= 1 && event->denied)
        {
            denials[count].uid = event->uid;
            denials[count++].path = event->key;
        }
    }
    qsort(denials, count, sizeof(*denials), CompareDeniedFile);
    for (size_t start = 0; start < count;)
    {
        size_t end = start;
        size_t distinct = 0;

        while (end < count && denials[end].uid == denials[start].uid)
        {
            if (end == start || strcmp(denials[end].path, denials[end - 1].path) != 0)
                distinct++;
            end++;
        }
        if (distinct > 5)
        {
            printf("UID %lu: %zu distinct denied files\n", denials[start].uid, distinct);
            found = 1;
        }
        start = end;
    }
    if (!found)
        puts("No suspicious users found.");
    free(denials);
    return 0;
}

static int CompareUsers(const void *left, const void *right)
{
    const FileUser *a = left;
    const FileUser *b = right;

    if (a->uid == b->uid)
        return 0;
    return a->uid < b->uid ? -1 : 1;
}

static int ListFileActivity(const AuditLog *log, const char *filename)
{
    char *absolute = MakeAbsolutePath(filename);
    char *key = absolute == NULL ? NULL : NormalizePath(absolute);
    FileUser *users;
    size_t count = 0;
    size_t total = 0;

    free(absolute);
    if (key == NULL)
    {
        fprintf(stderr, "audit_monitor: cannot normalize file pathname\n");
        return -1;
    }
    users = calloc(log->count == 0 ? 1 : log->count, sizeof(*users));
    if (users == NULL)
    {
        free(key);
        return -1;
    }
    for (size_t i = 0; i < log->count; i++)
    {
        const AuditEvent *event = &log->events[i];
        size_t index = 0;
        int modified = event->operation == 2 && event->size > 0 &&
                       event->requested > 0 && event->completed > 0;

        if (strcmp(event->key, key) != 0 || (!event->successful_open && !modified))
            continue;
        while (index < count && users[index].uid != event->uid)
            index++;
        if (index == count)
        {
            users[count].uid = event->uid;
            users[count++].modifications = 0;
        }
        if (modified)
        {
            if (users[index].modifications == SIZE_MAX || total == SIZE_MAX)
            {
                fprintf(stderr, "audit_monitor: modification count overflow\n");
                free(users);
                free(key);
                return -1;
            }
            users[index].modifications++;
            total++;
        }
    }
    qsort(users, count, sizeof(*users), CompareUsers);
    printf("File: %s\n", key);
    for (size_t i = 0; i < count; i++)
        printf("UID %lu: %zu modifications\n", users[i].uid, users[i].modifications);
    printf("Total modifications: %zu\n", total);
    free(users);
    free(key);
    return 0;
}

int main(int argc, char *argv[])
{
    AuditLog log = {0};
    int status;

    if (argc == 2 && strcmp(argv[1], "-h") == 0)
    {
        PrintUsage(stdout, argv[0]);
        return 0;
    }
    if (!((argc == 2 && strcmp(argv[1], "-s") == 0) ||
          (argc == 3 && strcmp(argv[1], "-i") == 0 && argv[2][0] != '\0')))
    {
        PrintUsage(stderr, argv[0]);
        return 2;
    }
    if (ReadLog(&log) != 0)
    {
        FreeLog(&log);
        return 1;
    }
    status = argc == 2 ? ListSuspiciousUsers(&log) : ListFileActivity(&log, argv[2]);
    FreeLog(&log);
    if (status != 0)
    {
        fprintf(stderr, "audit_monitor: analysis failed\n");
        return 1;
    }
    return 0;
}
