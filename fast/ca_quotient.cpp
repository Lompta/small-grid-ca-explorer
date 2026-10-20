// ca_quotient.cpp
//
// Exact solver for the "longest run of unique states" problem on an n x n
// wraparound (toroidal) grid, for n <= 6.
//
// Problem recap
// -------------
// Each cell looks at its 8 Moore neighbours (NOT itself). A rule is a 9-bit
// mask: bit k set means "a cell with exactly k live neighbours is alive next
// step". For a start configuration x, the answer for x is the number of
// distinct states seen before the first repeat (start counts; the repeat does
// not). We want the maximum over all 512 rules and all 2^(n*n) starts.
//
// Method (why this is fast enough for 6x6)
// ----------------------------------------
// Simulating every start from scratch is hopeless for 6x6: chaotic rules have
// trajectories tens of thousands of steps long, times 2^36 starts. Instead,
// for each rule we build the whole state-transition graph once and read off
// the answer from its structure:
//
// 1. Symmetry quotient. The update commutes with the 288 symmetries of the
//    6x6 torus (36 translations x 8 rotations/reflections). So we work on
//    orbit representatives ("canonical" = numerically smallest image). There
//    are ~2.4e8 orbits for 6x6 instead of 6.9e10 states. Each orbit gets an
//    index; succ[i] = index of canon(step(rep[i])).
//
// 2. Tails are preserved exactly. If x's orbit reaches a cycle of the quotient
//    graph after mu steps, then x itself is on a cycle of the real graph after
//    mu steps (the shifted copy it returns to must eventually return to
//    itself). So the tail length is the same in both graphs; only the cycle
//    length can grow (by the order of the symmetry relating a cycle state to
//    its later copy). We get the true cycle length by simulating one lap of
//    the real dynamics from a cycle representative.
//
// 3. Longest tail via Kahn's algorithm. Repeatedly peeling nodes with no
//    remaining predecessors gives every non-cycle node its height (longest
//    chain of predecessors behind it); the nodes left over are exactly the
//    cycle nodes. The longest tail into a cycle is max(height(pred)+1) over
//    its non-cycle predecessors, and the longest run for that cycle is
//    longest tail + true cycle length.
//
// 4. Complement symmetry. Inverting both the start and the rule
//    (rule' has k iff rule lacks 8-k) gives an inverted copy of the same run.
//    Exactly one rule of each such pair lacks k=4, so only those 256 rules are
//    searched.
//
// Usage
//   ca_quotient N                       all 256 rules (appends results_N.csv)
//   ca_quotient N first last            rules with mask in [first,last]
//   ca_quotient N --reconstruct RULE    rebuild the longest run for RULE,
//                                       verify it by direct simulation and
//                                       write it to longest_N_rule_RULE.txt
//   ca_quotient N --count-orbits        just enumerate orbits and check Burnside

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <string>
#include <unordered_set>
#include <vector>
#include <omp.h>

typedef uint64_t u64;
typedef uint32_t u32;

// ---------------------------------------------------------------------------
// Grid geometry. Cell (r, c) is bit r*N + c. Row N-1 is the most significant
// row, so "numerically smallest" prefers a small top row first.
// ---------------------------------------------------------------------------
static int N, CELLS, NCHUNK;
static u64 CELLMASK, ROWMASK, COL0, COLLAST;
static u64 HROT_HI[8], HROT_LO[8];   // masks for rotating every row by j
static u64 DIH_LUT[8][5][256];       // 8 rotations/reflections, by input byte
static uint8_t MIN_ROT[64];          // min over cyclic rotations of a row
static uint8_t MIN_ROT_REV[64];      // ... and also over reversal
static uint8_t ROTS_TO_MIN[64];      // bitmask of rotations j giving MIN_ROT

