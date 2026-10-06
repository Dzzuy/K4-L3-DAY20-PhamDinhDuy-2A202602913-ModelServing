# Bonus C9 - embedding serving versus chat serving

I started the local `llama-server` on port 8081 with `--embedding` and ran
`make embed-demo` against its OpenAI-compatible `/v1/embeddings` endpoint.
The raw output is in `bonus-embedding-serving-run.txt`. The server returned
1024-dimensional vectors for eight short documents and a query. The relevant
embedding-serving sentence ranked first at cosine similarity 0.891.

| Static batch size | Total latency (ms) | Throughput (texts/s) |
|--:|--:|--:|
| 1 | 99.9 | 10.0 |
| 2 | 172.8 | 11.6 |
| 4 | 295.3 | 13.5 |
| 8 | 576.3 | 13.9 |
| 16 | 1069.6 | 15.0 |

Batching 16 texts raised throughput by 1.50x compared with one text, while
the whole batch took about 10.7x as long. This is one short run, so I would
repeat it before choosing a production batch size. The curve levels off by
eight to sixteen texts on this laptop; bigger batches would also make a
single short request wait longer if I held it to fill a batch.

The track 02 chat test reached only 1.05 requests/s at 50 users, with 48 s
P95 latency, four decode slots almost full (3.90 busy), and 46 deferred
requests at the peak. These are different inputs and units, so their rates
are not directly comparable. They illustrate different serving pressures:
the embedding endpoint does one forward pass per text and benefits from
static batches, while chat generates tokens in a decode loop and uses
continuous batching so requests can join and leave between steps.

I would scale these endpoints from separate queues and latency/throughput
targets. If they shared one autoscaler, decode saturation could delay short
embedding requests, while large embedding batches could delay chat TTFT.

This demo reuses the Qwen3.5 chat GGUF in pooling mode. It is not a trained
sentence encoder. The unrelated RadixAttention and speculative-decoding
sentences still scored 0.848 and 0.813 against the query, so the first-place
result alone is not evidence of reliable retrieval. A real RAG service would
use a dedicated embedding model and evaluate ranking quality separately.
