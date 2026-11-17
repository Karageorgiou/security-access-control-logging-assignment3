#define _POSIX_C_SOURCE 200809L

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

static int MakePath(char *destination, size_t capacity, const char *directory,
                    const char *filename)
{
    int length = snprintf(destination, capacity, "%s/%s", directory, filename);
    return length < 0 || (size_t)length >= capacity ? -1 : 0;
}

static int WriteText(const char *path, const char *mode, const char *text)
{
    FILE *stream = fopen(path, mode);
    size_t length = strlen(text);
    int failed = 0;

    if (stream == NULL)
    {
        perror(path);
        return -1;
    }
    if (fwrite(text, 1, length, stream) != length)
    {
        fprintf(stderr, "Failed to write %s\n", path);
        failed = 1;
    }
    if (fclose(stream) != 0)
    {
        perror("fclose");
        failed = 1;
    }
    return failed ? -1 : 0;
}

static int ReadText(const char *path, const char *mode)
{
    FILE *stream = fopen(path, mode);
    int failed = 0;

    if (stream == NULL)
    {
        perror(path);
        return -1;
    }
    if (fgetc(stream) == EOF && ferror(stream))
        failed = 1;
    if (fclose(stream) != 0)
        failed = 1;
    if (failed)
        fprintf(stderr, "Failed to read or close %s\n", path);
    return failed ? -1 : 0;
}

static int CheckDeniedFiles(const char *directory)
{
    char path[4096];

    for (int index = 1; index <= 6; index++)
    {
        char filename[32];
        FILE *stream;
        int error;

        snprintf(filename, sizeof(filename), "denied_%d.txt", index);
        if (MakePath(path, sizeof(path), directory, filename) != 0 ||
            WriteText(path, "w", "not publicly readable\n") != 0 ||
            chmod(path, 0000) != 0)
            return -1;

        errno = 0;
        stream = fopen(path, "r");
        error = errno;
        if (stream != NULL)
            fclose(stream);

        // Restore permissions before removing our own temporary denial fixture.
        if (chmod(path, 0600) != 0 || unlink(path) != 0)
            return -1;
        if (stream != NULL || (error != EACCES && error != EPERM))
        {
            fprintf(stderr, "Expected a permission denial for %s (errno=%d)\n",
                    filename, error);
            return -1;
        }
    }
    return 0;
}

int main(void)
{
    char directory[] = "/tmp/a3-assignment-XXXXXX";
    char example[4096];
    char notes[4096];
    char activity[4096];
    int failed = 0;

    if (geteuid() == 0)
    {
        fprintf(stderr, "Run test_audit as an ordinary non-root user.\n");
        return 1;
    }

    if (mkdtemp(directory) == NULL)
    {
        perror("mkdtemp");
        return 1;
    }
    if (MakePath(example, sizeof(example), directory, "example.txt") != 0 ||
        MakePath(notes, sizeof(notes), directory, "notes.txt") != 0 ||
        MakePath(activity, sizeof(activity), directory, "activity.txt") != 0)
        failed = 1;

    // Three distinct qualifying fwrite() calls on example.txt.
    if (!failed && (WriteText(example, "w+", "first line\n") != 0 ||
                    WriteText(example, "r+", "changed line\n") != 0 ||
                    ReadText(example, "r") != 0 ||
                    WriteText(example, "a", "appended line\n") != 0 ||
                    ReadText(example, "rb") != 0 ||
                    WriteText(notes, "w", "notes\n") != 0 ||
                    ReadText(notes, "r") != 0 ||
                    WriteText(activity, "w+", "activity\n") != 0 ||
                    WriteText(activity, "a", "later\n") != 0 ||
                    CheckDeniedFiles(directory) != 0))
        failed = 1;

    if (failed)
    {
        fprintf(stderr, "Audit demonstration failed. Temporary directory: %s\n",
                directory);
        return 1;
    }

    printf("DEMO_DIR=%s\n", directory);
    printf("ANALYZE_FILE=%s\n", example);
    printf("EXPECTED_MODIFICATIONS=3\n");
    printf("EXPECTED_DISTINCT_DENIALS=6\n");
    return 0;
}