static inline u64 vrot(u64 x, int s) {  // move row r to row r+s (mod N)
    if (s == 0) return x;
    int k = s * N;
    return ((x << k) | (x >> (CELLS - k))) & CELLMASK;
}
static inline u64 hrot(u64 x, int j) {  // move column c to column c+j (mod N)
    if (j == 0) return x;
    return ((x << j) & HROT_HI[j]) | ((x >> (N - j)) & HROT_LO[j]);
}
static inline u32 rot_row(u32 v, int j) {
    u32 m = (1u << N) - 1;
    return j == 0 ? v : (((v << j) | (v >> (N - j))) & m);
}
static inline u32 rev_row(u32 v) {
    u32 o = 0;
    for (int c = 0; c < N; c++) if (v >> c & 1) o |= 1u << (N - 1 - c);
    return o;
}
static inline u64 dih(int d, u64 x) {
    u64 o = 0;
    for (int k = 0; k < NCHUNK; k++) o |= DIH_LUT[d][k][(x >> (8 * k)) & 255];
    return o;
}

static void init_geometry(int n) {
    N = n;
    CELLS = n * n;
    NCHUNK = (CELLS + 7) / 8;
    CELLMASK = (CELLS == 64) ? ~0ull : ((1ull << CELLS) - 1);
    ROWMASK = (1ull << N) - 1;
    COL0 = COLLAST = 0;
    for (int r = 0; r < N; r++) {
        COL0 |= 1ull << (r * N);
        COLLAST |= 1ull << (r * N + N - 1);
    }
    for (int j = 0; j < N; j++) {
        HROT_HI[j] = HROT_LO[j] = 0;
        for (int r = 0; r < N; r++)
            for (int c = 0; c < N; c++)
                (c >= j ? HROT_HI[j] : HROT_LO[j]) |= 1ull << (r * N + c);
    }
    // Dihedral transforms: optional transpose, then optional row/column flips.
    memset(DIH_LUT, 0, sizeof(DIH_LUT));
    for (int d = 0; d < 8; d++) {
        int perm[64];
        for (int r = 0; r < N; r++)
            for (int c = 0; c < N; c++) {
                int rr = r, cc = c;
                if (d & 4) std::swap(rr, cc);
                if (d & 1) rr = N - 1 - rr;
                if (d & 2) cc = N - 1 - cc;
                perm[r * N + c] = rr * N + cc;
            }
        for (int k = 0; k < NCHUNK; k++)
            for (int b = 0; b < 256; b++) {
                u64 o = 0;
                for (int t = 0; t < 8; t++) {
                    int i = 8 * k + t;
                    if ((b >> t & 1) && i < CELLS) o |= 1ull << perm[i];
                }
                DIH_LUT[d][k][b] = o;
            }
    }
    for (u32 v = 0; v < (1u << N); v++) {
        u32 m = v, mask = 0;
        for (int j = 0; j < N; j++) m = std::min(m, rot_row(v, j));
        for (int j = 0; j < N; j++) if (rot_row(v, j) == m) mask |= 1u << j;
        MIN_ROT[v] = (uint8_t)m;
        ROTS_TO_MIN[v] = (uint8_t)mask;
        u32 rv = rev_row(v), mr = m;
        for (int j = 0; j < N; j++) mr = std::min(mr, rot_row(rv, j));
        MIN_ROT_REV[v] = (uint8_t)mr;
    }
}

