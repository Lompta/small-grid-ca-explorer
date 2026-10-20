// sample_runs.cpp
//
// Estimate how much work a brute-force search would take for an n x n torus
// (n <= 8) by sampling random start configurations for every rule.
//
// For each of the 256 rules searched (one per complement pair), it runs
// SAMPLES random starts, measures each run (unique states = tail + cycle)
// exactly with Brent's cycle detection, and reports:
//   - mean run length and mean simulation steps per start (the cost of brute force)
//   - the longest run found (a lower bound on the true answer)
//
// Usage: sample_runs N SAMPLES [seed]

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <vector>
#include <omp.h>

typedef uint64_t u64;
typedef uint32_t u32;

static int N, CELLS;
static u64 CELLMASK, COL0, COLLAST;

static inline u64 vrot(u64 x, int s) {
    if (s == 0) return x;
    int k = s * N;
    return ((x << k) | (x >> (CELLS - k))) & CELLMASK;
}

static inline u64 step(u64 x, u32 rule) {
    u64 e = ((x >> 1) & ~COLLAST) | ((x << (N - 1)) & COLLAST);
    u64 w = ((x << 1) & ~COL0 & CELLMASK) | ((x >> (N - 1)) & COL0);
    u64 nb[8] = {e, w, vrot(x, 1), vrot(x, N - 1), vrot(e, 1), vrot(e, N - 1),
                 vrot(w, 1), vrot(w, N - 1)};
    u64 b0 = 0, b1 = 0, b2 = 0, b3 = 0;
    for (int k = 0; k < 8; k++) {
        u64 c0 = b0 & nb[k]; b0 ^= nb[k];
        u64 c1 = b1 & c0;    b1 ^= c0;
        u64 c2 = b2 & c1;    b2 ^= c1;
        b3 |= c2;
    }
    u64 out = 0;
    for (int k = 0; k <= 8; k++)
        if (rule >> k & 1)
            out |= ((k & 1) ? b0 : ~b0) & ((k & 2) ? b1 : ~b1) &
                   ((k & 4) ? b2 : ~b2) & ((k & 8) ? b3 : ~b3);
    return out & CELLMASK;
}

static inline u64 splitmix(u64& s) {
    u64 z = (s += 0x9E3779B97F4A7C15ull);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
    return z ^ (z >> 31);
}

// Brent's algorithm: returns tail + cycle length; adds steps taken to *cost.
static inline u64 run_length(u64 x0, u32 rule, u64* cost) {
    u64 power = 1, lam = 1, t = x0, h = step(x0, rule), steps = 1;
    while (t != h) {
        if (power == lam) { t = h; power *= 2; lam = 0; }
        h = step(h, rule); lam++; steps++;
    }
    t = h = x0;
    for (u64 i = 0; i < lam; i++) h = step(h, rule);
    u64 mu = 0;
    while (t != h) { t = step(t, rule); h = step(h, rule); mu++; }
    *cost += steps + lam + 2 * mu;
    return mu + lam;
}

int main(int argc, char** argv) {
    if (argc < 3) { fprintf(stderr, "usage: sample_runs N SAMPLES [seed]\n"); return 1; }
    N = atoi(argv[1]);
    long long samples = atoll(argv[2]);
    u64 seed = argc > 3 ? strtoull(argv[3], nullptr, 0) : 12345;
    CELLS = N * N;
    CELLMASK = CELLS == 64 ? ~0ull : ((1ull << CELLS) - 1);
    COL0 = COLLAST = 0;
    for (int r = 0; r < N; r++) { COL0 |= 1ull << (r * N); COLLAST |= 1ull << (r * N + N - 1); }

    double classes = std::ldexp(1.0, CELLS) / (8.0 * CELLS);  // ~ number of symmetry classes
    double total_steps_per_class = 0, total_wall = 0;
    u64 best_run = 0; u32 best_rule = 0; u64 best_start = 0;
    printf("rule,mean_run,mean_steps,max_run,max_start_hex,seconds\n");
    for (u32 rule = 0; rule < 512; rule++) {
        if (rule >> 4 & 1) continue;
        auto t0 = std::chrono::steady_clock::now();
        double sum_run = 0, sum_cost = 0;
        u64 mx = 0, mx_start = 0;
#pragma omp parallel
        {
            u64 s = seed ^ ((u64)rule << 32) ^ ((u64)omp_get_thread_num() * 0x1234567ull);
            double lr = 0; u64 lc = 0, lmx = 0, lst = 0;
#pragma omp for schedule(dynamic, 64)
            for (long long i = 0; i < samples; i++) {
                u64 x = splitmix(s) & CELLMASK;
                u64 r = run_length(x, rule, &lc);
                lr += (double)r;
                if (r > lmx) { lmx = r; lst = x; }
            }
#pragma omp critical
            {
                sum_run += lr; sum_cost += (double)lc;
                if (lmx > mx) { mx = lmx; mx_start = lst; }
            }
        }
        double sec = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
        total_wall += sec;
        total_steps_per_class += sum_cost / samples;
        if (mx > best_run) { best_run = mx; best_rule = rule; best_start = mx_start; }
        printf("%u,%.1f,%.1f,%llu,%llx,%.2f\n", rule, sum_run / samples, sum_cost / samples,
               (unsigned long long)mx, (unsigned long long)mx_start, sec);
        fflush(stdout);
    }
    double total_steps = classes * total_steps_per_class;
    double rate = (double)samples * 256 / total_wall;  // starts per second, all rules
    printf("# %dx%d: ~%.3g symmetry classes; mean brute-force steps per class summed over rules = %.0f\n",
           N, N, classes, total_steps_per_class);
    printf("# estimated total steps for exhaustive brute force: %.3g\n", total_steps);
    printf("# this machine (CPU, %d threads): %.3g steps/s -> ~%.1f days\n", omp_get_max_threads(),
           total_steps_per_class * samples / total_wall, total_steps / (total_steps_per_class * samples / total_wall) / 86400);
    printf("# longest run sampled: %llu (rule %u, start %llx)\n", (unsigned long long)best_run, best_rule,
           (unsigned long long)best_start);
    (void)rate;
    return 0;
}
