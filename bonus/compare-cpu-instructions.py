#!/usr/bin/env python3
"""C7: compare native and generic CPU builds from the same llama.cpp revision."""
from __future__ import annotations

import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "lib"))
import labkit  # noqa: E402


ROOT = labkit.repo_root() / "bonus" / "llama.cpp"


def check_build(build: str, native: bool) -> pathlib.Path:
    directory = ROOT / build
    cache = (directory / "CMakeCache.txt").read_text()
    expected = f"GGML_NATIVE:BOOL={'ON' if native else 'OFF'}"
    if expected not in cache or "CMAKE_BUILD_TYPE:STRING=Release" not in cache:
        labkit.die(f"{build} does not have the expected Release/{expected} settings")
    if "GGML_CUDA:BOOL=OFF" not in cache:
        labkit.die(f"{build} must be CPU-only for an instruction-set comparison")
    binary = directory / "bin" / "llama-bench"
    if not binary.is_file():
        labkit.die(f"Missing {binary}; compile the llama-bench target first")
    return binary


def measure(binary: pathlib.Path, model: pathlib.Path, metric: str) -> float:
    shape = ["-p", "512", "-n", "0"] if metric == "pp512" else ["-p", "0", "-n", "128"]
    command = [str(binary), "-m", str(model), "-t", "4", "-ngl", "0",
               *shape, "-r", "3"]
    result = subprocess.run(command, capture_output=True, text=True,
                            check=False, timeout=1800)
    output = result.stdout + result.stderr
    if result.returncode:
        labkit.die(f"{binary} failed: {output[-3000:]}")
    speed = labkit.bench_metric(output, metric)
    if not speed:
        labkit.die(f"No {metric} measurement from {binary}: {output[-3000:]}")
    return speed


def main() -> int:
    generic = check_build("build-cpu-baseline", native=False)
    native = check_build("build-cpu-native", native=True)
    model = labkit.repo_root() / labkit.load_active()["primary_model"]
    rows = []
    data = {}
    for metric in ("pp512", "tg128"):
        generic_speed = measure(generic, model, metric)
        native_speed = measure(native, model, metric)
        ratio = native_speed / generic_speed
        rows.append([metric, f"{generic_speed:.1f}", f"{native_speed:.1f}", f"{ratio:.2f}x"])
        data[metric] = {"generic_tok_s": generic_speed,
                        "native_tok_s": native_speed, "native_over_generic": ratio}
        print(f"{metric}: generic {generic_speed:.1f}, native {native_speed:.1f} tok/s ({ratio:.2f}x)")

    report = f"""# Bonus C7 - CPU instruction-set comparison

Both Release builds use pinned llama.cpp `{labkit.LLAMA_CPP_BUILD}`, the same
Qwen3.5 0.8B Q4 model (`{model.name}`), four CPU threads, `-ngl 0`, and three
repetitions per test. The generic build uses `GGML_NATIVE=OFF` (AVX2 target);
the native build uses `GGML_NATIVE=ON` on the Intel i7-1165G7 (AVX-512 available).
No GPU is used in this comparison.

{labkit.md_table(['Metric', 'Generic tok/s', 'Native tok/s', 'Native / generic'], rows)}

## Interpretation (required -- replace this line)

Explain what changed for prefill versus decode and whether vector instruction
width or memory bandwidth is the more plausible limiting factor. A difference
under a few percent should not be presented as a meaningful speedup.
"""
    path = labkit.write_report("bonus-cpu-instructions.md", report, data)
    print(f"Wrote {path.relative_to(labkit.repo_root())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