// ---------------------------------------------------------------------------
// One CA step for all cells at once (bit-parallel within a 64-bit word).
// ---------------------------------------------------------------------------
static inline u64 step(u64 x, u32 rule) {
    u64 e = ((x >> 1) & ~COLLAST) | ((x << (N - 1)) & COLLAST);   // value of (r, c+1)
    u64 w = ((x << 1) & ~COL0 & CELLMASK) | ((x >> (N - 1)) & COL0); // value of (r, c-1)
    u64 nb[8] = {e, w, vrot(x, 1), vrot(x, N - 1), vrot(e, 1), vrot(e, N - 1),
                 vrot(w, 1), vrot(w, N - 1)};
    // Bit-sliced counter: (b3 b2 b1 b0) = number of live neighbours per cell.
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

// ---------------------------------------------------------------------------
// Canonical form: smallest integer among all 8*N*N symmetric images.
// The top row of the winner must be the smallest rotation of some row of some
// dihedral image, so only those few (image, row, rotation) combos are tried.
// ---------------------------------------------------------------------------
static inline u64 canon(u64 y) {
    u64 z[8];
    u32 m = 255;
    for (int d = 0; d < 8; d++) {
        z[d] = dih(d, y);
        for (int r = 0; r < N; r++) m = std::min<u32>(m, MIN_ROT[(z[d] >> (r * N)) & ROWMASK]);
    }
    u64 best = ~0ull;
    for (int d = 0; d < 8; d++)
        for (int r = 0; r < N; r++) {
            u32 v = (u32)((z[d] >> (r * N)) & ROWMASK);
            if (MIN_ROT[v] != m) continue;
            u64 t = vrot(z[d], N - 1 - r);
            for (u32 mask = ROTS_TO_MIN[v]; mask; mask &= mask - 1) {
                int j = 0;
                while (!(mask >> j & 1)) j++;
                best = std::min(best, hrot(t, j));
            }
        }
    return best;
}

// ---------------------------------------------------------------------------
// Burnside count of orbits, as an independent check on the enumeration.
// ---------------------------------------------------------------------------
static double burnside_orbits() {
    double total = 0;
    for (int d = 0; d < 8; d++)
        for (int s = 0; s < N; s++)
            for (int j = 0; j < N; j++) {
                int perm[64];
                for (int i = 0; i < CELLS; i++) {
                    u64 img = hrot(vrot(dih(d, 1ull << i), s), j);
                    int p = 0;
                    while (!(img >> p & 1)) p++;
                    perm[i] = p;
                }
                bool seen[64] = {};
                int cycles = 0;
                for (int i = 0; i < CELLS; i++) {
                    if (seen[i]) continue;
                    cycles++;
                    for (int k = i; !seen[k]; k = perm[k]) seen[k] = true;
                }
                total += std::ldexp(1.0, cycles);
            }
    return total / (8.0 * N * N);
}

// ---------------------------------------------------------------------------
// Enumerate all canonical representatives in increasing order.
// Pruning: a canonical x has top row v with v == MIN_ROT_REV[v], and every row
// and column w of x has MIN_ROT_REV[w] >= v.
// ---------------------------------------------------------------------------
static std::vector<u64> enumerate_reps() {
    struct Task { u32 v, a; };
    std::vector<Task> tasks;
    std::vector<std::vector<u32>> W(1u << N);
    for (u32 v = 0; v < (1u << N); v++) {
        if (MIN_ROT_REV[v] != v) continue;
        for (u32 w = 0; w < (1u << N); w++) if (MIN_ROT_REV[w] >= v) W[v].push_back(w);
        for (u32 a : W[v]) tasks.push_back({v, a});
    }
    std::vector<std::vector<u64>> out(tasks.size());
    const int lower = N - 2;  // rows N-3 .. 0 enumerated by odometer
#pragma omp parallel for schedule(dynamic, 1)
    for (long long t = 0; t < (long long)tasks.size(); t++) {
        u32 v = tasks[t].v;
        const std::vector<u32>& Wv = W[v];
        u64 head = ((u64)v << ((N - 1) * N)) | ((u64)tasks[t].a << ((N - 2) * N));
        std::vector<size_t> idx(lower, 0);
        for (;;) {
            u64 x = head;
            for (int k = 0; k < lower; k++) x |= (u64)Wv[idx[k]] << ((lower - 1 - k) * N);
            // column check via the transpose image
            u64 tx = dih(4, x);
            bool ok = true;
            for (int r = 0; r < N && ok; r++) ok = MIN_ROT_REV[(tx >> (r * N)) & ROWMASK] >= v;
            if (ok && canon(x) == x) out[t].push_back(x);
            int k = lower - 1;
            while (k >= 0 && ++idx[k] == Wv.size()) idx[k--] = 0;
            if (k < 0) break;
        }
    }
    size_t total = 0;
    for (auto& o : out) total += o.size();
    std::vector<u64> reps;
    reps.reserve(total);
    for (auto& o : out) { reps.insert(reps.end(), o.begin(), o.end()); std::vector<u64>().swap(o); }
    return reps;
}

// ---------------------------------------------------------------------------
// Lookup from canonical config to its index: bucket on the top bits, then
// binary search within the bucket.
// ---------------------------------------------------------------------------
struct Index {
    const std::vector<u64>* reps;
    std::vector<u32> start;
    int shift;
    void build(const std::vector<u64>& r) {
        reps = &r;
        int B = std::min(24, CELLS);
        shift = CELLS - B;
        start.assign((1u << B) + 1, 0);
        size_t i = 0;
        for (u64 k = 0; k <= (1ull << B); k++) {
            while (i < r.size() && (r[i] >> shift) < k) i++;
            start[k] = (u32)i;
        }
    }
    inline u32 find(u64 x) const {
        u64 k = x >> shift;
        const u64* b = reps->data();
        const u64* p = std::lower_bound(b + start[k], b + start[k + 1], x);
        if (p == b + start[k + 1] || *p != x) {
            fprintf(stderr, "lookup failed for %llx\n", (unsigned long long)x);
            exit(1);
        }
        return (u32)(p - b);
    }
};

// Length of the real (non-quotient) cycle through configuration x.
static u64 true_cycle_length(u64 x, u32 rule, u64 cap) {
    u64 y = step(x, rule), n = 1;
    while (y != x) {
        y = step(y, rule);
        if (++n > cap) { fprintf(stderr, "cycle length cap exceeded\n"); exit(1); }
    }
    return n;
}

struct RuleResult {
    u32 rule;
    u64 best_run;        // longest run of unique states
    u64 best_tail;       // tail length of that run
    u64 best_cycle;      // true cycle length of that run
    u32 best_cycle_id;
    u64 cycle_nodes;     // orbits lying on cycles
    u64 num_cycles;      // cycles in the quotient graph
    u32 max_height;      // deepest tail in the whole graph
    double seconds;
};

// Working memory reused across rules.
struct Work {
    std::vector<u32> succ, h;
    std::atomic<u32>* indeg = nullptr;
    std::vector<u32> cur, nxt;
    std::vector<u32> cycle_rep;      // a node on each cycle
    std::vector<u64> cycle_len;      // true cycle length
};

static const u32 UNSET = 0xFFFFFFFFu;

static RuleResult solve_rule(u32 rule, const std::vector<u64>& reps, const Index& index, Work& wk) {
    auto t0 = std::chrono::steady_clock::now();
    const long long M = (long long)reps.size();
    RuleResult res = {};
    res.rule = rule;

    // 1. successor of every orbit + in-degrees
#pragma omp parallel for schedule(static)
    for (long long i = 0; i < M; i++) {
        wk.indeg[i].store(0, std::memory_order_relaxed);
        wk.h[i] = UNSET;
    }
#pragma omp parallel for schedule(dynamic, 65536)
    for (long long i = 0; i < M; i++) {
        u32 s = index.find(canon(step(reps[i], rule)));
        wk.succ[i] = s;
        wk.indeg[s].fetch_add(1, std::memory_order_relaxed);
    }

    // 2. Kahn peeling, one level at a time; a node's level is its height.
    size_t ncur = 0;
    {
        int T = omp_get_max_threads();
        std::vector<std::vector<u32>> loc(T);
#pragma omp parallel
        {
            auto& L = loc[omp_get_thread_num()];
#pragma omp for schedule(static)
            for (long long i = 0; i < M; i++)
                if (wk.indeg[i].load(std::memory_order_relaxed) == 0) { L.push_back((u32)i); wk.h[i] = 0; }
        }
        for (auto& L : loc) { memcpy(&wk.cur[ncur], L.data(), L.size() * 4); ncur += L.size(); }
    }
    u32 level = 0;
    u64 peeled = 0;
    while (ncur) {
        peeled += ncur;
        size_t nnext = 0;
        if (ncur < 4096) {
            for (size_t q = 0; q < ncur; q++) {
                u32 v = wk.succ[wk.cur[q]];
                if (wk.indeg[v].fetch_sub(1, std::memory_order_relaxed) == 1) { wk.h[v] = level + 1; wk.nxt[nnext++] = v; }
            }
        } else {
            std::atomic<size_t> pos(0);
#pragma omp parallel
            {
                std::vector<u32> L;
#pragma omp for schedule(static)
                for (long long q = 0; q < (long long)ncur; q++) {
                    u32 v = wk.succ[wk.cur[q]];
                    if (wk.indeg[v].fetch_sub(1, std::memory_order_relaxed) == 1) { wk.h[v] = level + 1; L.push_back(v); }
                }
                size_t at = pos.fetch_add(L.size());
                if (!L.empty()) memcpy(&wk.nxt[at], L.data(), L.size() * 4);
            }
            nnext = pos.load();
        }
        std::swap(wk.cur, wk.nxt);
        ncur = nnext;
        if (ncur) level++;
    }
    res.max_height = level;
    res.cycle_nodes = (u64)M - peeled;

    // 3. label cycles (cycle nodes still have indeg > 0); store cycle id in h
    wk.cycle_rep.clear();
    wk.cycle_len.clear();
    for (long long i = 0; i < M; i++) {
        if (wk.indeg[i].load(std::memory_order_relaxed) == 0 || wk.h[i] != UNSET) continue;
        u32 id = (u32)wk.cycle_rep.size();
        u64 p = 0;
        u32 c = (u32)i;
        do { wk.h[c] = id; c = wk.succ[c]; p++; } while (c != (u32)i);
        wk.cycle_rep.push_back((u32)i);
        wk.cycle_len.push_back(true_cycle_length(reps[i], rule, p * 8 * N * N));
    }
    res.num_cycles = wk.cycle_rep.size();

    // 4. longest tail into each cycle
    std::vector<std::atomic<u32>> tail(wk.cycle_rep.size());
    for (auto& t : tail) t.store(0);
#pragma omp parallel for schedule(static)
    for (long long u = 0; u < M; u++) {
        if (wk.indeg[u].load(std::memory_order_relaxed) != 0) continue;  // u on a cycle
        u32 v = wk.succ[u];
        if (wk.indeg[v].load(std::memory_order_relaxed) == 0) continue;  // v not on a cycle
        u32 cid = wk.h[v], cand = wk.h[u] + 1;
        u32 old = tail[cid].load(std::memory_order_relaxed);
        while (cand > old && !tail[cid].compare_exchange_weak(old, cand)) {}
    }
    for (size_t c = 0; c < tail.size(); c++) {
        u64 run = (u64)tail[c].load() + wk.cycle_len[c];
        if (run > res.best_run) {
            res.best_run = run;
            res.best_tail = tail[c].load();
            res.best_cycle = wk.cycle_len[c];
            res.best_cycle_id = (u32)c;
        }
    }
    res.seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    return res;
}

static std::string rule_str(u32 rule) {
    std::string s = "{";
    for (int k = 0; k <= 8; k++)
        if (rule >> k & 1) { if (s.size() > 1) s += ","; s += std::to_string(k); }
    return s + "}";
}

static std::string grid_str(u64 x) {
    std::string s;
    for (int r = N - 1; r >= 0; r--) {
        for (int c = 0; c < N; c++) s += (x >> (r * N + c) & 1) ? '#' : '.';
        s += '\n';
    }
    return s;
}

// Count unique states by plain simulation (independent of the graph logic).
static u64 direct_run_length(u64 x, u32 rule) {
    std::unordered_set<u64> seen;
    while (seen.insert(x).second) x = step(x, rule);
    return seen.size();
}

int main(int argc, char** argv) {
    if (argc < 2) { fprintf(stderr, "usage: ca_quotient N [first last | --reconstruct RULE | --count-orbits]\n"); return 1; }
    int n = atoi(argv[1]);
    if (n < 3 || n > 6) { fprintf(stderr, "N must be 3..6\n"); return 1; }
    init_geometry(n);

    auto t0 = std::chrono::steady_clock::now();
    std::vector<u64> reps = enumerate_reps();
    double bs = burnside_orbits();
    double te = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    printf("%dx%d: %zu orbit representatives (Burnside: %.0f) in %.1fs\n", N, N, reps.size(), bs, te);
    if ((double)reps.size() != bs) { fprintf(stderr, "orbit count mismatch!\n"); return 1; }
    if (argc >= 3 && !strcmp(argv[2], "--count-orbits")) return 0;

    Index index;
    index.build(reps);
    Work wk;
    size_t M = reps.size();
    wk.succ.resize(M);
    wk.h.resize(M);
    wk.cur.resize(M);
    wk.nxt.resize(M);
    wk.indeg = new std::atomic<u32>[M];

    if (argc >= 4 && !strcmp(argv[2], "--count")) {
        // How many starts (up to symmetry) reach the rule's longest run, and
        // how soon do their paths merge?
        u32 rule = (u32)strtoul(argv[3], nullptr, 0);
        RuleResult r = solve_rule(rule, reps, index, wk);
        printf("rule %u %s: longest run %llu\n", rule, rule_str(rule).c_str(), (unsigned long long)r.best_run);
        // Distance to cycle (d) and cycle id (cyc) for every orbit, by memoized forward walks.
        u32* d = wk.cur.data();
        u32* cyc = wk.nxt.data();
        for (size_t i = 0; i < M; i++) {
            bool on_cycle = wk.indeg[i].load(std::memory_order_relaxed) != 0;
            d[i] = on_cycle ? 0 : UNSET;
            cyc[i] = on_cycle ? wk.h[i] : UNSET;
        }
        std::vector<u32> stack;
        for (size_t i = 0; i < M; i++) {
            u32 u = (u32)i;
            while (d[u] == UNSET) { stack.push_back(u); u = wk.succ[u]; }
            while (!stack.empty()) {
                u32 v = stack.back(); stack.pop_back();
                d[v] = d[wk.succ[v]] + 1;
                cyc[v] = cyc[wk.succ[v]];
            }
        }
        std::vector<u32> best;
        std::vector<u32> best_cycles;
        for (size_t i = 0; i < M; i++)
            if (d[i] + wk.cycle_len[cyc[i]] == r.best_run) {
                best.push_back((u32)i);
                if (std::find(best_cycles.begin(), best_cycles.end(), cyc[i]) == best_cycles.end())
                    best_cycles.push_back(cyc[i]);
            }
        // Raw configuration count: orbit size = group order / stabilizer size.
        u64 configs = 0;
        for (u32 i : best) {
            u64 x = reps[i];
            int stab = 0;
            for (int g = 0; g < 8; g++)
                for (int s = 0; s < N; s++)
                    for (int j = 0; j < N; j++) stab += hrot(vrot(dih(g, x), s), j) == x;
            configs += (u64)(8 * N * N / stab);
        }
        printf("%zu start(s) up to symmetry (%llu raw configurations), ending in %zu distinct cycle(s)\n",
               best.size(), (unsigned long long)configs, best_cycles.size());
        for (u32 i : best)
            printf("\nstart hex %llx (tail %u), direct check %llu:\n%s", (unsigned long long)reps[i], d[i],
                   (unsigned long long)direct_run_length(reps[i], rule), grid_str(reps[i]).c_str());
        // Follow all best starts forward together and report when they merge.
        std::vector<u32> S = best;
        for (u32 k = 1; S.size() > 1; k++) {
            for (auto& u : S) u = wk.succ[u];
            std::sort(S.begin(), S.end());
            S.erase(std::unique(S.begin(), S.end()), S.end());
            if (S.size() > 1 && k > r.best_run) break;
            printf("after step %u: %zu distinct path(s) up to symmetry\n", k, S.size());
            if (S.size() == 1) break;
        }
        return 0;
    }

    if (argc >= 4 && !strcmp(argv[2], "--reconstruct")) {
        u32 rule = (u32)strtoul(argv[3], nullptr, 0);
        RuleResult r = solve_rule(rule, reps, index, wk);
        printf("rule %u %s: longest run %llu (tail %llu + cycle %llu)\n", rule, rule_str(rule).c_str(),
               (unsigned long long)r.best_run, (unsigned long long)r.best_tail, (unsigned long long)r.best_cycle);
        // Walk back from the cycle along heights to a start with the longest tail.
        u32 cid = r.best_cycle_id;
        u32 u = wk.cycle_rep[cid];
        if (r.best_tail > 0) {
            long long found = -1;
#pragma omp parallel for
            for (long long i = 0; i < (long long)M; i++)
                if (wk.indeg[i].load() == 0 && wk.indeg[wk.succ[i]].load() != 0 && wk.h[wk.succ[i]] == cid &&
                    wk.h[i] + 1 == r.best_tail)
                    found = i;
            u = (u32)found;
            while (wk.h[u] > 0) {
                u32 want = wk.h[u] - 1;
                long long prev = -1;
#pragma omp parallel for
                for (long long i = 0; i < (long long)M; i++)
                    if (wk.succ[i] == u && wk.indeg[i].load() == 0 && wk.h[i] == want) prev = i;
                u = (u32)prev;
            }
        }
        u64 start = reps[u];
        u64 direct = direct_run_length(start, rule);
        printf("start config (hex %llx), direct simulation gives %llu unique states -> %s\n",
               (unsigned long long)start, (unsigned long long)direct, direct == r.best_run ? "VERIFIED" : "MISMATCH");
        printf("%s", grid_str(start).c_str());
        char fn[128];
        snprintf(fn, sizeof fn, "longest_%dx%d_rule_%u.txt", N, N, rule);
        FILE* f = fopen(fn, "w");
        fprintf(f, "# %dx%d torus, rule %u = on with %s neighbours\n", N, N, rule, rule_str(rule).c_str());
        fprintf(f, "# unique states: %llu (tail %llu, cycle %llu); verified by direct simulation: %s\n",
                (unsigned long long)direct, (unsigned long long)r.best_tail, (unsigned long long)r.best_cycle,
                direct == r.best_run ? "yes" : "NO");
        fprintf(f, "# one state per line, hex, bit (r*N+c) = cell at row r, column c\n");
        u64 x = start;
        for (u64 s = 0; s <= direct; s++) { fprintf(f, "%llx\n", (unsigned long long)x); x = step(x, rule); }
        fclose(f);
        printf("wrote %s\n", fn);
        return direct == r.best_run ? 0 : 2;
    }

    u32 first = 0, last = 511;
    if (argc >= 4) { first = (u32)atoi(argv[2]); last = (u32)atoi(argv[3]); }
    char fn[64];
    snprintf(fn, sizeof fn, "results_%dx%d.csv", N, N);
    FILE* f = fopen(fn, "a");
    RuleResult overall = {};
    for (u32 rule = first; rule <= last; rule++) {
        if (rule >> 4 & 1) continue;  // complement symmetry: partner rule is searched instead
        RuleResult r = solve_rule(rule, reps, index, wk);
        printf("rule %3u %-22s run %8llu = tail %6llu + cycle %8llu | cycles %8llu cycle-orbits %10llu maxh %6u | %.1fs\n",
               rule, rule_str(rule).c_str(), (unsigned long long)r.best_run, (unsigned long long)r.best_tail,
               (unsigned long long)r.best_cycle, (unsigned long long)r.num_cycles, (unsigned long long)r.cycle_nodes,
               r.max_height, r.seconds);
        fflush(stdout);
        fprintf(f, "%u,\"%s\",%llu,%llu,%llu,%llu,%llu,%u,%.2f\n", rule, rule_str(rule).c_str(), (unsigned long long)r.best_run,
                (unsigned long long)r.best_tail, (unsigned long long)r.best_cycle, (unsigned long long)r.num_cycles,
                (unsigned long long)r.cycle_nodes, r.max_height, r.seconds);
        fflush(f);
        if (r.best_run > overall.best_run) overall = r;
    }
    fclose(f);
    printf("\nBEST for %dx%d over rules %u..%u: %llu unique states, rule %u %s (tail %llu + cycle %llu)\n", N, N, first,
           last, (unsigned long long)overall.best_run, overall.rule, rule_str(overall.rule).c_str(),
           (unsigned long long)overall.best_tail, (unsigned long long)overall.best_cycle);
    return 0;
}
