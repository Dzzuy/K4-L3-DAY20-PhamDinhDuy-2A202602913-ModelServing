# Reflection — Day 20 Lab (Personal Report)

> **Đây là báo cáo cá nhân.** Số liệu của bạn **không** so sánh được với bạn cùng lớp
> — chỉ so **before vs after trên chính máy bạn**. Rubric chấm độ rõ ràng của setup,
> đo lường và **lập luận**, không chấm tốc độ tuyệt đối.
>
> `make verify` sẽ fail nếu còn placeholder chưa điền. Đó là cố ý.

**Họ Tên:** Phạm Đình Duy
**MSSV:** 2A202602913
**Cohort:** K4-L3
**Ngày submit:** 2026-10-06

---

## 1. Hardware & runtime  *(rubric 1, 2 — 10 điểm)*

> Từ `make probe`. Paste output hoặc điền tay.

- **OS:** Fedora Linux 44 (Workstation Edition)
- **CPU:** Intel Core i7-1165G7
- **Cores:** 4 physical / 8 logical
- **CPU extensions:** AVX2, AVX-512
- **RAM:** 15.3 GB
- **Accelerator:** NVIDIA T500 4 GB được phát hiện; runtime Vulkan hiện thấy Intel Iris Xe để offload
- **llama.cpp asset đã tải:** llama-b10488-bin-ubuntu-vulkan-x64.tar.gz
- **Model đã dùng:** Qwen3.5 0.8B (`LAB_MODEL=qwen35-0.8b`)
- **Quantization:** Q4_K_M + UD-Q2_K_XL (từ `models/active.json`)

**Chạy ở đâu:** Laptop cá nhân, chạy local.

**Setup story** (≤ 80 chữ): điều gì cần thay đổi để lab chạy trên máy bạn? Có bước
nào fail rồi phải workaround không?

Tôi chọn Qwen3.5 0.8B để chạy local và giữ phép đo ổn định khi máy đang dùng nhiều RAM.
`make setup` tải hai quantization và bản llama.cpp Vulkan có sẵn cho Linux. NVIDIA T500
được nhận diện, nhưng runtime Vulkan liệt kê Intel Iris Xe là thiết bị đầu tiên;
đây không phải phép đo CUDA.

---

## 2. Đo lường  *(rubric 3, 4, 5 — 20 điểm)*

> Paste bảng từ `benchmarks/01-quickstart-results.md` (`make bench` tự sinh).

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|---|--:|--:|--:|--:|--:|--:|
| Q4_K_M | 0.50 | 3056 | 142 / 178 | 19.2 / 23.8 | 1173 / 1643 / 1643 | 51.9 |
| UD-Q2_K_XL | 0.39 | 3026 | 145 / 160 | 20.1 / 20.9 | 1405 / 1463 / 1463 | 49.7 |

**Quan sát** (≤ 60 chữ): 2-bit nhanh hơn bao nhiêu, và **có đáng không**? Bạn đã thử
hỏi cùng một câu trên cả hai (`make serve` vs `.venv/bin/python labs/02-serve/serve.py --compare`)
chưa? Chất lượng khác nhau thế nào?

UD-Q2_K_XL nhỏ hơn 0.11 GB (22%) nhưng decode chậm hơn khoảng 4%:
49.7 so với 51.9 tok/s. Đã gửi cùng câu hỏi về goodput@SLO cho hai bản ở
`temperature=0`: Q4 trả lời một phần, còn Q2 không định nghĩa được, cả hai đều
chưa đúng hoàn toàn. Vậy nên chọn Q4 cho bài này. Câu trả lời gốc nằm ở
`benchmarks/01-quality-comparison.md` là một mẫu kiểm tra chất lượng.

---

## 3. Serving under load  *(rubric 8, 9, 10 — 20 điểm)*

> Từ `benchmarks/02-server-results.md` (`make load-report`).

