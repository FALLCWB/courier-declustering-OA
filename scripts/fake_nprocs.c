/* Report FAKE_NPROCS processors to a process (LD_PRELOAD), so that OpenBLAS starts the same number of threads as on
   FE-SIM-1. OpenBLAS caps its thread count at the processors it sees (min of sysconf and the affinity mask), and the
   values of a run depend on that count (DECISIONS.md, BLAS rule): on a 16-thread machine, OPENBLAS_NUM_THREADS=30 gives
   16 threads and other last digits. Only the count reported changes; no thread is bound to a processor.
   Build: gcc -O2 -shared -fPIC -o .venv/lib/fake_nprocs.so scripts/fake_nprocs.c -ldl
   Use:   LD_PRELOAD=.venv/lib/fake_nprocs.so FAKE_NPROCS=30 OPENBLAS_CORETYPE=Haswell python ... */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <sched.h>
#include <stdlib.h>
#include <sys/sysinfo.h>
#include <unistd.h>

static int fake(void) { const char *s = getenv("FAKE_NPROCS"); return s ? atoi(s) : 0; }

long sysconf(int name) {
    static long (*real)(int) = 0;
    if (!real) real = (long (*)(int))dlsym(RTLD_NEXT, "sysconf");
    int f = fake();
    if (f > 0 && (name == _SC_NPROCESSORS_CONF || name == _SC_NPROCESSORS_ONLN)) return f;
    return real(name);
}

int sched_getaffinity(pid_t pid, size_t size, cpu_set_t *mask) {
    static int (*real)(pid_t, size_t, cpu_set_t *) = 0;
    if (!real) real = (int (*)(pid_t, size_t, cpu_set_t *))dlsym(RTLD_NEXT, "sched_getaffinity");
    int r = real(pid, size, mask), f = fake();
    if (r == 0 && f > 0) { CPU_ZERO_S(size, mask); for (int i = 0; i < f; i++) CPU_SET_S(i, size, mask); }
    return r;
}

int get_nprocs(void) {
    static int (*real)(void) = 0;
    if (!real) real = (int (*)(void))dlsym(RTLD_NEXT, "get_nprocs");
    int f = fake();
    return f > 0 ? f : real();
}

int get_nprocs_conf(void) {
    static int (*real)(void) = 0;
    if (!real) real = (int (*)(void))dlsym(RTLD_NEXT, "get_nprocs_conf");
    int f = fake();
    return f > 0 ? f : real();
}
