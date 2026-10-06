# Bonus - GPU offload sweep

Host `Linux-x86_64` · hardware probe `nvidia_cuda` ·
llama.cpp `b10488` · `threads=4` ·
runtime device `Vulkan1` · metric `tg128` · repetitions `3`

| -ngl | tg128 (tok/s) | vs -ngl 0 | vs best |
|:--|--:|--:|--:|
| 0 | 29.4 | 1.00x | 51% |
| 32 | 57.3 | 1.95x | 100% |
| 99 | 56.6 | 1.93x | 99% |

Best: `-ngl 32` at 57.3 tok/s
-- 1.95x faster than CPU-only.

Once all model layers are offloaded, increasing `-ngl` cannot move more layers.
A lower result at `-ngl 99` than at a partial setting may also be run-to-run
noise or host contention; this sweep alone cannot establish a VRAM bottleneck.

## My finding

On the NVIDIA T500 (`Vulkan1`), moving from `-ngl 0` to `-ngl 32` raised
decode speed from 29.4 to 57.3 tok/s, a 1.95x gain. Setting `-ngl 99` gave
56.6 tok/s, only about 1% lower; I would treat 32 and 99 as effectively
the same result. The model is small enough that 32 may already cover all
its layers. This does not show a VRAM limit. My first full-grid run happened
while a CPU build was compiling and had a much lower CPU baseline, so I did
not use its larger speedup claim. A separate focused repeat with two
repetitions gave 29.4, 59.0, and 56.8 tok/s for the same three settings,
which supports the direction and approximate size of this result.
