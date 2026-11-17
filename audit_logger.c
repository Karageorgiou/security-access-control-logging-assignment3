#define _GNU_SOURCE

#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <openssl/evp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/file.h>
#include <sys/stat.h>
#include <sys/statfs.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>
#include <linux/magic.h>

#define AUDIT_LOG_PATH "/tmp/access_audit.log"

static __thread int audit_depth;
static int diagnostic_reported;

typedef enum
{
    PRIOR_UNKNOWN,
    PRIOR_PRESENT,
    PRIOR_ABSENT
} PriorExistence;

static void ReportAuditFailure(void)
{
    static const char message[] = "audit_logger: could not append to /tmp/access_audit.log\n";

    if (__atomic_exchange_n(&diagnostic_reported, 1, __ATOMIC_RELAXED) == 0)
    {
        ssize_t result = write(STDERR_FILENO, message, sizeof(message) - 1);
        (void)result;
    }
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

    length = strlen(directory) + strlen(path) + 2;
    absolute = malloc(length);
    if (absolute != NULL)
        snprintf(absolute, length, "%s/%s", directory, path);
    free(directory);
    return absolute;
}

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

static char *EscapeField(const char *value)
{
    static const char hex[] = "0123456789ABCDEF";
    size_t length = strlen(value);
    char *encoded;
    size_t used = 0;

    if (length > (SIZE_MAX - 1) / 3)
        return NULL;
    encoded = malloc(length * 3 + 1);
    if (encoded == NULL)
        return NULL;

    for (size_t i = 0; i < length; i++)
    {
        unsigned char byte = (unsigned char)value[i];
        if (byte >= 0x21 && byte <= 0x7e && byte != '%')
        {
            encoded[used++] = (char)byte;
        }
        else
        {
            encoded[used++] = '%';
            encoded[used++] = hex[byte >> 4];
            encoded[used++] = hex[byte & 15];
        }
    }

    encoded[used] = '\0';
    return encoded;
}

static PriorExistence GetPriorExistence(const char *path)
{
    struct stat metadata;

    if (stat(path, &metadata) == 0)
        return PRIOR_PRESENT;
    if (errno == ENOENT)
        return PRIOR_ABSENT;
    return PRIOR_UNKNOWN;
}

static int IsOrdinaryRegularFile(int descriptor, struct stat *metadata)
{
    struct statfs filesystem;

    if (fstat(descriptor, metadata) != 0 || !S_ISREG(metadata->st_mode))
        return 0;
    if (fstatfs(descriptor, &filesystem) != 0)
        return 0;

    // A reported regular-file type is insufficient for procfs and sysfs content.
    if (filesystem.f_type == PROC_SUPER_MAGIC || filesystem.f_type == SYSFS_MAGIC)
        return 0;
#ifdef DEBUGFS_MAGIC
    if (filesystem.f_type == DEBUGFS_MAGIC)
        return 0;
#endif
#ifdef TRACEFS_MAGIC
    if (filesystem.f_type == TRACEFS_MAGIC)
        return 0;
#endif
    return 1;
}

static int HashFile(const char *path, FILE *stream, char digest_hex[65])
{
    static const char hex[] = "0123456789abcdef";
    unsigned char buffer[8192];
    unsigned char digest[EVP_MAX_MD_SIZE];
    unsigned int digest_length = 0;
    struct stat observed;
    struct stat target;
    EVP_MD_CTX *context = NULL;
    int descriptor = -1;
    int success = 0;
    ssize_t count;

    if (stream != NULL)
    {
        if (fileno(stream) < 0 || !IsOrdinaryRegularFile(fileno(stream), &observed))
            return 0;
    }
    else if (stat(path, &observed) != 0 || !S_ISREG(observed.st_mode))
    {
        return 0;
    }

    descriptor = open(path, O_RDONLY | O_CLOEXEC | O_NONBLOCK | O_NOFOLLOW);
    if (descriptor < 0)
        return 0;
    if (!IsOrdinaryRegularFile(descriptor, &target))
        goto cleanup;
    if (target.st_dev != observed.st_dev || target.st_ino != observed.st_ino)
        goto cleanup;

    context = EVP_MD_CTX_new();
    if (context == NULL || EVP_DigestInit_ex(context, EVP_sha256(), NULL) != 1)
        goto cleanup;

    while ((count = read(descriptor, buffer, sizeof(buffer))) != 0)
    {
        if (count < 0)
        {
            if (errno == EINTR)
                continue;
            goto cleanup;
        }
        if (EVP_DigestUpdate(context, buffer, (size_t)count) != 1)
            goto cleanup;
    }
    if (EVP_DigestFinal_ex(context, digest, &digest_length) != 1 || digest_length != 32)
        goto cleanup;

    for (size_t i = 0; i < digest_length; i++)
    {
        digest_hex[2 * i] = hex[digest[i] >> 4];
        digest_hex[2 * i + 1] = hex[digest[i] & 15];
    }
    digest_hex[64] = '\0';
    success = 1;

cleanup:
    EVP_MD_CTX_free(context);
    close(descriptor);
    return success;
}

