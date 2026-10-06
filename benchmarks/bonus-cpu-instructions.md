# Bonus C7 - CPU instruction-set comparison

Both Release builds use pinned llama.cpp `b10488`, the same
Qwen3.5 0.8B Q4 model (`Qwen3.5-0.8B-Q4_K_M.gguf`), four CPU threads, `-ngl 0`, and three
repetitions per test. The generic build uses `GGML_NATIVE=OFF` (AVX2 target);
the native build uses `GGML_NATIVE=ON` on the Intel i7-1165G7 (AVX-512 available).
No GPU is used in this comparison.

| Build | Key CMake flags | CPU instructions |
|:--|:--|:--|
| Generic | `-DCMAKE_BUILD_TYPE=Release -DGGML_NATIVE=OFF -DGGML_CUDA=OFF` | AVX2 target |
| Native | `-DCMAKE_BUILD_TYPE=Release -DGGML_NATIVE=ON -DGGML_CUDA=OFF` | Compiled for this i7 (AVX-512 available) |

| Metric | Generic tok/s | Native tok/s | Native / generic |
|:--|--:|--:|--:|
| pp512 | 77.2 | 101.1 | 1.31x |
| tg128 | 13.8 | 14.9 | 1.08x |

## My interpretation

The native build improved prefill from 77.2 to 101.1 tok/s (1.31x), while
decode moved from 13.8 to 14.9 tok/s (1.08x). Prefill processes many tokens
together, so its matrix operations have more opportunity to use the native
CPU's wider vector instructions. Decode processes one token at a time and
repeatedly reads weights, so memory bandwidth is a more plausible limit there.
These measurements support that explanation but do not isolate AVX-512 from
every other compiler optimization. Both builds were Release builds of the same
revision, with the same four threads, model, and CPU-only setting.
