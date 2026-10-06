# 02 - Serve: load test + saturation reading

Host `Linux-x86_64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=4` ·
`ngl=99`

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 22 | 0.37 | 25000 | 45000 | 46000 | 8.8 | 0.0% |
| 50 | 62 | 1.05 | 27000 | 48000 | 50000 | 29.3 | 0.0% |

*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were
really in flight, regardless of how many users locust simulated. It counts queued requests
too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not
utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **2.79x** (56% of linear) |
| P95 latency | **1.07x** |
| Effective concurrency at 50 users | 29.3 vs `--parallel 4` slots (occupancy/slot ratio 7.31) |

**Slot capacity reached; throughput still rises.** Effective concurrency (29.3) exceeds the 4 decode slots, while throughput still rose 2.79x. Some requests may wait for a slot. These two load levels do not locate the exact throughput knee; check the server's deferred-request gauge.

P95 grew less than throughput (1.07x vs 2.79x), but effective concurrency is at or above the 4 slots. This does not establish spare capacity: inspect deferred requests and report goodput against a stated latency SLO.

## My reading

The four decode slots were full during the 50-user run: `make metrics` sampled
3.90 busy slots and as many as 46 deferred requests. The load report gives
29.3 requests in the system at 50 users, including those waiting. Even the
10-user run averaged 8.8 in the system, so these two load levels do not
pinpoint the onset of queueing. RPS rose 2.79x for 5x more users, while P95
rose from 45 to 48 seconds. With a 45-second P95 target, the 50-user run
misses the target. I would test `-t 1` first because the decode sweep improved
from 49.0 to 77.3 tok/s, then repeat both load runs; single-request speed
alone does not prove better goodput under concurrency.