static int AppendRecord(const char *record, size_t length)
{
    struct stat metadata;
    size_t written = 0;
    int descriptor = open(AUDIT_LOG_PATH,
                          O_WRONLY | O_APPEND | O_CLOEXEC | O_NONBLOCK | O_NOFOLLOW);
    int success = 0;

    // The shared log is provisioned explicitly; interception never creates it.
    if (descriptor < 0)
        return -1;
    if (fstat(descriptor, &metadata) != 0 || !S_ISREG(metadata.st_mode))
        goto cleanup;
    if (flock(descriptor, LOCK_EX) != 0)
        goto cleanup;

    while (written < length)
    {
        ssize_t count = write(descriptor, record + written, length - written);
        if (count < 0 && errno == EINTR)
            continue;
        if (count <= 0)
            break;
        written += (size_t)count;
    }
    success = written == length;
    if (flock(descriptor, LOCK_UN) != 0)
        success = 0;

cleanup:
    if (close(descriptor) != 0)
        success = 0;
    return success ? 0 : -1;
}

static void RecordOpen(const char *absolute, const char *mode, PriorExistence prior,
                       int creation_intent, FILE *stream, int original_errno,
                       const struct timespec *timestamp)
{
    char digest[65] = "N/A";
    char date[16];
    char time_text[32];
    char *encoded_path = NULL;
    char *normalized = NULL;
    char *encoded_key = NULL;
    char *encoded_mode = NULL;
    char *record = NULL;
    const char *prior_text = prior == PRIOR_PRESENT ? "present" :
                             prior == PRIOR_ABSENT ? "absent" : "unknown";
    const char *outcome = stream == NULL ? "failure" : "success";
    const char *hash_status;
    struct tm utc;
    int operation = creation_intent && prior == PRIOR_ABSENT ? 0 : 1;
    int denied = stream == NULL && (original_errno == EACCES || original_errno == EPERM);
    int needed;

    if (absolute == NULL || gmtime_r(&timestamp->tv_sec, &utc) == NULL)
        goto failure;
    if (strftime(date, sizeof(date), "%Y-%m-%d", &utc) == 0 ||
        strftime(time_text, sizeof(time_text), "%H:%M:%S", &utc) == 0)
        goto failure;

    normalized = NormalizePath(absolute);
    encoded_path = EscapeField(absolute);
    encoded_key = normalized == NULL ? NULL : EscapeField(normalized);
    encoded_mode = EscapeField(mode == NULL ? "" : mode);
    if (encoded_path == NULL || encoded_key == NULL || encoded_mode == NULL)
        goto failure;

    if (HashFile(absolute, stream, digest))
        hash_status = "visible";
    else
        hash_status = "unavailable";

    needed = snprintf(NULL, 0,
                      "v1\t%lu\t%ld\t%s\t%s\t%s.%09ldZ\t%d\t%d\t%s\t%s\t%s\t%s\t%d\t%d\t%s\t-\t-\t-\t%s\n",
                      (unsigned long)getuid(), (long)getpid(), encoded_path, date,
                      time_text, timestamp->tv_nsec, operation, denied, digest,
                      outcome, encoded_mode, prior_text, creation_intent,
                      stream == NULL ? original_errno : 0, hash_status, encoded_key);
    if (needed < 0)
        goto failure;
    record = malloc((size_t)needed + 1);
    if (record == NULL)
        goto failure;

    snprintf(record, (size_t)needed + 1,
             "v1\t%lu\t%ld\t%s\t%s\t%s.%09ldZ\t%d\t%d\t%s\t%s\t%s\t%s\t%d\t%d\t%s\t-\t-\t-\t%s\n",
             (unsigned long)getuid(), (long)getpid(), encoded_path, date,
             time_text, timestamp->tv_nsec, operation, denied, digest,
             outcome, encoded_mode, prior_text, creation_intent,
             stream == NULL ? original_errno : 0, hash_status, encoded_key);
    if (AppendRecord(record, (size_t)needed) != 0)
        goto failure;
    goto cleanup;

failure:
    ReportAuditFailure();
cleanup:
    free(record);
    free(encoded_mode);
    free(encoded_key);
    free(encoded_path);
    free(normalized);
}

FILE *fopen(const char *path, const char *mode)
{
    FILE *(*original_fopen)(const char *, const char *);
    FILE *result;
    char *absolute = NULL;
    PriorExistence prior = PRIOR_UNKNOWN;
    int incoming_errno = errno;
    int original_errno;
    int nested = audit_depth++ > 0;
    int creation_intent = 0;
    struct timespec timestamp;

    original_fopen = dlsym(RTLD_NEXT, "fopen");
    if (original_fopen == NULL)
    {
        audit_depth--;
        errno = ENOSYS;
        return NULL;
    }

    if (!nested)
    {
        absolute = MakeAbsolutePath(path);
        if (absolute != NULL)
            prior = GetPriorExistence(absolute);
        creation_intent = mode != NULL && (mode[0] == 'w' || mode[0] == 'a');
    }

    // Pre-call observation is advisory; only the libc call determines the result.
    errno = incoming_errno;
    result = original_fopen(path, mode);
    original_errno = errno;
    if (!nested)
    {
        if (clock_gettime(CLOCK_REALTIME, &timestamp) == 0)
            RecordOpen(absolute, mode, prior, creation_intent, result, original_errno, &timestamp);
        else
            ReportAuditFailure();
    }

    free(absolute);
    audit_depth--;
    errno = original_errno;
    return result;
}
