# PLAN.md — Kế hoạch thực hiện FLAP Dashboard

> Tài liệu này là **lộ trình và tiến độ**. Kiến thức nền (schema dữ liệu, môi trường, quyết định kỹ thuật và lý do) nằm ở [CLAUDE.md](CLAUDE.md).

---

## 1. Mục tiêu

Dựng hệ thống dashboard theo dõi sản xuất cho Regent Garment Factory, tự host trên một PC Windows 11, chia sẻ trong mạng LAN nhà máy.

| Yêu cầu | Cách đáp ứng |
|---|---|
| Song ngữ Việt / Anh | Từ điển JSON ở frontend, backend chỉ trả mã gốc |
| Nhiều dashboard | Nhóm `/tv/*` cho màn hình TV, nhóm `/pc/*` cho PC tương tác |
| Dashboard TV tĩnh | Không thao tác, chữ lớn, tự xoay trang, tự kết nối lại |
| Dashboard PC tương tác | Bộ lọc, bảng sắp xếp, drill-down, xuất CSV |
| Backend FastAPI | Đọc Excel giai đoạn 1, sẵn sàng đổi sang SQL Server |
| Cập nhật realtime | Watcher theo dõi file + đẩy sự kiện qua SSE |
| Giao diện chuyên nghiệp | Next.js + Tailwind + shadcn/ui |
| Tài liệu tiếng Việt | `PLAN.md` và `CLAUDE.md` |
| Chạy ngầm, có log | `pythonw` + Task Scheduler + log xoay vòng |

---

## 2. Bảng tiến độ

| Bước | Nội dung | Trạng thái |
|:--:|---|:--:|
| **0** | Khởi tạo, git, tài liệu | 🟡 Đang làm |
| 1 | Nhân đọc & chuẩn hoá Excel + kiểm thử đối chiếu | ⬜ Chưa |
| 2 | API WIP + KPI | ⬜ Chưa |
| 3 | Realtime (SSE) + lưu lịch sử Parquet | ⬜ Chưa |
| 4 | Nền frontend (Next.js + i18n) | ⬜ Chưa |
| 5 | Dashboard TV — WIP Overview (MVP) | ⬜ Chưa |
| 6 | Dashboard PC tương tác | ⬜ Chưa |
| 7 | Triển khai LAN + chạy ngầm | ⬜ Chưa |
| 8 | Các dashboard còn lại | ⬜ Chưa |
| 9 | Sẵn sàng SQL Server | ⬜ Chưa |

**Quy ước làm việc:** sau **mỗi** bước phải cập nhật `PLAN.md` + `CLAUDE.md`, rồi **dừng lại chờ xác nhận** mới sang bước tiếp theo.

### Nhật ký

| Ngày | Việc đã làm |
|---|---|
| 2026-08-03 | Khảo sát 5 file Excel, xác định schema và các bẫy dữ liệu. Kiểm tra môi trường máy. Chốt kiến trúc Next.js + FastAPI. Viết `.gitignore`, `PLAN.md`, `CLAUDE.md`. |

---

## 3. Kiến trúc tổng thể

```
Client (TV kiosk / PC trình duyệt)
        │  HTTP + SSE — chỉ 1 port duy nhất (8080)
        ▼
FastAPI ─── phục vụ luôn frontend Next.js đã build tĩnh
        ├── /api/...      REST trả dữ liệu + KPI
        ├── /api/stream   SSE đẩy sự kiện khi dữ liệu đổi
        └── Watcher       theo dõi thư mục "EXCEL files"
                │
                ▼
        DataSource (lớp trừu tượng)
          ├── ExcelDataSource      ← giai đoạn 1
          └── SqlServerDataSource  ← giai đoạn 2, cắm vào không sửa frontend
```

### Cấu trúc thư mục dự kiến

