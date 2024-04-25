#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <errno.h>

#include "branch.h"

#include <error.h>
#include <linux/perf_event.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid,
			    int cpu, int group_fd, unsigned long flags)
{
	int ret = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd,
			  flags);
	return ret;
}

/* Notice: the layout of this struct depends on the flags passed to perf_event_open. */
struct read_format {
	uint64_t nr;
	struct {
		uint64_t value;
	} values[];
};

struct events {
	uint32_t type;
	uint32_t config;
	char *name;
};

struct events events[] = {
	{ PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, "cycles" },
	{ PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, "instructions" },
	{ PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_MISSES, "missed_branches" },
	// the following don't work on arm64
	{ PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_INSTRUCTIONS, "branches" },
};

#define ARRAY_SIZE(array) (sizeof(array) / sizeof(array[0]))
#define EVENTS_SZ ((int)ARRAY_SIZE(events))

void perf_open(struct perf *perf, int raw_counter)
{
	if (ARRAY_SIZE(perf->fd) < EVENTS_SZ) {
		abort();
	}

	perf->fd[0] = -1;
	int i;
	for (i = 0; i < EVENTS_SZ; i++) {
		struct perf_event_attr pe = {
			.type = events[i].type,
			.size = sizeof(struct perf_event_attr),
			.config = events[i].config,
			.disabled = 1,
			.exclude_kernel = 1,
			.exclude_guest = 1,
			.exclude_hv = 1,
			.read_format = PERF_FORMAT_GROUP,
			.sample_type = PERF_SAMPLE_IDENTIFIER,
		};
		if (i == 3 && raw_counter) {
			pe.type = PERF_TYPE_RAW;
			pe.config = raw_counter;
			events[i].name = "raw_counter";
		}
		perf->fd[i] = perf_event_open(&pe, 0, -1, perf->fd[0],
					      PERF_FLAG_FD_CLOEXEC);
		if (perf->fd[i] == -1) {
			// allow for branches/raw_counter to fail
			if (i == 3)
				continue;
			fprintf(stderr, "Error opening perf %s\n",
				events[i].name);
			exit(EXIT_FAILURE);
		}
	}
}

inline void perf_start(struct perf *perf)
{
	asm volatile("" ::: "memory");
	ioctl(perf->fd[0], PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
	ioctl(perf->fd[0], PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
	asm volatile("" ::: "memory");
}

inline void perf_stop(struct perf *perf, uint64_t *numbers)
{
	asm volatile("" ::: "memory");
	ioctl(perf->fd[0], PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
	char perf_buf[4096];
	int r = read(perf->fd[0], &perf_buf, sizeof(perf_buf));
	if (r < 1)
		error(-1, errno, "read(perf)");

	struct read_format *rf = (struct read_format *)perf_buf;
	switch (rf->nr) {
	case 4:
		numbers[1] = rf->values[3].value; // branches
		/* fallthrough */
	case 3:
		numbers[0] = rf->values[0].value; // cycles
		numbers[3] = rf->values[1].value; // instructions
		numbers[2] = rf->values[2].value; // missed_branches
		break;
	default:
		abort();
	}
}

