# 01 - Measure: latency baseline

Model `Qwen3.5 0.8B` · host `Linux-x86_64` · llama.cpp `b10488`
Settings: `threads=4` `ngl=99` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `Q4_K_M` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| Q4_K_M | 0.50 | 3056 | 142 / 178 | 19.2 / 23.8 | 1173 / 1643 / 1643 | 51.9 |
| UD-Q2_K_XL | 0.39 | 3026 | 145 / 160 | 20.1 / 20.9 | 1405 / 1463 / 1463 | 49.7 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` decodes **1.04x SLOWER** than `Q4_K_M` here, despite being 0.11 GB smaller. This run used Vulkan offload (`ngl=99`); the smaller file did not produce a decode speedup. The measurement alone does not isolate the cause. Quantized kernel cost, device bandwidth, and run-to-run variation are possible contributors.

## My observation

UD-Q2_K_XL saves 0.11 GB (22%) against Q4_K_M, but its median decode speed is
49.7 instead of 51.9 tok/s, about 4% slower. In a same-prompt check with
`temperature=0`, Q4 gave a partial definition of goodput@SLO while Q2 did not
answer the question. Neither answer was fully correct. I would use Q4 here:
the smaller file brings no latency gain and looked less useful in this one
quality check. The raw answers are in `benchmarks/01-quality-comparison.md`.