| Users | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|--:|--:|--:|--:|--:|--:|--:|
| 10 | 0.37 | 25000 | 45000 | 46000 | 8.8 | 0.0% |
| 50 | 1.05 | 27000 | 48000 | 50000 | 29.3 | 0.0% |

- **Offered load tăng 5×, throughput thực tăng:** 2.79×
- **P95 tăng:** 1.07×
- **Effective concurrency ở 50 users:** 29.3 so với `--parallel` = 4 slots

**Peak `llamacpp:n_busy_slots_per_decode`** (từ `make metrics` khi `make load-50` đang
chạy): 3.90 / 4 slots

**Saturation reading** (≤ 80 chữ): server của bạn bão hoà ở đâu, và **bằng chứng nào**
thuyết phục bạn? Nếu P95 tăng nhanh hơn RPS thì phần latency thêm đó là queue time hay
compute time — bạn biết bằng cách nào? Nếu bạn phải nâng goodput@SLO, bạn sẽ đổi knob
nào **trước**, và vì sao knob đó?

Tại 50 users, 3.90/4 slot bận và có lúc 46 request bị deferred; effective
concurrency 29.3 tính cả hàng chờ. RPS chỉ tăng 2.79× khi số users tăng 5×.
Nếu lấy P95 ≤ 45 giây làm SLO thử nghiệm, mức 50 users không đạt (P95 = 48 giây).
Tôi muốn thử `-t 1` trước vì sweep decode tăng từ 49.0 lên 77.3 tok/s, rồi đo
lại load; tăng tốc một request chưa bảo đảm goodput tăng khi nhiều request cùng vào.

---

## 4. Integration  *(rubric 12, 13 — 15 điểm)*

> Từ `make pipeline`. Nói thật cái nào real, cái nào stub — stub **không** mất điểm.

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | Chạy trên localhost | stub |
| N17 Data pipeline | Danh sách tài liệu mẫu trong bộ nhớ | stub |
| N18 Lakehouse | `TOY_DOCS` trong `pipeline.py` | stub |
| N19 Vector + features | Keyword overlap, không dùng vector index hay feature store | stub |
| N20 Serving | `llama-server` | real |

**Latency split** (mean của 3 query, từ output của `pipeline.py`):

- embed: 0.0 ms
- retrieve: 0.0 ms
- llm: 1665.3 ms
- **stage chiếm nhiều nhất:** llm (gần 100% của tổng 1665.4 ms)

**Reflection** (≤ 60 chữ): bottleneck ở đâu? Có khớp với kỳ vọng của bạn không? Nếu
phải giảm latency của pipeline này 2×, bạn sẽ tấn công vào đâu?

Với các stage N16–N19 đang stub, embed và retrieve gần như không tốn thời gian;
LLM chiếm gần toàn bộ 1665.4 ms. Điều này hợp với pipeline mẫu, nhưng không thể
suy rộng sang retrieval thật. Nếu cần giảm tổng latency 2×, tôi sẽ thử giảm số
token đầu ra và đo lại chất lượng, vì query đầu sinh 186 token và mất lâu nhất.

---

## 5. The single change that mattered most  *(rubric 11 — 10 điểm)*

> **Phần quan trọng nhất của report.** Không cần bonus track: `make tune` đã cho bạn
> một before/after thật (`benchmarks/01-tuning-tg128.md`). Đổi quantization,
> `LAB_N_CTX`, hay `--parallel` rồi đo lại cũng được.

**Change:** Hạ số CPU thread của phép đo `tg128` từ `-t 4` xuống `-t 1`, giữ `-ngl 99`.

```
before:  49.0 tok/s (-t 4)
after:   77.3 tok/s (-t 1)
speedup: 1.58×
```

**Tại sao nó work** (1–2 đoạn — đây là phần grader đọc kỹ nhất):

