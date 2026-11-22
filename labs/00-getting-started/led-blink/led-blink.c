#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

static volatile sig_atomic_t stopped;

static void stop(int signal_number)
{
    stopped = signal_number;
}

static int read_attribute(const char *path, char *buffer, size_t size)
{
    int fd = open(path, O_RDONLY);
    if (fd < 0)
        return -1;
    ssize_t length;
    do {
        length = read(fd, buffer, size - 1);
    } while (length < 0 && errno == EINTR);
    int saved_errno = errno;
    int result = close(fd);
    if (length < 0) {
        errno = saved_errno;
        return -1;
    }
    if (result < 0)
        return -1;
    if (length == 0 || (size_t)length == size - 1) {
        errno = EINVAL;
        return -1;
    }
    buffer[length] = '\0';
    buffer[strcspn(buffer, "\r\n")] = '\0';
    return 0;
}

static int write_attribute(const char *path, const char *value)
{
    int fd = open(path, O_WRONLY | O_TRUNC);
    if (fd < 0)
        return -1;
    ssize_t written;
    size_t length = strlen(value);
    do {
        written = write(fd, value, length);
    } while (written < 0 && errno == EINTR);
    int saved_errno = errno;
    int result = close(fd);
    if (written < 0) {
        errno = saved_errno;
        return -1;
    }
    if ((size_t)written != length) {
        errno = EIO;
        return -1;
    }
    return result;
}

static int number(const char *text, long minimum, long maximum, long *value)
{
    char *end;
    errno = 0;
    long parsed = strtol(text, &end, 10);
    if (errno || end == text || *end || parsed < minimum || parsed > maximum)
        return -1;
    *value = parsed;
    return 0;
}

static void pause_blink(void)
{
    struct timespec remaining = { .tv_sec = 0, .tv_nsec = 250000000 };
    while (!stopped && nanosleep(&remaining, &remaining) < 0 && errno == EINTR)
        ;
}

int main(int argc, char **argv)
{
    long cycles;
    if (argc != 3 || number(argv[2], 1, 1000000, &cycles) < 0) {
        fprintf(stderr, "Usage: %s LED_DIRECTORY CYCLES (1..1000000)\n", argv[0]);
        return 2;
    }
    char trigger_path[PATH_MAX], brightness_path[PATH_MAX], maximum_path[PATH_MAX];
    int a = snprintf(trigger_path, sizeof trigger_path, "%s/trigger", argv[1]);
    int b = snprintf(brightness_path, sizeof brightness_path, "%s/brightness", argv[1]);
    int c = snprintf(maximum_path, sizeof maximum_path, "%s/max_brightness", argv[1]);
    if (a < 0 || b < 0 || c < 0 || (size_t)a >= sizeof trigger_path ||
        (size_t)b >= sizeof brightness_path || (size_t)c >= sizeof maximum_path) {
        fprintf(stderr, "LED directory path is too long\n");
        return 2;
    }
    char triggers[4096], original_brightness[32], maximum[32];
    if (read_attribute(trigger_path, triggers, sizeof triggers) < 0 ||
        read_attribute(brightness_path, original_brightness, sizeof original_brightness) < 0 ||
        read_attribute(maximum_path, maximum, sizeof maximum) < 0) {
        perror("Read LED attributes");
        return 1;
    }
    char *original_trigger = strchr(triggers, '[');
    char *end = original_trigger ? strchr(original_trigger, ']') : NULL;
    long original_value, maximum_value;
    if (!end || number(maximum, 1, INT_MAX, &maximum_value) < 0 ||
        number(original_brightness, 0, maximum_value, &original_value) < 0) {
        fprintf(stderr, "Invalid LED attributes\n");
        return 1;
    }
    *end = '\0';
    ++original_trigger;
    struct sigaction action = { .sa_handler = stop };
    sigemptyset(&action.sa_mask);
    if (sigaction(SIGINT, &action, NULL) < 0 || sigaction(SIGTERM, &action, NULL) < 0) {
        perror("Install signal handler");
        return 1;
    }
    if (write_attribute(trigger_path, "none") < 0) {
        perror("Disable LED trigger");
        return 1;
    }
    int result = 0;
    for (long i = 0; i < cycles && !stopped; ++i) {
        if (write_attribute(brightness_path, maximum) < 0) {
            perror("Turn LED on");
            result = 1;
            break;
        }
        pause_blink();
        if (write_attribute(brightness_path, "0") < 0) {
            perror("Turn LED off");
            result = 1;
            break;
        }
        pause_blink();
    }
    /* Brightness first: writing zero can otherwise disable a restored trigger. */
    if (write_attribute(brightness_path, original_brightness) < 0) {
        perror("Restore brightness");
        result = 1;
    }
    if (write_attribute(trigger_path, original_trigger) < 0) {
        perror("Restore trigger");
        result = 1;
    }
    return result ? result : (stopped ? 128 + stopped : 0);
}
