#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <dirent.h>

#define SHARED_DIRECTORY "/tmp/security_a3_tests"
#define WORKING_FILES 15
#define MAX_PROTECTED_FILES 10

typedef struct
{
    char path[PATH_MAX];
    dev_t device;
    ino_t inode;
    int created;
    int identified;
    int removed;
} ProtectedFile;

static void ReportError(const char *operation, const char *path)
{
    fprintf(stderr, "%s: %s: %s\n", operation, path, strerror(errno));
}

static int CheckDirectory(int descriptor, mode_t permissions, uid_t owner,
                          int check_owner, const char *name)
{
    struct stat status;

    if (fstat(descriptor, &status) != 0)
    {
        ReportError("fstat", name);
        return -1;
    }
    if (!S_ISDIR(status.st_mode) || (status.st_mode & 07777) != permissions ||
        (check_owner && status.st_uid != owner))
    {
        fprintf(stderr, "Unsafe directory type, owner or permissions: %s\n", name);
        return -1;
    }
    return 0;
}

static int OpenOrCreateDirectory(int parent, const char *name, mode_t permissions,
                                 uid_t owner, int check_owner)
{
    int descriptor;
    mode_t previous_umask = umask(0);
    int created = mkdirat(parent, name, permissions);
    int mkdir_error = errno;
    umask(previous_umask);

    if (created != 0 && mkdir_error != EEXIST)
    {
        errno = mkdir_error;
        ReportError("mkdirat", name);
        return -1;
    }
    descriptor = openat(parent, name, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    if (descriptor < 0)
    {
        ReportError("openat", name);
        return -1;
    }
    if (CheckDirectory(descriptor, permissions, owner, check_owner, name) != 0)
    {
        close(descriptor);
        return -1;
    }
    return descriptor;
}

static int ParseRunNumber(const char *name, unsigned int *number)
{
    char *end;
    unsigned long value;

    if (strncmp(name, "run_", 4) != 0 || name[4] < '0' || name[4] > '9')
        return 0;
    errno = 0;
    value = strtoul(name + 4, &end, 10);
    if (errno != 0 || *end != '\0' || value == 0 || value > UINT_MAX)
        return 0;
    *number = (unsigned int)value;
    return 1;
}

static int ClaimRunDirectory(int user_directory, char *name, size_t capacity)
{
    DIR *entries;
    struct dirent *entry;
    unsigned int highest = 0;
    unsigned int number;
    int descriptor;
    int duplicated = dup(user_directory);

    if (duplicated < 0 || (entries = fdopendir(duplicated)) == NULL)
    {
        if (duplicated >= 0)
            close(duplicated);
        perror("fdopendir");
        return -1;
    }
    errno = 0;
    while ((entry = readdir(entries)) != NULL)
    {
        if (ParseRunNumber(entry->d_name, &number) && number > highest)
            highest = number;
        errno = 0;
    }
    if (errno != 0)
    {
        perror("readdir");
        closedir(entries);
        return -1;
    }
    if (closedir(entries) != 0 || highest == UINT_MAX)
    {
        fprintf(stderr, "Unable to enumerate or number run directories\n");
        return -1;
    }
    for (number = highest + 1; number != 0; number++)
    {
        int length = snprintf(name, capacity, "run_%02u", number);
        mode_t previous_umask;
        int created;
        int error;

        if (length < 0 || (size_t)length >= capacity)
            break;
        previous_umask = umask(0);
        created = mkdirat(user_directory, name, 0700);
        error = errno;
        umask(previous_umask);
        if (created != 0)
        {
            if (error == EEXIST)
                continue;
            errno = error;
            ReportError("mkdirat", name);
            return -1;
        }
        descriptor = openat(user_directory, name,
                            O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
        if (descriptor < 0 ||
            CheckDirectory(descriptor, 0700, geteuid(), 1, name) != 0)
        {
            if (descriptor < 0)
                ReportError("openat", name);
            if (descriptor >= 0)
                close(descriptor);
            return -1;
        }
        return descriptor;
    }
    fprintf(stderr, "Run-directory numbering exhausted\n");
    return -1;
}

static int CreateRunPath(char path[PATH_MAX])
{
    char user_name[80];
    char run_name[80];
    int temp_directory = -1;
    int shared_directory = -1;
    int user_directory = -1;
    int run_directory = -1;
    int length;

    temp_directory = open("/tmp", O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
    if (temp_directory < 0)
    {
        perror("open /tmp");
        goto failure;
    }
    if (CheckDirectory(temp_directory, 01777, 0, 1, "/tmp") != 0)
        goto failure;
    shared_directory = OpenOrCreateDirectory(temp_directory, "security_a3_tests",
                                             01777, 0, 0);
    if (shared_directory < 0)
        goto failure;
    snprintf(user_name, sizeof(user_name), "a3_test_files_%lu", (unsigned long)geteuid());
    user_directory = OpenOrCreateDirectory(shared_directory, user_name,
                                           0700, geteuid(), 1);
    if (user_directory < 0)
        goto failure;
    run_directory = ClaimRunDirectory(user_directory, run_name, sizeof(run_name));
    if (run_directory < 0)
        goto failure;
    length = snprintf(path, PATH_MAX, "%s/%s/%s", SHARED_DIRECTORY,
                      user_name, run_name);
    if (length < 0 || length >= PATH_MAX)
    {
        fprintf(stderr, "Run directory path is too long\n");
        goto failure;
    }
    close(run_directory);
    close(user_directory);
    close(shared_directory);
    close(temp_directory);
    return 0;

failure:
    if (run_directory >= 0)
        close(run_directory);
    if (user_directory >= 0)
        close(user_directory);
    if (shared_directory >= 0)
        close(shared_directory);
    if (temp_directory >= 0)
        close(temp_directory);
    return -1;
}

static int MakePath(char path[PATH_MAX], const char *directory, const char *prefix,
                    int number)
{
    int length = snprintf(path, PATH_MAX, "%s/%s_%02d", directory, prefix, number);
    if (length < 0 || length >= PATH_MAX)
    {
        fprintf(stderr, "File path is too long\n");
        return -1;
    }
    return 0;
}

static int WriteNumberedMessage(FILE *stream, int file_number, int write_number)
{
    char message[80];
    int length = snprintf(message, sizeof(message), "File %02d - Write %02d\n",
                          file_number, write_number);
    if (length < 0 || (size_t)length >= sizeof(message) ||
        fwrite(message, 1, (size_t)length, stream) != (size_t)length)
    {
        fprintf(stderr, "Failed writing file %02d, message %02d\n",
                file_number, write_number);
        return -1;
    }
    return 0;
}

static int ReadCompleteFile(const char *path)
{
    FILE *stream = fopen(path, "r");
    int failed = 0;

    if (stream == NULL)
    {
        ReportError("fopen for reading", path);
        return -1;
    }
    while (fgetc(stream) != EOF)
    {
    }
    if (ferror(stream))
    {
        ReportError("fgetc", path);
        failed = 1;
    }
    if (fclose(stream) != 0)
    {
        ReportError("fclose after reading", path);
        failed = 1;
    }
    return failed ? -1 : 0;
}

static int ProcessWorkingFile(const char *directory, int file_number)
{
    char path[PATH_MAX];
    FILE *stream;
    int writes = file_number <= 9 ? 2 * file_number : (file_number >= 13 ? 1 : 0);
    int separate_sessions = file_number <= 9 && file_number % 2 == 0;

    if (MakePath(path, directory, "a3_test_file", file_number) != 0)
        return -1;
    if (separate_sessions)
    {
        for (int index = 1; index <= writes; index++)
        {
            int failed;
            stream = fopen(path, index == 1 ? "wx" : "a");
            if (stream == NULL)
            {
                ReportError("fopen for writing", path);
                return -1;
            }
            failed = WriteNumberedMessage(stream, file_number, index);
            if (fclose(stream) != 0)
            {
                ReportError("fclose after writing", path);
                failed = -1;
            }
            if (failed != 0)
                return -1;
        }
    }
    else
    {
        int failed = 0;
        stream = fopen(path, "wx");
        if (stream == NULL)
        {
            ReportError("fopen for creation", path);
            return -1;
        }
        for (int index = 1; index <= writes; index++)
        {
            if (WriteNumberedMessage(stream, file_number, index) != 0)
            {
                failed = 1;
                break;
            }
        }
        if (fclose(stream) != 0)
        {
            ReportError("fclose after writing", path);
            failed = 1;
        }
        if (failed)
            return -1;
    }
    if (ReadCompleteFile(path) != 0)
        return -1;
    if (printf("a3_test_file_%02d: %d successful writes\n", file_number, writes) < 0 ||
        fflush(stdout) != 0)
    {
        perror("file summary output");
        return -1;
    }
    return 0;
}

static int SameProtectedFile(const ProtectedFile *fixture)
{
    struct stat status;

    if (!fixture->identified || lstat(fixture->path, &status) != 0 ||
        !S_ISREG(status.st_mode) || status.st_uid != geteuid() ||
        status.st_dev != fixture->device || status.st_ino != fixture->inode)
    {
        fprintf(stderr, "Protected fixture identity unavailable or changed: %s\n",
                fixture->path);
        return 0;
    }
    return 1;
}

static int CleanupProtectedFiles(ProtectedFile fixtures[MAX_PROTECTED_FILES],
                                  int fixture_count)
{
    int failed = 0;

    for (int index = 0; index < fixture_count; index++)
    {
        ProtectedFile *fixture = &fixtures[index];
        if (!fixture->created || fixture->removed)
            continue;
        if (!SameProtectedFile(fixture))
        {
            failed = 1;
            continue;
        }
        if (chmod(fixture->path, 0600) != 0)
        {
            ReportError("restore protected file permissions", fixture->path);
            failed = 1;
            continue;
        }
        if (!SameProtectedFile(fixture))
        {
            failed = 1;
            continue;
        }
        if (unlink(fixture->path) != 0)
        {
            ReportError("remove protected file", fixture->path);
            failed = 1;
        }
        else
            fixture->removed = 1;
    }
    return failed ? -1 : 0;
}

static int ProcessProtectedFiles(const char *directory, int count)
{
    ProtectedFile fixtures[MAX_PROTECTED_FILES] = {0};
    int created_count = 0;
    int failed = 0;

    for (int number = 1; number <= count; number++)
    {
        ProtectedFile *fixture = &fixtures[created_count];
        FILE *stream;
        struct stat status;
        int denied_errno;
        const char text[] = "This is a protected file";

        if (MakePath(fixture->path, directory, "a3_protected_file", number) != 0)
        {
            failed = 1;
            break;
        }
        stream = fopen(fixture->path, "wx");
        if (stream == NULL)
        {
            ReportError("fopen protected file", fixture->path);
            failed = 1;
            break;
        }
        fixture->created = 1;
        created_count++;
        if (fstat(fileno(stream), &status) == 0 && S_ISREG(status.st_mode) &&
            status.st_uid == geteuid())
        {
            fixture->identified = 1;
            fixture->device = status.st_dev;
            fixture->inode = status.st_ino;
        }
        else
        {
            ReportError("fstat protected file", fixture->path);
            failed = 1;
        }
        if (!failed && fwrite(text, 1, sizeof(text) - 1, stream) != sizeof(text) - 1)
        {
            ReportError("fwrite protected file", fixture->path);
            failed = 1;
        }
        if (fclose(stream) != 0)
        {
            ReportError("fclose protected file", fixture->path);
            failed = 1;
        }
        if (failed)
            break;
        if (!SameProtectedFile(fixture) || chmod(fixture->path, 0000) != 0)
        {
            if (fixture->identified)
                ReportError("protect file", fixture->path);
            failed = 1;
            break;
        }
        errno = 0;
        stream = fopen(fixture->path, "r");
        denied_errno = errno;
        if (stream != NULL)
        {
            fprintf(stderr, "Protected file unexpectedly readable: %s\n", fixture->path);
            if (fclose(stream) != 0)
                ReportError("fclose unexpected protected open", fixture->path);
            failed = 1;
            break;
        }
        if (denied_errno != EACCES && denied_errno != EPERM)
        {
            fprintf(stderr, "Unexpected protected-file error (%d): %s\n",
                    denied_errno, fixture->path);
            failed = 1;
            break;
        }
        if (CleanupProtectedFiles(fixtures, created_count) != 0)
        {
            failed = 1;
            break;
        }
    }
    if (CleanupProtectedFiles(fixtures, created_count) != 0)
        failed = 1;
    return failed ? -1 : 0;
}

int main(int argc, char *argv[])
{
    char directory[PATH_MAX];
    char example[PATH_MAX];
    int normal;
    int denied_count;

    if (argc == 1)
        normal = 0;
    else if (argc == 2 && strcmp(argv[1], "--normal") == 0)
        normal = 1;
    else
    {
        fprintf(stderr, "Usage: %s [--normal]\n", argv[0]);
        return 1;
    }
    if (geteuid() == 0)
    {
        fprintf(stderr, "Run test_audit as an ordinary non-root user.\n");
        return 1;
    }
    if (CreateRunPath(directory) != 0)
        return 1;
    for (int number = 1; number <= WORKING_FILES; number++)
    {
        if (ProcessWorkingFile(directory, number) != 0)
        {
            fprintf(stderr, "Demonstration stopped. Working files kept at %s\n",
                    directory);
            return 1;
        }
    }
    denied_count = normal ? 4 : MAX_PROTECTED_FILES;
    if (ProcessProtectedFiles(directory, denied_count) != 0)
    {
        fprintf(stderr, "Demonstration stopped. Working files kept at %s\n", directory);
        return 1;
    }
    if (MakePath(example, directory, "a3_test_file", 9) != 0)
        return 1;
    if (printf("Mode: %s\nRun directory: %s\nSuccessful ordinary writes: 93\n"
               "Genuine denied attempts: %d\nAnalyze file: %s\n"
               "Analyzer command: ./audit_monitor -i %s\n",
               normal ? "normal" : "default", directory, denied_count,
               example, example) < 0 || fflush(stdout) != 0)
    {
        perror("final summary output");
        return 1;
    }
    return 0;
}
