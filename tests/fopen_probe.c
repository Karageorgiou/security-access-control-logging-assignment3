#include <errno.h>
#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>

int main(int argc, char *argv[])
{
    FILE *file;
    int result_errno;

    if (argc != 3)
    {
        fprintf(stderr, "Usage: %s path mode\n", argv[0]);
        return 2;
    }

    errno = E2BIG;
    file = fopen(argv[1], argv[2]);
    result_errno = errno;
    printf("success=%d errno=%d pid=%ld\n", file != NULL, result_errno, (long)getpid());
    if (file != NULL && fclose(file) != 0)
        return 3;
    return 0;
}
