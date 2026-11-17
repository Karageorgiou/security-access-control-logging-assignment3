#define _GNU_SOURCE

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

static int WriteAndReport(FILE *stream, const char *text, size_t size, size_t count)
{
    size_t completed;
    int saved;

    errno = E2BIG;
    completed = fwrite(text, size, count, stream);
    saved = errno;
    printf("write=%zu errno=%d\n", completed, saved);
    return 0;
}

static void CloseAndReport(FILE *stream)
{
    int result;
    int saved;

    errno = E2BIG;
    result = fclose(stream);
    saved = errno;
    printf("close=%d errno=%d\n", result, saved);
}

int main(int argc, char *argv[])
{
    FILE *first;
    FILE *second;
    int descriptor;

    if (argc < 3)
        return 2;
    if (strcmp(argv[1], "basic") == 0)
    {
        first = fopen(argv[2], "w+");
        if (first == NULL)
            return 3;
        WriteAndReport(first, "hello", 1, 5);
        CloseAndReport(first);
    }
    else if (strcmp(argv[1], "multi") == 0 && argc == 4)
    {
        first = fopen(argv[2], "w+");
        second = fopen(argv[3], "w+");
        if (first == NULL || second == NULL)
            return 4;
        WriteAndReport(first, "alpha", 1, 5);
        WriteAndReport(first, "x", 0, 5);
        WriteAndReport(second, "beta", 1, 4);
        WriteAndReport(first, "alpha", 1, 5);
        CloseAndReport(second);
        CloseAndReport(first);
    }
    else if (strcmp(argv[1], "unregistered") == 0)
    {
        descriptor = open(argv[2], O_CREAT | O_TRUNC | O_WRONLY, 0600);
        if (descriptor < 0)
            return 5;
        first = fdopen(descriptor, "w");
        if (first == NULL)
        {
            close(descriptor);
            return 6;
        }
        WriteAndReport(first, "orphan", 1, 6);
        CloseAndReport(first);
    }
    else if (strcmp(argv[1], "reassociate") == 0 && argc == 4)
    {
        first = fopen(argv[2], "w+");
        if (first == NULL)
            return 7;
        if (freopen(argv[3], "w+", first) == NULL)
            return 8;
        WriteAndReport(first, "newfile", 1, 7);
        CloseAndReport(first);
    }
    else if (strcmp(argv[1], "reuse") == 0 && argc == 4)
    {
        first = fopen(argv[2], "w+");
        if (first == NULL)
            return 9;
        CloseAndReport(first);
        second = fopen(argv[3], "w+");
        if (second == NULL)
            return 10;
        WriteAndReport(second, "newfile", 1, 7);
        CloseAndReport(second);
    }
    else if (strcmp(argv[1], "failed-write") == 0)
    {
        first = fopen("/dev/full", "w");
        if (first == NULL || setvbuf(first, NULL, _IONBF, 0) != 0)
            return 11;
        WriteAndReport(first, "hello", 1, 5);
        CloseAndReport(first);
    }
    else if (strcmp(argv[1], "failed-close") == 0)
    {
        first = fopen("/dev/full", "w");
        if (first == NULL)
            return 12;
        WriteAndReport(first, "hello", 1, 5);
        CloseAndReport(first);
    }
    else if (strcmp(argv[1], "stdout") == 0)
    {
        WriteAndReport(stdout, "x", 1, 1);
    }
    else
    {
        return 13;
    }
    printf("pid=%ld\n", (long)getpid());
    return 0;
}