```
FLAP/
├─ CLAUDE.md              # kiến thức nền, cập nhật sau MỖI bước
├─ PLAN.md                # tài liệu này
├─ .gitignore
├─ EXCEL files/           # dữ liệu nguồn — CHỈ ĐỌC, KHÔNG commit
├─ data/history/          # snapshot Parquet theo thời gian — không commit
├─ logs/                  # nhật ký xoay vòng — không commit
├─ backend/
│  ├─ .venv/
│  ├─ requirements.txt
│  ├─ run_server.py       # điểm chạy ngầm bằng pythonw
│  ├─ tests/              # pytest: hàm chuẩn hoá + đối chiếu WIP_Sammary
│  └─ app/
│     ├─ main.py
│     ├─ config.py            # pydantic-settings, đọc .env
│     ├─ logging_config.py    # log xoay vòng UTF-8
│     ├─ core/
│     │  ├─ excel_utils.py    # serial→datetime, "NULL"→None, tách list, bỏ banner
│     │  └─ events.py         # EventBus in-memory cho SSE
│     ├─ datasource/
│     │  ├─ base.py           # Protocol DataSource
│     │  ├─ excel_source.py
│     │  └─ sql_source.py     # Bước 9
│     ├─ models/              # Pydantic schema
│     ├─ services/
│     │  ├─ cache.py          # cache RAM + hash nội dung
│     │  ├─ watcher.py        # watchdog + debounce + retry
│     │  ├─ history.py        # ghi snapshot Parquet
│     │  └─ kpi.py            # tính KPI
│     └─ api/                 # routes_wip.py, routes_stream.py, routes_meta.py
├─ frontend/
│  ├─ next.config.ts          # output:'export', basePath, images.unoptimized
│  └─ src/
│     ├─ app/tv/wip/          # layout TV
│     ├─ app/pc/wip/          # layout PC
│     ├─ components/
│     ├─ lib/                 # api client, hook useLiveData
│     └─ i18n/{vi,en}.json
└─ scripts/
   ├─ dev-backend.ps1  dev-frontend.ps1  build-and-serve.ps1
   ├─ start.cmd  stop.cmd  restart.cmd
   ├─ install-task.ps1
   └─ firewall-rule.ps1       # đưa IT chạy, cần Admin
```

---

## 4. Các bước chi tiết

### Bước 0 — Khởi tạo, git & tài liệu 🟡

- [x] Tạo `.gitignore` loại trừ `EXCEL files/`, `*.xlsx`, `data/`, `logs/`, `.env`, `.venv/`, `node_modules/` — **làm trước mọi lệnh `git add`**
- [x] Viết `PLAN.md` và `CLAUDE.md` bằng tiếng Việt
- [ ] Nối remote `https://github.com/nqhuy-212/FLAP.git`, commit đầu tiên, push
- [ ] *(session sau)* Tạo `.env` + `.env.example` + `config.py`
- [ ] *(session sau)* Tạo venv Python 3.13, cài `fastapi uvicorn[standard] pandas python-calamine openpyxl pyarrow watchdog pydantic-settings pytest`
- [ ] *(session sau)* Dựng `logging_config.py` + `run_server.py` để mọi bước sau đều có log

**Hai việc phụ thuộc bên ngoài — khởi động NGAY, chạy song song với code:**
- [ ] **Gửi ticket IT xin mở inbound firewall TCP 8080.** Đây là việc duy nhất không kiểm soát được thời gian; để đến Bước 7 mới xin là quá muộn.
- [ ] **Thử Task Scheduler bằng một task giả** xem tuỳ chọn *"Run whether user is logged on or not"* có bị domain policy chặn không.

*Nghiệm thu:* `git ls-files` không có file `.xlsx` nào và không có `.env`.

### Bước 1 — Nhân đọc & chuẩn hoá Excel + kiểm thử đối chiếu

`excel_utils.py` + `datasource/base.py` (theo hợp đồng đã chốt trong CLAUDE.md) + `excel_source.py` đọc `WIP Report_1.1`.

Kèm **bộ test tự động** — đây là chỗ duy nhất có sẵn "đề bài và đáp án":
- Test hàm thuần: serial date → datetime, `"NULL"` → None, tách `"34003,34004"`, bỏ 4 dòng banner, lấy cột trùng tên theo vị trí.
- **Test đối chiếu:** tự tính từ `WIP_Detail` rồi so với `WIP_Sammary`. Bắt được đúng loại lỗi nguy hiểm nhất — sai mẫu số khi tính trung bình, ra số sai mà không báo lỗi rồi hiện thẳng lên TV xưởng.