_Giải thích như đang nói với bạn ngồi cạnh. Bám vào **cơ chế**, không phải "vibes":
memory bandwidth? vector width? cache residency? scheduling? queueing? Nếu kết quả
**khác** với kỳ vọng từ deck — nói rõ, và giải thích vì sao. Grader thưởng điểm cho
lập luận đúng về một kết quả bất ngờ, hơn là một con số đẹp không được giải thích._

Đường cong này không đạt đỉnh ở bốn core vật lý như kỳ vọng thường gặp: `-t 1`
cho 77.3 tok/s, còn `-t 4` cho 49.0 tok/s. Phép đo dùng `-ngl 99`, và runtime
Vulkan liệt kê Intel Iris Xe trước NVIDIA T500. CPU thread chủ yếu còn lo phần
công việc và đồng bộ quanh GPU; thêm thread có thể tăng tranh chấp lịch chạy và
băng thông bộ nhớ dùng chung thay vì tăng tốc decode. Đây là lời giải thích có
thể phù hợp với máy này, không phải bằng chứng rằng mọi GPU cần một thread.

Giá trị ở 8 và 16 thread lại tăng so với 4, nên đường cong không có một knee
đơn giản. Tôi sẽ lặp lại hai cấu hình 1 và 4 thread trong cùng điều kiện, rồi
kiểm tra P95/goodput ở load thực tế trước khi đổi cấu hình phục vụ lâu dài.

---

## 6. Bonus  *(optional — tối đa 10 điểm)*

> Bỏ trống nếu không làm. Xem `docs/bonus/README.md`. Đừng làm hết — **một** finding sâu
> ăn điểm hơn năm bảng nông.

**Đã làm:** _<B1 build-compare / B2 sweep nào / B4 challenge nào / B5 lựa chọn nào>_

**Numbers:**

```
before:  <số>
after:   <số>
speedup: <X.Y>×
```

**Điều này nói lên gì mà deck chưa nói:**

_(để trống nếu bạn không làm phần này)_

---

## 7. Điều làm bạn ngạc nhiên nhất  *(optional)*

_(1–2 câu. Không bắt buộc, nhưng grader đọc hết.)_

_(để trống nếu bạn không làm phần này)_

---

## 8. Self-check trước khi push

- [x] `hardware.json` committed
- [x] `models/active.json` committed
- [x] `benchmarks/01-quickstart-results.md` committed (`make bench`)
- [x] `benchmarks/01-tuning-tg128.md` committed (`make tune`)
- [x] `benchmarks/02-server-results.md` committed (`make load-report`)
- [x] `benchmarks/02-server-batching-u50.md` hoặc `-metrics-u50.csv` committed (`make metrics`)
- [x] `benchmarks/locust-10_stats.csv` + `locust-50_stats.csv` committed (`make load-10` / `load-50`)
- [x] `benchmarks/03-integration-results.md` committed (`make pipeline`)
- [x] Mọi section **"required — replace this line"** trong các file `benchmarks/*.md`
      đã được thay bằng nhận xét của bạn
- [x] 5 screenshots trong `submission/screenshots/`
- [x] `make verify` → **exit 0**
- [x] Repo tên đúng mẫu `K4-L3-DAY20-HoVaTen-MSSV-ModelServing` (xem `docs/SUBMISSION.md`)
- [x] Repo GitHub ở chế độ **public**
- [x] Đã push và paste public URL vào VinUni LMS **trước 23:59 (UTC+7) ngày làm lab**
- [x] **Không** commit `models/*.gguf`, `runtime/` hay `.env` (đã có trong `.gitignore`)

**Quan trọng:** repo phải **public** đến khi điểm được công bố. Private → grader không
xem được → 0 điểm.

---

## 9. Khai báo sử dụng AI  *(xem `docs/RULES.md` §3)*

OpenAI Codex: hỗ trợ đọc rubric, kiểm tra báo cáo, và hỗ trợ biên tập báo cáo có kiểm duyệt. Số liệu và screenshot được tạo từ các lệnh chạy trên máy của tôi.
