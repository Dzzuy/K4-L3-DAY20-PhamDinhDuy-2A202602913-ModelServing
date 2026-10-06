# 01 - Tune: thread-count sweep

Model `Qwen3.5-0.8B-Q4_K_M.gguf` · host `Linux-x86_64` · llama.cpp `b10488`
CPU: **4 physical · 8 logical** cores · `ngl=99` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 77.3 | 100% |
| 2 | 69.0 | 89% |
| 4 | 49.0 | 63% |
| 8 | 57.8 | 75% |
| 16 | 66.6 | 86% |

**Best**: `-t 1` at 77.3 tok/s
**Slowest tested**: `-t 4` at 49.0 tok/s (1.58x spread)
**Against the physical-core default** (`-t 4`, 49.0 tok/s): 1.58x

Use this in your run:

```bash
LAB_N_THREADS=1 make bench
```

## My explanation

The best measured point was one CPU thread (77.3 tok/s), not the four physical
cores (49.0 tok/s). This run used `-ngl 99`; the Vulkan runtime enumerated
Intel Iris Xe as its first device. More CPU threads therefore need not mean
more parallel GPU decode work. CPU-side scheduling and synchronization can add
overhead, and the integrated GPU shares system memory bandwidth with the CPU.

The curve is not monotonic: 8 and 16 threads recovered some throughput. That
makes a simple "bandwidth knee at one thread" claim too strong. I would treat
the 1.58x gain as the result of this sweep and repeat the comparison under a
controlled load before using `-t 1` as a production default.
