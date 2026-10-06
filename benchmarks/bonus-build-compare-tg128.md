# Bonus B1 - Prebuilt vs source build

Host `Linux-x86_64` · CPU `11th Gen Intel(R) Core(TM) i7-1165G7 @ 2.80GHz`
Vector extensions detected: AVX-512, AVX2
llama.cpp `b10488` both sides · `threads=4` ·
**both pinned to `ngl=0`** so this isolates the compiler ·
metric `tg128`, 3 repetitions

> **Backend mismatch, handled.** The prebuilt binary sees
> `['Vulkan0: Intel(R) Iris(R) Xe Graphics (TGL GT2) (11774 MiB, 3874 MiB free)', 'Vulkan1: NVIDIA T500 (4342 MiB, 2935 MiB free)']` and your source build sees `(no devices)`.
> Left at `-ngl 99` this comparison would have measured the accelerator and printed
> it under a compiler headline, so both sides were pinned to `-ngl 0`.

| Binary | Built for | tg128 (tok/s) | Relative |
|:--|--:|--:|--:|
| prebuilt release | runtime CPU dispatch | 17.0 | 1.00x |
| your source build | this CPU (`-DGGML_NATIVE=ON`) | 17.9 | 1.05x |

On this machine, the source build is **1.05x faster**.

before: 17.0 tok/s (prebuilt release)
after:  17.9 tok/s (source build, -DGGML_NATIVE=ON)
speedup: 1.05x

Same source revision, same model, same backend, same `-ngl` -- the only difference
is what the compiler was allowed to assume about the CPU.



## My explanation

The source build is 0.9 tok/s faster (about 5%) in this CPU-only decode test.
This i7 supports AVX-512 and AVX2, so a native build can select instructions
for this exact chip at compile time. The prebuilt release also has runtime CPU
dispatch, which likely narrows the gap. Decode reads model weights repeatedly,
so memory bandwidth may limit how much wider vector instructions help. This
single three-repetition comparison is a small measured difference, not proof
that AVX-512 alone caused it; the separate C7 build comparison tests the
instruction-set choice more directly.