*Nghiệm thu:* `pytest` xanh; đọc ra 352 dòng `WIP_Detail` với ngày tháng đã là datetime thật.

### Bước 2 — API WIP + KPI

Pydantic models, `services/kpi.py`, endpoints `/api/wip/detail`, `/api/wip/summary`, `/api/wip/kpi`, `/api/meta/health`.

KPI: tổng trolley và sản lượng đang tồn; phân bổ theo khu vực CCT/VAP; nhóm tuổi WIP (0–3 / 4–7 / 8–14 / >14 ngày); Top 10 style-MO tồn lâu nhất; xu hướng theo `Loading Date`.

*Nghiệm thu:* mở `http://localhost:8080/docs`, thử từng endpoint ra số liệu đúng.

### Bước 3 — Realtime + lưu lịch sử

`events.py` (EventBus), `watcher.py` (watchdog + debounce + hash + poll dự phòng 30s), `GET /api/stream` (SSE có heartbeat).

**Kèm lưu lịch sử Parquet** vào `data/history/` mỗi khi chấp nhận snapshot mới — **làm ngay ở bước này, không hoãn được**, vì dữ liệu không lưu là mất vĩnh viễn.

*Nghiệm thu:* copy đè file Excel → sự kiện `data_changed` bắn ra trong vài giây, có file Parquet mới trong `data/history/`.

### Bước 4 — Nền frontend

Next.js 15 (App Router, TypeScript) + Tailwind + shadcn/ui; provider i18n VI/EN nhẹ (React Context + JSON); api client; hook `useLiveData` bọc `EventSource` kèm chỉ báo trạng thái kết nối.

`next.config.ts`: `output: 'export'`, `basePath`/`assetPrefix` từ env, **`images.unoptimized: true`** (bắt buộc với static export).

*Chỉ dịch nhãn giao diện* — giá trị dữ liệu từ MES như `Color_Name` = "69 NAVY" hay tên nhân viên giữ nguyên.

*Nghiệm thu:* trang hiển thị số trolley thật; đổi VI/EN thấy nhãn đổi ngay.

### Bước 5 — Dashboard TV: WIP Overview (MVP hoàn chỉnh)

Layout 1920×1080 cố định, chữ lớn, nền tối tương phản cao, **không thanh cuộn**, tự xoay giữa các khối; đèn báo kết nối + dấu thời gian cập nhật cuối; ngôn ngữ chọn qua URL (`/tv/wip?lang=vi`) vì TV không thao tác được.

> Nạp skill `dataviz` trước khi viết dòng code biểu đồ đầu tiên.

*Nghiệm thu:* mở toàn màn hình, sửa file Excel → số trên TV tự đổi, không cần F5.

### Bước 6 — Dashboard PC tương tác

Bộ lọc (khoảng ngày, style, màu, khu vực, workstation), bảng sắp xếp, drill-down từ tổng hợp xuống chi tiết trolley, xuất CSV, nút VI/EN, sáng/tối.

*Nghiệm thu:* lọc một style, số liệu khớp với bản tổng hợp trong Excel.

### Bước 7 — Triển khai LAN + chạy ngầm

- Build Next tĩnh, nhúng vào FastAPI (1 port), uvicorn `--host 0.0.0.0`, **1 worker**
- Hoàn thiện `run_server.py` chạy bằng `pythonw` (xử lý bẫy `sys.stdout is None`)
- `install-task.ps1` đăng ký Task Scheduler tự khởi động + tự restart; `start/stop/restart.cmd` bấm đúp
- Trang `/pc/system` xem trạng thái và log **không cần Terminal** — đặt sau token vì log chứa tên nhân viên
- Theo dõi ticket IT; `firewall-rule.ps1` để IT chạy một lần
- Mini PC nối TV chạy Chrome kiosk (`--kiosk --noerrdialogs --disable-session-crashed-bubble`), tự mở khi khởi động

