# Same-prompt quality check

On the local Qwen3.5 0.8B server, both quantizations received the same system message
(`You are a model-serving tutor. Be concise.`) and user question
(`Define goodput@SLO in one sentence.`), with `temperature=0` and `max_tokens=80`.
The Q4 server listened on port 8080 and the Q2 comparison server on port 8090.

| Quantization | Answer returned |
|:--|:--|
| Q4_K_M | Goodput@SLO is the specific latency threshold (in milliseconds) that a service must achieve to be considered "good" for a given service level agreement (SLA). |
| UD-Q2_K_XL | Goodput@SLO is a specific, specialized term that is not widely recognized in the general public, so it is not defined in a single sentence. |

Neither answer gives the full lab definition: goodput@SLO counts requests per second
that meet the stated latency targets. Q4 at least relates the concept to an SLO;
Q2 does not answer the question. This is one qualitative sample, not a broad
accuracy evaluation.
