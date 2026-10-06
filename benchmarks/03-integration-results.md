# 03 - Integrate: RAG pipeline run

Host `Linux-x86_64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.0 | 3399.6 | 3399.6 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.0 | 582.8 | 582.9 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.0 | 1013.6 | 1013.7 |

Mean per stage (ms): embed **0.0** · retrieve **0.0** ·
llm **1665.3** · total **1665.4**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Based on the provided context, **Goodput** is more useful than raw throughput because it explicitly addresses the issue of **saturation**.

While raw throughput measures the total requests per second (which can be high if the system is overloaded), Goodput only counts requests that met the **TTFT** (Throughput Target for Throughput) and **TPOT** (Throughput Target for Throughput Overhead) targets.

**What problem does PagedAttention actually solve?**

> PagedAttention solves the problem of **internal fragmentation in GPU memory** by storing the KV cache in non-contiguous pages.

**When does splitting prefill and decode help?**

> Based on the provided context, splitting prefill and decode helps when **prefill is compute-bound and decode is memory-bandwidth-bound**.

The context explicitly states: "Disaggregated serving splits prefill and decode onto separate pools because prefill is compute-bound and decode is memory-bandwidth-bound."


## Which N16-N19 pieces are real

N16 is localhost rather than deployed cloud infrastructure; N17 is an in-memory
list; N18 is the toy document collection; N19 is keyword overlap, not a vector
index or feature store. Those four pieces are stubs. N20 is a real
`llama-server` call. In this toy pipeline, embed and retrieve round to 0.0 ms,
while the LLM averages 1665.3 ms of 1665.4 ms total. To halve total latency I
would target generation first, especially the long first answer (186 output
tokens), and measure whether a shorter answer budget preserves usefulness.
The first answer also expanded TTFT and TPOT incorrectly, so latency is not the
only quality constraint.