*Nghiệm thu:* khởi động lại PC → dashboard tự chạy, không cửa sổ Terminal nào; máy khác trong LAN mở `http://192.168.156.46:8080/tv/wip` thấy chạy; kill tiến trình → tự bật lại trong 1 phút.

### Bước 8 — Các dashboard còn lại

Delivery Panel (TV, cảnh báo hàng tái chế) · Cutting & Print từ `order_8.1` (PC) · Fabric Relaxation đếm ngược 24 giờ (PC/TV) · Material Exception từ `Heat_7.1` gồm bóc tách cột `ResultJson`.

### Bước 9 — Sẵn sàng SQL Server

`sql_source.py` hiện thực đúng Protocol ở Bước 1 (pyodbc + ODBC Driver 17 đã có sẵn); đổi nguồn chỉ bằng `FLAP_DATASOURCE=sql` trong `.env`; ưu tiên Windows Authentication để khỏi lưu mật khẩu; realtime chuyển sang mốc nước `MAX(updated_at)` hoặc Change Tracking; lập tài liệu các bảng/cột cần xin quyền đọc để gửi DBA.

---

## 5. Nghiệm thu tổng thể

1. `scripts/build-and-serve.ps1` → mở được `/tv/wip` và `/pc/wip`
2. Copy đè `WIP Report_1.1.xlsx` → **cả hai màn hình tự cập nhật trong ~3 giây**, không F5
3. Rút cáp mạng client vài giây rồi cắm lại → TV tự kết nối lại, đèn báo về xanh
4. Từ laptop khác trong LAN mở bằng IP → hoạt động y hệt
5. Bấm VI/EN → nhãn, định dạng ngày và số đổi theo, số liệu giữ nguyên
6. So một chỉ tiêu bất kỳ với công thức tính tay trong Excel → khớp
7. Khởi động lại PC → dashboard tự chạy, **không cửa sổ Terminal nào**
8. Kết thúc tiến trình `pythonw` → tự bật lại trong 1 phút
9. `logs/data-events.log` ghi đúng thời điểm thả file, tên tiếng Việt đúng dấu
10. `git ls-files` không có `.xlsx`, không có `.env`
11. `pytest` xanh, gồm test đối chiếu với `WIP_Sammary`
12. `data/history/` tích luỹ nhiều snapshot Parquet sau vài lần thả file

---

## 6. Rủi ro đã biết

| Rủi ro | Mức độ | Xử lý |
|---|:--:|---|
| **Dữ liệu nhà máy lên GitHub.** `Relaxed_3.1.xlsx` chứa tên thật nhân viên; 4 file còn lại là số liệu sản xuất nội bộ | 🔴 Cao | `.gitignore` đã chặn. Cần kiểm tra repo GitHub để **Private**. Nếu lỡ push thì xoá commit là chưa đủ — phải coi như đã lộ |
| **Không có quyền Admin** → không tự mở được firewall, máy khác trong LAN không vào được | 🔴 Cao | Thiết kế chỉ dùng 1 port; gửi ticket IT ngay Bước 0 |
| **`Cut_Qty` / `Deduct_Qty` chỉ có ở sheet tổng hợp**, không có ở sheet chi tiết | 🟠 Vừa | Đánh dấu `SOURCE` trong bảng nguồn gốc ở CLAUDE.md; sang SQL phải tìm lại đúng nguồn |
| **Task Scheduler "chạy khi chưa đăng nhập"** có thể bị domain policy chặn | 🟠 Vừa | Thử sớm ở Bước 0; dự phòng là để PC luôn đăng nhập |
| **Excel xuất thủ công** → "realtime" thực chất là "tức thì kể từ lúc thả file vào" | 🟡 Thấp | Chấp nhận ở giai đoạn 1; realtime đúng nghĩa chờ giai đoạn SQL |
| **PC host phải luôn bật** thì TV mới có dữ liệu | 🟡 Thấp | Tắt chế độ ngủ của máy |
