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
| **0** | Khởi tạo, git, tài liệu | 🟡 Gần xong — còn `run_server.py`, ticket IT, thử Task Scheduler |
| **1** | Nhân đọc & chuẩn hoá Excel + kiểm thử đối chiếu | ✅ Xong — `pytest` xanh 34/34 |
| **2** | API WIP + KPI | ✅ Xong — 4 endpoint chạy thật, `pytest` xanh 55/55 |
| **3** | Realtime (SSE) + lưu lịch sử Parquet | ✅ Xong — kiểm chứng thật end-to-end, `pytest` xanh 70/70 |
| **4** | Nền frontend (Next.js + i18n) | ✅ Xong — kiểm chứng thật bằng trình duyệt headless |
| **5** | Dashboard TV — WIP Overview (MVP) | ✅ Xong — kiểm chứng thật, live-update không F5 |
| **6** | Dashboard PC tương tác | ✅ Xong — kiểm chứng thật, lọc style khớp Excel |
| 7 | Triển khai LAN + chạy ngầm | 🟡 Code + script xong, kiểm chứng thật trên localhost — còn IT mở firewall, đăng ký Task Scheduler thật, kiosk TV |
| 8 | Các dashboard còn lại | ⬜ Chưa |
| 9 | Sẵn sàng SQL Server | ⬜ Chưa |

**Quy ước làm việc:** sau **mỗi** bước phải cập nhật `PLAN.md` + `CLAUDE.md`, rồi **dừng lại chờ xác nhận** mới sang bước tiếp theo.

### Nhật ký

| Ngày | Việc đã làm |
|---|---|
| 2026-08-03 | Khảo sát 5 file Excel, xác định schema và các bẫy dữ liệu. Kiểm tra môi trường máy. Chốt kiến trúc Next.js + FastAPI. Viết `.gitignore`, `PLAN.md`, `CLAUDE.md`. Commit đầu tiên + push lên GitHub. |
| 2026-08-04 | Phát hiện **PyPI bị chặn ở tầng TCP** trên mạng nhà máy. Viết [py_pack.md](py_pack.md) — quy trình wheelhouse offline. Tạo venv, `requirements.txt`, `pytest.ini`. Viết code Bước 1: `excel_utils.py`, `datasource/base.py`, `excel_source.py`, models, 2 file test. |
| 2026-08-07 | So sánh phương án backend Node.js với Python — **giữ nguyên Python + FastAPI** (npm chạy được nhưng mất pandas/pyarrow, Parquet của Node yếu, và Node không có tương đương `pythonw`). Nhận wheelhouse 36 file. Kiểm chứng bằng `pip --dry-run`: **thiếu đúng `tzdata`**. Thêm `*.7z` vào `.gitignore`. Cài 36 gói bằng `pip install --no-index --no-deps <từng wheel>` (né được việc thiếu `tzdata` vì dự án chỉ dùng datetime naive, không cần timezone). **Chạy `pytest` thật lần đầu: 34/34 PASS**, không cần sửa dòng code nào dù pandas 3.0.5 là bản major mới. Sửa số liệu nghiệm thu Bước 1: 347 dòng `WIP_Detail` / 36 dòng `WIP_Sammary` (con số 352/41 trong bảng khảo sát CLAUDE.md là tổng dòng vật lý kể cả banner/header, không phải dòng dữ liệu). Làm Bước 2: tạo `.env`/`.env.example`/`config.py`, `models/kpi.py`, `services/kpi.py`, `api/routes_wip.py`, `api/routes_meta.py`, `main.py`. Chạy server thật (`python -m app.main`) và gọi từng endpoint — phát hiện 2 bug thật chỉ lộ ra khi chạy thật (pytest không bắt được vì test dùng đối tượng Python thuần, không đi qua serialize JSON của FastAPI): (1) `/api/wip/detail` lỗi 500 vì cột ngày trống được pandas parse thành `NaT`, mà `NaT` là subclass của `datetime` nên lọt qua nhánh passthrough của `excel_serial_to_datetime` thay vì bị nhận diện là rỗng; (2) `Area`/`wbCode` có ô trống thật trong dữ liệu (5 và 4 dòng) nhưng bị `str(clean_null(x))` ép thành chuỗi `"None"` sai thay vì `None` thật. Sửa cả hai, thêm 3 test hồi quy, `pytest` xanh 55/55. Làm Bước 3: thêm `history_dir`/`log_dir` vào `config.py`, `logging_config.py` (logger `data-events.log`), `core/events.py` (EventBus), `services/watcher.py` (watchdog + debounce 2s + hash SHA-256 + retry `PermissionError` + bỏ qua `~$*.xlsx` + poll dự phòng 30s), `services/history.py` (snapshot Parquet `wip_detail_*`/`wip_summary_*`), `api/routes_stream.py` (SSE thủ công qua `StreamingResponse`, không cần thêm dependency vì `httpx` chưa có trong wheelhouse). Kiểm chứng **thật end-to-end**: dựng server phụ trỏ vào bản sao tạm của `WIP Report_1.1.xlsx` (không đụng "EXCEL files/" gốc), dùng `curl` mở `/api/stream`, sửa bản sao bằng `openpyxl` để mô phỏng MES xuất lại — nhận đúng `event: data_changed` trong ~2s, có 2 file Parquet mới (`wip_detail_*`, `wip_summary_*`), `logs/data-events.log` ghi đúng tên file + hash + thời điểm. `pytest` xanh 70/70 (15 test mới cho events/watcher/history). Làm Bước 4: khởi tạo `frontend/` bằng Next.js **16.3.0** (không phải 15 như dự kiến — cảnh báo `AGENTS.md` tự sinh nói rõ có breaking change so với dữ liệu huấn luyện AI, đã đọc `node_modules/next/dist/docs/` trước khi viết code, API `output:'export'`/`basePath`/`images.unoptimized` không đổi). shadcn/ui init lỗi `self-signed certificate in certificate chain` khi gọi `ui.shadcn.com` (mạng có proxy soi SSL — khác kiểu chặn với PyPI) → tạm tắt xác thực TLS chỉ cho lệnh `shadcn init`/`add`. Viết `next.config.ts` (đọc `FLAP_BASE_PATH` thẳng từ `.env` gốc, không tách riêng), `i18n/context.tsx` (VI/EN qua React Context + JSON), `lib/api.ts` + `lib/types.ts` (khớp Pydantic models), `lib/useLiveData.ts` (bọc EventSource). Phát hiện 2 vấn đề thật khi chạy thử bằng trình duyệt headless (Edge qua `playwright-core`, không cần tải Chromium): (1) `next build` **cũng nạp `.env.local`** giống `next dev` — phải đổi tên file dev-only thành `.env.development.local` để URL backend dev không bị đóng băng vào bundle production; (2) CORS: backend chưa cho phép origin `localhost:3000` gọi sang `localhost:8080`, toàn bộ fetch/EventSource lỗi — thêm `CORSMiddleware` + `FLAP_CORS_ORIGINS` vào backend. ESLint bắt lỗi thật "Cannot access refs during render" ở `useLiveData.ts` — sửa bằng cách gán `ref.current` trong `useEffect` thay vì lúc render. Kiểm chứng cuối bằng ảnh chụp màn hình thật: số liệu đúng (347 trolley, 110.209 sản lượng), đổi VI/EN đổi nhãn ngay, badge "Đã kết nối", không lỗi console. Sau đó phát hiện **bug thật thứ 3**: khai `cors_origins: list[str]` làm `Settings()` lỗi ngay khi `FLAP_CORS_ORIGINS` thật sự có trong `.env` (pydantic-settings tự parse env var kiểu list bằng JSON trước khi field_validator chạy) — đổi sang `cors_origins: str` + property `cors_origins_list`, thêm `tests/test_config.py`. `pytest` xanh 76/76. Làm Bước 5: nạp skill `dataviz` trước khi viết code biểu đồ (bắt buộc theo PLAN.md); dùng palette dark tham chiếu của skill (nguyên hex, đã `validate_palette.js --ordinal --surface "#1a1a19"` PASS cho dải tuổi WIP `#86b6ef→#184f95`); viết 4 component biểu đồ thuần SVG (`HorizontalBarChart`, `TrendChart`, `TopAgingTable`, `StatTile`) theo đúng mark spec (cột ≤24px, bo 4px, nhãn trực tiếp, 1 hue cho category không thứ tự, ordinal ramp cho age_buckets có thứ tự — tránh đúng anti-pattern "value-ramp on nominal categories"); `app/tv/wip/page.tsx` đọc `lang` từ URL (`useSearchParams` trong `<Suspense>` — bắt buộc với static export), tự xoay 4 khối mỗi 12s, layout 1920×1080 cố định nền tối. **Bug thật nghiêm trọng nhất dự án tới giờ:** khi kiểm chứng "sửa Excel → TV tự đổi không F5" bằng trình duyệt thật, dữ liệu **không** cập nhật dù backend đã log đúng đã phát hiện đổi + lưu snapshot — dò từng lớp (raw `EventSource` cùng-origin, rồi `curl` thay hẳn browser) phát hiện `curl` cũng không nhận được event nữa dù đã nhận được ở Bước 3, tức lỗi nằm ở backend chứ không phải frontend/CORS. Nguyên nhân: `uvicorn.run(..., reload=True)` không truyền `reload_dirs` nên mặc định theo dõi **toàn bộ** `backend/` kể cả `.venv/` — cache `.pyc` sinh ra khi `pyarrow` chạy lần đầu bị hiểu nhầm là đổi code, worker restart ngầm, `EventBus` mất theo, mọi SSE client rớt kết nối im lặng (không lỗi, không log). Sửa: `reload_dirs=["app"]`. Xác nhận lại bằng kịch bản y hệt — số liệu đổi đúng tại T=2s, không gọi `reload()`/F5. `tsc`/ESLint/`next build` xanh; `pytest` xanh 76/76 (backend không đổi entity, chỉ đổi `main.py` phần `__main__`). Làm Bước 6: thêm shadcn `table`/`select`/`switch`/`input`/`label`; `lib/theme.tsx` (ThemeProvider sáng/tối — Tailwind v4 đã có sẵn class `.dark` + `@custom-variant dark` từ lúc `shadcn init` ở Bước 4, chỉ cần toggle class trên `<html>`); `components/pc/{FilterBar,SummaryTable,DetailTable,SortableHead}.tsx` + `lib/useSortableData.ts` + `lib/csv.ts`; `app/pc/wip/page.tsx`. Kiến trúc lọc: filter áp lên **entity thô** (`WipTrolley`, có đủ ngày/khu vực/trạm), từ đó suy ra tập `mo_no` còn hiển thị rồi lọc **bảng tổng hợp SOURCE nguyên bản** (`WipSummary`, không tính lại `Cut_Qty`/`Deduct_Qty`) theo tập đó — đảm bảo khi chỉ lọc Style thì số liệu khớp tuyệt đối với Excel (đúng nghiệm thu). ESLint bắt tiếp 2 lỗi thật cùng loại "set-state trong effect" (`theme.tsx` đọc localStorage lúc mount, và logic tự bỏ chọn MO khi bị lọc mất trong `page.tsx`) — sửa bằng lazy initializer (`useState(getInitialTheme)`) và giá trị dẫn xuất tính thẳng lúc render (`effectiveSelectedMo`) thay vì effect + setState, đúng khuyến nghị "you might not need an effect" của React. Bug hiển thị nhỏ: base-ui `Select.Value` mặc định hiện **giá trị thô** (`__all__`) thay vì nhãn — đọc doc cục bộ `node_modules/@base-ui/react/docs/`, sửa bằng children-render-prop `<SelectValue>{(v) => label}</SelectValue>`. Kiểm chứng thật bằng trình duyệt: lọc Style=`146N216` ra đúng 4 MO với số liệu **khớp tuyệt đối** API/Excel (đối chiếu tay trước khi test); drill-down MO `5V2607331001` ra đúng 7 trolley khớp ví dụ đã biết ở CLAUDE.md mục 5.2; sort 2 chiều đúng; xuất CSV kích hoạt tải file; đổi EN, bật dark mode đều đúng; không lỗi console. `tsc`/ESLint/`next build` xanh; `pytest` xanh 76/76 (backend không đổi). |
| 2026-08-08 | Làm Bước 7: `logging_config.py` thêm `configure_logging()` bật `app.log`/`access.log`/`error.log` (giữ nguyên `data-events.log` từ Bước 3), gọi 1 lần trong `create_app()` nên có hiệu lực cả dev lẫn production. `backend/run_server.py` — điểm chạy ngầm bằng `pythonw`: gán lại `sys.stdout`/`sys.stderr` vào `crash.log` mở trực tiếp bằng `open()` (an toàn trước cả khi `Settings()` kịp đọc `.env`), bật `faulthandler`, ghi PID vào `logs/flap.pid`, gọi `uvicorn.run(..., reload=False, workers=1)`. `main.py`: thêm `configure_logging()` + logger `flap.app` ghi start/stop watcher; thêm `app.mount("/", StaticFiles(directory="frontend/out", html=True))` **sau cùng** (không che `/api/*`); thêm router `routes_system`. `next.config.ts` thêm `trailingSlash: true` để `next build` xuất mỗi route thành thư mục + `index.html` (khớp cách `StaticFiles(html=True)` tự tìm `index.html`). Thêm `FLAP_SYSTEM_TOKEN` vào `config.py`/`.env`/`.env.example`, `api/routes_system.py` (`GET /api/system/status?token=...`, tắt hẳn 503 nếu chưa cấu hình token, 403 nếu token sai — bảo vệ vì log chứa tên thật nhân viên) trả trạng thái watcher/uptime/snapshot + tail 200 dòng mỗi file log. Trang `frontend/src/app/pc/system/page.tsx`: nhập token (lưu `localStorage`, không tự nạp lúc mount — phải bấm "Mở khoá" 1 lần, tránh vi phạm `react-hooks/set-state-in-effect`), tự làm mới 15s sau khi xác thực. Viết đủ `scripts/`: `dev-backend.ps1`/`dev-frontend.ps1` (venv Python + Node ngoài PATH), `build-and-serve.ps1` (build tĩnh + chạy production trong 1 cửa sổ để kiểm tra tay), `start.cmd`/`stop.cmd`/`restart.cmd` (pythonw nền + PID file, không cần cửa sổ Terminal), `install-task.ps1` (đăng ký Task Scheduler "FLAP Dashboard", mặc định trigger "khi đăng nhập" không cần Admin; cờ `-RunWithoutLogon` thử kiểu "chạy cả khi chưa đăng nhập" — vẫn **chưa kiểm chứng** có bị domain policy chặn không, để lại cho Bước 0), `firewall-rule.ps1` (đưa IT chạy, mở TCP 8080 Domain/Private). ⚠️ **2 bug thật phát hiện khi kiểm chứng bằng server production thật** (`pytest` không bắt được vì cả hai chỉ lộ khi `next build` + `uvicorn.run()` thật chạy cùng nhau): (1) Next.js (`trailingSlash: true`) xuất trang lỗi thành `out/404/index.html`, nhưng Starlette `StaticFiles(html=True)` chỉ tự tìm file **phẳng** `404.html` ở gốc thư mục khi 404 (xem `starlette/staticfiles.py`, không tìm theo thư mục như các route khác) — trang 404 tuỳ chỉnh không bao giờ hiện, rơi về JSON mặc định của FastAPI; sửa bằng cách copy `out/404/index.html` → `out/404.html` trong `build-and-serve.ps1` sau mỗi lần build. (2) `uvicorn.run()` mặc định tự `dictConfig` lại logging **sau khi** `app.main` đã import xong (tức sau `configure_logging()` chạy trong `create_app()`) — ghi đè mất handler ghi vào `access.log` của logger `uvicorn.access` bằng handler console mặc định của uvicorn; request vẫn chạy đúng, `access.log` chỉ đơn giản **rỗng vĩnh viễn, không lỗi, không cảnh báo**; sửa bằng `uvicorn.run(..., log_config=None)` ở cả `run_server.py` và khối `__main__` dev của `main.py`. Kiểm chứng **thật 100%**: `pytest` xanh 76/76 sau các đổi trên; `next build` xuất đúng `out/{,tv/wip,pc/wip,pc/system}/index.html`; chạy `run_server.py` thật (port tạm 8091 vì 8080 đang bị một socket "ma" — PID không còn tồn tại nhưng Windows vẫn giữ ở trạng thái LISTENING, xem rủi ro mới ở mục 6) — `GET /`, `/tv/wip`, `/pc/wip`, `/pc/system` đều 200 phục vụ đúng file tĩnh; `GET /api/wip/kpi` 200; `GET /api/system/status?token=đúng` 200 kèm `watcher_running: true` + tail log đúng dấu tiếng Việt qua JSON (`"khởi động"` giữ nguyên, mojibake chỉ là artefact hiển thị của PowerShell `Get-Content`, không phải lỗi file); `?token=sai` → 403; `FLAP_SYSTEM_TOKEN` rỗng → 503; route lạ → 404 đúng trang tĩnh; `/api/stream` mở đúng `text/event-stream`. `app.log`/`access.log`/`error.log`/`data-events.log` đều có nội dung đúng sau khi sửa bug #2. `git status` xác nhận `.gitignore` vẫn chặn đúng `out/`, `logs/`, `.env`. ⚠️ **Phát hiện ngoài phạm vi Bước 7:** toàn bộ code Bước 1–6 (`backend/`, `frontend/`, `scripts/`, `py_pack.md`, `.env.example`) **chưa từng được commit** — `git log` chỉ có đúng 1 commit từ Bước 0 (2026-08-03); không tự ý commit/push, để người dùng quyết định. |
| 2026-08-08 (2) | Thiết kế lại giao diện `/tv/wip` theo 3 yêu cầu liên tiếp của người dùng (chi tiết đầy đủ ở Bước 5 mục "Thiết kế lại giao diện TV"). (1) Gộp 4 khối tự xoay 12s thành 1 lưới tĩnh 1920×1080, đổi nền theo màu editor VS Code mặc định (`#1e1e1e`/`#252526`, xác nhận qua `settings.json` không có `workbench.colorTheme` tuỳ chỉnh), viết `components/tv/Card.tsx` dùng chung; `HorizontalBarChart`/`TrendChart` đổi hằng số kích thước cố định sang props để khớp lưới nhiều cột độ rộng khác nhau — kiểm chứng bằng ảnh chụp Edge headless thật (`playwright-core` cài tạm `--no-save`, gỡ ngay sau khi xong), `scrollWidth/Height` đúng 1920×1080. (2) Đổi nền sang Solarized Dark `#002B36`/`#073642` (base03/base02), thêm font Century Gothic (không phải web font miễn phí — chỉ khai `font-family`, trông cậy máy xem có cài sẵn, rơi về Verdana), tiêu đề trang song ngữ VI (dòng chính)/EN (dòng phụ) — **bug thật**: Verdana rộng hơn font cũ làm bảng Top 10 tràn 2 dòng/ô, sửa bằng đổi tỉ lệ cột `0.85fr 1.3fr 0.85fr`. Mỗi lần đổi nền đều chạy lại `validate_palette.js --surface <mới> --mode dark` — ramp tuổi WIP phải re-step lại vì bậc tối nhất không còn đạt 2:1 trên nền mới (`#184f95`→`#1c5cab`→`#9ec5f4→#256abf`, xem CLAUDE.md mục 6.3 mới). (3) Mở rộng song ngữ ra toàn bộ 6 card (kể cả 2 hero-figure — bỏ prop `label` khỏi `StatTile`, chuyển hẳn sang `Card` title/subtitle) và header 5 cột bảng Top 10 (2 dòng VI/EN mỗi cột); tăng cỡ chữ subtitle gần bằng title ở cả 3 nơi (tiêu đề trang, tiêu đề card, header cột) — bù lại bằng giảm đệm dọc card/dòng bảng để bảng vẫn đủ 10 dòng không bị cắt (`Card` nội dung dùng `overflow-hidden`, tràn sẽ bị cắt lặng lẽ chứ không lỗi). Cố ý **chưa** làm song ngữ nhãn dữ liệu trong biểu đồ (mã khu vực CCT/PDC/VAP, nhãn "0-3 ngày") — cột quá hẹp, thêm chữ sẽ tràn như bug bảng đã gặp. `pytest` không đổi (76/76, chỉ sửa frontend); build/lint sạch sau mọi bước. |

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
│     │  ├─ cache.py          # (chưa cần) đọc thẳng Excel mỗi request đủ nhanh với ~350 dòng; xem CLAUDE.md quyết định #7
│     │  ├─ watcher.py        # watchdog + debounce + retry
│     │  ├─ history.py        # ghi snapshot Parquet
│     │  └─ kpi.py            # tính KPI
│     └─ api/                 # routes_wip.py, routes_stream.py, routes_meta.py, routes_system.py
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

- [x] Tạo `.gitignore` loại trừ `EXCEL files/`, `*.xlsx`, `data/`, `logs/`, `.env`, `.venv/`, `node_modules/`, `wheelhouse/`
- [x] Viết `PLAN.md` và `CLAUDE.md` bằng tiếng Việt
- [x] Nối remote `https://github.com/nqhuy-212/FLAP.git`, commit đầu tiên, push
- [x] Viết `py_pack.md` — quy trình wheelhouse offline vì PyPI bị chặn
- [x] Tạo venv Python 3.13 + `requirements.txt` + `pytest.ini`
- [x] Nhận wheelhouse: **36 file `.whl`, 54,8 MB**, đúng `cp313`/`win_amd64`, không lẫn `.tar.gz`
- [x] Cài offline (`pip install --no-index --no-deps` từng wheel) rồi chạy `pytest` nghiệm thu Bước 1 — xanh 34/34
- [ ] ⚠️ **Vẫn thiếu `tzdata`** — không chặn app chạy (dự án chỉ dùng datetime naive), nhưng sẽ chặn `pip install -r requirements.txt` bình thường nếu không tải bổ sung. Xem [py_pack.md](py_pack.md)
- [x] Tạo `.env` + `.env.example` + `config.py` — làm ở Bước 2, mở rộng thêm ở Bước 3/4/6 (`history_dir`, `log_dir`, `cors_origins`)
- [x] Dựng `logging_config.py` — làm ở Bước 3 (logger `data-events.log`); `app.log`/`access.log`/`error.log`/`crash.log` còn lại nối vào Bước 7
- [ ] Dựng `run_server.py` chạy ngầm bằng `pythonw` — Bước 7

**Hai việc phụ thuộc bên ngoài — khởi động NGAY, chạy song song với code:**
- [ ] **Gửi ticket IT xin mở inbound firewall TCP 8080.** Việc duy nhất không kiểm soát được thời gian; để đến Bước 7 mới xin là quá muộn.
- [ ] **Thử Task Scheduler bằng một task giả** xem tuỳ chọn *"Run whether user is logged on or not"* có bị domain policy chặn không.

**Việc dọn dẹp đã làm:**
- [x] Thêm `*.7z` vào `.gitignore` — file `wheelhouse.7z` **53,8 MB** ở gốc dự án đã được chặn, không lo vượt ngưỡng cảnh báo 50 MB của GitHub

*Nghiệm thu:* `git ls-files` không có `.xlsx`, không có `.env`, không có file nén wheelhouse.

### Bước 1 — Nhân đọc & chuẩn hoá Excel + kiểm thử đối chiếu ✅

| File | Kích thước | Vai trò |
|---|---|---|
| `app/core/excel_utils.py` | 4,4 KB | serial→datetime, `"NULL"`→None, tách list, bỏ banner |
| `app/datasource/base.py` | 1,4 KB | Protocol `DataSource` |
| `app/datasource/excel_source.py` | 5,2 KB | Đọc `WIP Report_1.1` |
| `app/models/wip.py`, `meta.py`, `other.py` | 2,7 KB | Pydantic schema |
| `tests/test_excel_utils.py` | 3,2 KB | Test hàm thuần |
| `tests/test_excel_source.py` | 6,8 KB | Test đối chiếu `WIP_Sammary` |

**Test đối chiếu** là phần giá trị nhất: tự tính từ `WIP_Detail` rồi so với `WIP_Sammary` cho **toàn bộ 36 MO**, không chỉ 1 mẫu. Bắt được đúng loại lỗi nguy hiểm nhất — sai mẫu số khi tính trung bình, ra số sai mà không báo lỗi rồi hiện thẳng lên TV xưởng.

`pytest` chạy xanh **34/34** ngay lần đầu dù wheelhouse có **pandas 3.0.5** (bản major mới) — không phải sửa code nào.

*Nghiệm thu:* `pytest` xanh (34/34); đọc ra **347 dòng dữ liệu** `WIP_Detail` (không phải 352 — con số đó trong bảng khảo sát CLAUDE.md mục 4 là tổng dòng vật lý của sheet, tính cả 5 dòng banner/header; 41 dòng vật lý `WIP_Sammary` → 36 dòng dữ liệu) với ngày tháng đã là datetime thật.

### Bước 2 — API WIP + KPI ✅

`config.py` (pydantic-settings, đọc `.env` ở gốc dự án — biến `FLAP_PORT`/`FLAP_DATA_DIR`/`FLAP_BASE_PATH`/`FLAP_DATASOURCE`), `models/kpi.py`, `services/kpi.py`, `api/deps.py`, `api/routes_wip.py`, `api/routes_meta.py`, `main.py`.

Endpoint: `GET /api/wip/detail`, `GET /api/wip/summary`, `GET /api/wip/kpi`, `GET /api/meta/health` (gộp cả `SnapshotInfo` — không tách route riêng vì PLAN chỉ định đúng 4 URL này).

KPI (toàn bộ COMPUTED, xem CLAUDE.md mục 5.3 — thuần Python trên `list[WipTrolley]`, không phụ thuộc Excel hay SQL nên giữ nguyên khi đổi DataSource ở Bước 9):
- Tổng trolley + tổng sản lượng đang tồn
- Phân bổ theo khu vực (`area_breakdown`, nhóm cả trolley không có Area — có thật trong dữ liệu, 5 dòng)
- Nhóm tuổi WIP 0–3/4–7/8–14/>14 ngày — **quy tắc quan trọng:** tuổi = cột `Wip_CCT`/`Wip_VAP`/`PDC_WIP` khớp đúng `Area` hiện tại của trolley, không phải cả 3 cột cộng lại (trolley có đủ cả 3 cột nhưng chỉ cột khớp Area phản ánh đúng "đang chờ ở đây bao lâu")
- Top 10 style-MO tồn lâu nhất — xếp theo tuổi lớn nhất (`max`) trong các trolley cùng MO
- Xu hướng theo `Loading Date` (gộp theo ngày, bỏ giờ)

⚠️ **2 bug chỉ lộ khi chạy server thật, `pytest` không bắt được** (test dùng object Python thuần, không đi qua bước serialize JSON của FastAPI) — đã sửa, thêm test hồi quy:
1. `/api/wip/detail` lỗi 500: cột ngày trống (`In Vap Date`) được pandas parse thành `NaT` — mà `pandas.NaT` là **subclass của `datetime`**, lọt qua nhánh passthrough `isinstance(value, datetime)` trong `excel_serial_to_datetime` thay vì bị nhận diện là rỗng. Sửa: kiểm tra `pd.isna()` trước tiên.
2. `Area`/`wbCode` có ô trống thật (5 và 4 dòng trong 347 dòng) nhưng bị `str(clean_null(x))` ép thành **chuỗi `"None"`** thay vì `None` thật — hiện sai lên `area_breakdown` (`"area": "None"`). Sửa: đổi 2 trường này thành `str | None` trong model, bỏ `str(...)` khi gán.

*Nghiệm thu:* `pytest` xanh 55/55; mở `http://localhost:8080/docs`, gọi thật cả 4 endpoint — `/api/wip/detail` trả 347 dòng, `/api/wip/summary` trả 36 dòng, `/api/wip/kpi` ra số hợp lý (tổng 347 trolley / 110.209 sản lượng, top aging cao nhất 35 ngày), `/api/meta/health` trả `status: "ok"` kèm `SnapshotInfo`.

### Bước 3 — Realtime + lưu lịch sử ✅

`core/events.py` (EventBus in-memory, `publish()` an toàn gọi từ thread khác qua `call_soon_threadsafe` — watcher chạy trên thread riêng của watchdog), `services/watcher.py` (watchdog + debounce 2s + hash SHA-256 nội dung + retry `PermissionError` + bỏ qua `~$*.xlsx` + poll dự phòng 30s), `GET /api/stream` (`api/routes_stream.py`, SSE thủ công qua `StreamingResponse` — không thêm dependency, heartbeat 15s).

**Chỉ `WIP Report_1.1.xlsx` kích hoạt lưu Parquet** (`services/history.py`, ghi cả `WipTrolley` lẫn `WipSummary`) — 4 file Excel còn lại watcher vẫn theo dõi và bắn `data_changed` bình thường (kiến trúc chung cho cả 5 file), nhưng chưa gọi `get_delivery_trolleys()`/... vì các entity đó chưa hiện thực (Bước 8, sẽ raise `NotImplementedError`).

⚠️ **Không dùng được `FastAPI TestClient` để test SSE tự động** — thiếu gói `httpx` trong wheelhouse (xem [py_pack.md](py_pack.md)). Thay bằng: (1) `pytest` cho toàn bộ phần thuần Python (`EventBus`, debounce/hash logic của watcher, `save_wip_snapshot`) bằng test double + `tmp_path`, không đụng watchdog Observer thật; (2) kiểm chứng SSE + Parquet + log **thật 100%** bằng server phụ trỏ vào bản sao tạm của `WIP Report_1.1.xlsx` (không đụng "EXCEL files/" gốc — mục 3 cấm ghi vào đó), `curl` mở `/api/stream`, sửa bản sao bằng `openpyxl` để mô phỏng MES xuất lại.

*Nghiệm thu:* `pytest` xanh 70/70; copy đè file Excel → sự kiện `data_changed` bắn ra trong ~2s (đã đo thật), có 2 file Parquet mới (`wip_detail_*.parquet`, `wip_summary_*.parquet`) trong `data/history/`, `logs/data-events.log` ghi đúng tên file + hash + thời điểm.

### Bước 4 — Nền frontend ✅

⚠️ **Next.js thật là 16.3.0, không phải 15** — dự án luôn `npm create next-app@latest` nên tự nhận bản mới nhất tại thời điểm cài. Bản này tự sinh `frontend/AGENTS.md` cảnh báo AI có breaking change so với dữ liệu huấn luyện, yêu cầu đọc `node_modules/next/dist/docs/` trước khi viết code — đã làm, các API dùng trong dự án (`output:'export'`, `basePath`, `images.unoptimized`) không đổi so với hiểu biết cũ, chỉ khác cú pháp `LayoutProps<"/">`/`PageProps<...>` cho type của layout/page.

`frontend/` (App Router, TypeScript, Tailwind v4, shadcn/ui — Button/Card/Badge) + `src/i18n/context.tsx` (VI/EN qua React Context + JSON, không dùng thư viện ngoài) + `src/lib/api.ts` + `src/lib/types.ts` (khớp Pydantic models backend) + `src/lib/useLiveData.ts` (bọc `EventSource`, trạng thái `connecting`/`connected`/`disconnected`).

`next.config.ts`: `output: 'export'`, `images.unoptimized: true`, đọc `FLAP_BASE_PATH` **trực tiếp từ `.env` gốc** (không tách biến riêng cho frontend — một nguồn sự thật duy nhất, đúng tinh thần CLAUDE.md mục 10).

⚠️ **`.env.local` bị `next build` nạp giống hệt `next dev`** (khác kỳ vọng ban đầu) — biến `NEXT_PUBLIC_API_BASE_URL` dùng cho dev (`http://localhost:8080`) phải để trong `frontend/.env.development.local` (chỉ nạp khi `NODE_ENV=development`), nếu không bundle production sẽ đóng băng nhầm URL dev thay vì dùng đường dẫn tương đối cùng origin.

⚠️ **CORS cần bật cho dev** — `next dev` (port 3000) và backend (port 8080) khác origin nên trình duyệt chặn hết fetch/EventSource. Thêm `CORSMiddleware` + `FLAP_CORS_ORIGINS` (mặc định `http://localhost:3000`) vào `backend/app/config.py` + `main.py`. Production không cần vì cùng origin (quyết định #3).

*Chỉ dịch nhãn giao diện* — giá trị dữ liệu từ MES như `Color_Name` = "69 NAVY" hay tên nhân viên giữ nguyên.

*Nghiệm thu:* kiểm chứng thật bằng trình duyệt headless (Edge cài sẵn trên máy, điều khiển qua `playwright-core` — không cần tải Chromium) chạy song song `next dev` (3000) và backend thật (8080): trang hiển thị đúng **347 trolley / 110.209 sản lượng**; bấm EN đổi toàn bộ nhãn ngay lập tức; badge trạng thái hiện "Đã kết nối"/"Connected"; `console --errors` rỗng. Ảnh chụp màn hình xác nhận cả 2 ngôn ngữ.

⚠️ **Bug thật thứ 3 phát hiện sau khi ghi biến vào `.env`:** khai `cors_origins: list[str]` khiến
`Settings()` lỗi ngay lúc khởi tạo — pydantic-settings tự parse env var kiểu `list` bằng JSON *trước khi*
`field_validator` chạy, nên `FLAP_CORS_ORIGINS=http://localhost:3000` (chuỗi phân tách dấu phẩy thường,
không phải JSON) làm vỡ toàn bộ app. Chỉ lộ ra khi biến thật sự có mặt trong `.env` — lúc test bằng
default Python (`["..."]"`) thì không sao vì pydantic-settings không đụng tới nguồn env khi biến không tồn
tại. Sửa: khai `cors_origins: str`, thêm property `cors_origins_list` tự tách. Thêm `tests/test_config.py`.
`pytest` xanh 76/76.

### Bước 5 — Dashboard TV: WIP Overview (MVP hoàn chỉnh) ✅

`app/tv/wip/page.tsx`: layout 1920×1080 cố định (`w-[1920px] h-[1080px]`, `overflow-hidden`), nền tối
(`#0d0d0d`/`#1a1a19` — palette dark tham chiếu của skill `dataviz`), chữ lớn, **không thanh cuộn** (đã kiểm
`scrollHeight`/`scrollWidth` bằng script thật = false), tự xoay 4 khối mỗi 12 giây (Tổng quan → Nhóm tuổi
WIP → Top 10 tồn lâu → Xu hướng), đèn báo kết nối + dấu thời gian cập nhật cuối, ngôn ngữ đọc từ URL
(`?lang=vi`/`?lang=en`, qua `useSearchParams` bọc `<Suspense>` — bắt buộc để `next build` static export
không lỗi).

4 component biểu đồ thuần SVG (`components/tv/`): `HorizontalBarChart` (phân bổ khu vực — 1 hue phẳng vì
category không thứ tự; nhóm tuổi WIP — ordinal ramp `#86b6ef→#184f95` vì có thứ tự tự nhiên, đã
`validate_palette.js --ordinal` PASS), `TrendChart` (đường + vùng cho xu hướng theo ngày, nhãn trực tiếp
chỉ ở điểm cuối), `TopAgingTable` (bảng — đúng quy tắc "table không phải chart" cho dữ liệu >~7 lớp),
`StatTile` (hero figure cho tổng trolley/sản lượng).

⚠️ **Bug thật nghiêm trọng nhất từ đầu dự án — SSE rớt kết nối im lặng sau một thời gian chạy.** Kiểm
chứng "sửa Excel → TV tự đổi" lần đầu **thất bại**: backend log đúng đã phát hiện đổi + lưu snapshot,
nhưng không client nào (kể cả `curl`, không riêng browser) nhận được `data_changed`. Nguyên nhân:
`uvicorn.run(..., reload=True)` không truyền `reload_dirs` → mặc định theo dõi **toàn bộ** `backend/` kể
cả `.venv/`; cache `.pyc` sinh ra khi thư viện chạy lần đầu (vd `pyarrow`) bị hiểu nhầm là đổi code, worker
bị restart ngầm, `EventBus` trong RAM mất theo — không lỗi, không log, chỉ đơn giản im lặng mất kết nối.
Sửa: `reload_dirs=["app"]` trong `main.py`. Xem CLAUDE.md quyết định #9.

*Nghiệm thu:* mở `http://localhost:3000/tv/wip?lang=vi` — không thanh cuộn, tự xoay đúng 4 khối, số liệu
khớp Bước 2 (347 trolley, 110.209 sản lượng, đúng breakdown/age-bucket/top-aging/trend). Sửa file Excel
(bản sao tạm, không đụng `EXCEL files/` gốc) → **số trên TV tự đổi tại T=2s, không F5, không gọi lại
`reload()` thủ công** — đã đo bằng trình duyệt Edge headless thật (`playwright-core`), có ảnh chụp màn
hình trước/sau xác nhận.

#### Thiết kế lại giao diện TV (2026-08-08, theo yêu cầu người dùng sau khi Bước 5 đã "xong")

Đổi hẳn cách trình bày so với mô tả gốc ở trên — không còn tự xoay 4 khối, và bảng màu/font khác hẳn
palette dark tham chiếu ban đầu của skill `dataviz`. Chi tiết đầy đủ nằm ở nhật ký (mục dưới); tóm tắt:

- **Gộp 4 khối thành 1 lưới tĩnh** 1920×1080 (bỏ hẳn `panelIndex`/`ROTATE_INTERVAL_MS`) — `Card` component
  dùng chung (mới, `components/tv/Card.tsx`) cho cả 6 khối (2 hero figure + 4 biểu đồ).
- **Bảng màu đổi 2 lần theo yêu cầu**: đầu tiên khớp nền editor VS Code mặc định (`#1e1e1e`/`#252526`),
  sau đó đổi hẳn sang Solarized Dark (`#002B36`/`#073642` — đúng cặp base03/base02 của bảng Solarized).
  Mỗi lần đổi nền đều chạy lại `validate_palette.js --surface <nền mới> --mode dark` cho `singleSeries` và
  `AGE_BUCKET_RAMP` — bậc tối nhất của ramp phải đổi lại **2 lần** vì mỗi nền mới có độ sáng khác, bậc cũ
  không còn đạt tương phản 2:1 (từ `#184f95` → `#1c5cab` → ramp giãn rộng hơn `#9ec5f4→#256abf`).
- **Font Century Gothic** — không phải web font miễn phí (bản quyền Monotype, không có trên Google Fonts)
  nên không nhúng qua `next/font` được, chỉ khai `font-family` thẳng và trông cậy máy xem có cài sẵn (thường
  qua MS Office), rơi về Verdana nếu không có (`TV_FONT_FAMILY` trong `colors.ts`).
- **Song ngữ toàn bộ tiêu đề**: tiêu đề trang, tiêu đề cả 6 card, header 5 cột bảng Top 10 — đều hiện cả
  VI (dòng chính) lẫn EN (dòng phụ, cỡ chữ gần bằng dòng chính) **cùng lúc**, độc lập với `?lang=` (thứ chỉ
  còn điều khiển đơn vị số liệu và nhãn dữ liệu bên trong biểu đồ, cố ý chưa làm song ngữ — xem lý do bug bên dưới).
- Các component biểu đồ (`HorizontalBarChart`, `TrendChart`) đổi từ hằng số kích thước cố định sang nhận
  `width`/`height`/font-size qua **props** — bắt buộc vì lưới mới có nhiều cột độ rộng khác nhau, không
  còn dùng chung 1 kích thước full-width như thiết kế xoay khối cũ.

⚠️ **Bug thật gặp khi đổi font:** Century Gothic/Verdana rộng hơn đáng kể so với font mặc định cũ, làm
bảng Top 10 tràn xuống 2 dòng mỗi ô (phát hiện qua ảnh chụp thật, không phải lỗi kiểu/logic). Sửa bằng
đổi tỉ lệ cột hàng 2 từ 3 cột đều nhau sang `0.85fr 1.3fr 0.85fr` (nhường bảng nhiều chỗ hơn) + giảm nhẹ
đệm dọc mỗi dòng bảng.

*Nghiệm thu (redesign):* build sạch (`tsc`/ESLint/`next build`); chụp màn hình thật qua Edge headless
(`playwright-core` cài tạm bằng `npm install --no-save`, gỡ lại ngay sau khi xong — không đọng trong
`package.json`) ở cả bản VI mặc định lẫn `?lang=en`; `scrollWidth`/`scrollHeight` đúng 1920×1080 (không
tràn, không cuộn) sau mọi lần đổi; số liệu vẫn khớp Bước 2 xuyên suốt các lần chỉnh.

### Bước 6 — Dashboard PC tương tác ✅

`app/pc/wip/page.tsx` + `components/pc/{FilterBar,SummaryTable,DetailTable,SortableHead}.tsx` +
`lib/{useSortableData,csv,theme}.ts(x)`.

**Kiến trúc lọc — quyết định quan trọng:** bộ lọc (khoảng ngày, style, màu, khu vực, workstation) áp lên
**entity thô** `WipTrolley` (chỉ nơi này có đủ cả 5 chiều dữ liệu), từ tập trolley còn lại suy ra tập
`mo_no` đang hiển thị, rồi lọc **bảng tổng hợp theo tập `mo_no` đó nhưng giữ nguyên số liệu SOURCE** từ
`WipSummary` (`Cut_Qty`/`Deduct_Qty`/`Qty_After_Deduct`/`Total_Qty`... không tính lại) — đảm bảo khi lọc
chỉ theo Style, số liệu hiển thị khớp tuyệt đối với `WIP_Sammary` trong Excel (đúng CLAUDE.md mục 5.3:
SOURCE không được tái tạo). Click 1 dòng tổng hợp → drill-down bảng chi tiết trolley của đúng MO đó (áp
lại các filter khác), có nút quay lại. Bảng sắp xếp 2 chiều theo mọi cột (client-side, dữ liệu chỉ ~350
dòng nên không cần sort ở backend). Xuất CSV theo đúng bảng đang xem (tổng hợp hoặc chi tiết đã lọc), có
BOM để Excel đọc đúng dấu tiếng Việt. Nút VI/EN dùng lại `useI18n()` Context (khác TV — PC thao tác được
nên dùng nút bấm, không qua URL). Sáng/tối: `ThemeProvider` toggle class `.dark` trên `<html>` — Tailwind
v4 đã có sẵn toàn bộ theme tối từ lúc `shadcn init` ở Bước 4 (`@custom-variant dark`), không cần cấu hình
thêm.

*Nghiệm thu:* lọc một style, số liệu khớp với bản tổng hợp trong Excel.

### Bước 7 — Triển khai LAN + chạy ngầm 🟡

**Đã làm (code + script, kiểm chứng thật trên localhost):**
- `frontend/next.config.ts`: `trailingSlash: true` — `next build` xuất mỗi route thành `<route>/index.html`, khớp cách Starlette `StaticFiles(html=True)` tự tìm `index.html` theo thư mục.
- `backend/app/main.py`: `app.mount("/", StaticFiles(directory="frontend/out", html=True))` đăng ký **sau cùng** (sau mọi `include_router`) nên không che `/api/*`; nhúng chung FastAPI đúng quyết định #3 (1 port).
- `backend/run_server.py`: điểm chạy ngầm bằng `pythonw` — xử lý bẫy `sys.stdout is None` (CLAUDE.md mục 6.1) bằng cách gán lại `sys.stdout`/`sys.stderr` vào `crash.log` (mở trực tiếp bằng `open()`, không qua `logging_config.py`, để an toàn trước cả khi `Settings()` kịp đọc `.env`) là việc **đầu tiên** trong file, trước mọi import khác; bật `faulthandler`; ghi PID vào `logs/flap.pid`; `uvicorn.run(..., reload=False, workers=1, log_config=None)` — 1 worker cố ý (quyết định #9).
- `backend/app/logging_config.py`: thêm `configure_logging()` bật `app.log` (30 ngày)/`access.log` (14 ngày)/`error.log` (90 ngày, mọi logger WARNING+), gọi 1 lần trong `create_app()` nên có hiệu lực cả dev (`python -m app.main`) lẫn production (`run_server.py`).
- Trang `/pc/system` (`frontend/src/app/pc/system/page.tsx` + `backend/app/api/routes_system.py`): xem trạng thái (datasource, uptime, watcher có chạy không, `SnapshotInfo`) và tail 200 dòng mỗi file log **không cần Terminal** — bảo vệ bằng `FLAP_SYSTEM_TOKEN` (query param, `hmac.compare_digest`) vì log chứa **tên thật nhân viên** (`Relaxed_3.1.xlsx`); token rỗng ở backend → 503 (tắt hẳn, không mặc định mở); token sai → 403.
- `scripts/`: `dev-backend.ps1`/`dev-frontend.ps1` (venv Python + Node ngoài PATH, xem CLAUDE.md mục 3); `build-and-serve.ps1` (build tĩnh + chạy production trong 1 cửa sổ, kèm bước copy `out/404/index.html` → `out/404.html` — xem bug #1 ở nhật ký); `start.cmd`/`stop.cmd`/`restart.cmd` (pythonw nền + PID file, không cửa sổ Terminal); `install-task.ps1` (đăng ký Task Scheduler **"FLAP Dashboard"**, mặc định trigger "khi đăng nhập" không cần Admin; cờ `-RunWithoutLogon` cho kiểu "chạy cả khi chưa đăng nhập", chưa kiểm chứng thật); `firewall-rule.ps1` (đưa IT chạy, `New-NetFirewallRule` mở TCP 8080 profile Domain/Private).

**Còn lại — phụ thuộc bên ngoài, không tự làm được từ agent này:**
- [ ] Gửi/theo dõi ticket IT xin mở firewall TCP 8080 thật (`scripts/firewall-rule.ps1` cần IT chạy với quyền Admin) — vẫn là việc tồn đọng từ Bước 0.
- [ ] Chạy `scripts/install-task.ps1` thật trên máy, xác nhận Task Scheduler khởi động đúng lúc đăng nhập; thử cờ `-RunWithoutLogon` xem domain policy có chặn không (Bước 0 chưa làm).
- [ ] Kiểm chứng full reboot: khởi động lại PC → dashboard tự chạy không cửa sổ Terminal; `taskkill` tiến trình → Task Scheduler tự bật lại trong 1 phút.
- [ ] Mini PC nối TV chạy Chrome kiosk (`--kiosk --noerrdialogs --disable-session-crashed-bubble`), tự mở khi khởi động.
- [ ] Máy khác thật trong LAN mở `http://192.168.156.46:8080/tv/wip` — chưa thử được vì cổng 8080 trên máy dev đang bị một socket "ma" chiếm giữ (xem mục 6 rủi ro mới), cần kiểm tra bằng cổng khác hoặc sau khi khởi động lại máy.

*Nghiệm thu (đã đạt trên localhost, cổng tạm 8091):* `GET /`, `/tv/wip`, `/pc/wip`, `/pc/system` phục vụ đúng file tĩnh qua FastAPI (không cần `next dev`); `/api/*` không bị static mount che; `/api/stream` vẫn mở đúng `text/event-stream`; `app.log`/`access.log`/`error.log`/`data-events.log` đều có nội dung UTF-8 đúng; trang 404 tĩnh hiển thị đúng thay vì JSON mặc định; `/pc/system` đúng: token đúng → 200 + số liệu khớp, token sai → 403, token rỗng ở backend → 503. *Nghiệm thu đầy đủ (khởi động lại PC, LAN thật, kiosk) còn chờ các việc phụ thuộc bên ngoài ở trên.*

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
| **Cổng TCP 8080 bị "socket ma" chiếm giữ** trên máy dev (phát hiện Bước 7, 2026-08-08): `netstat` báo `LISTENING` bởi 1 PID, nhưng `Get-Process`/`tasklist` xác nhận PID đó **không còn tồn tại** — không phải tiến trình FLAP, không nằm trong dải `netsh excludedportrange`. Chưa rõ do đâu (nghi socket kernel bị treo sau 1 lần tắt tiến trình đột ngột) | 🟡 Thấp | Không có quyền Admin nên không tự reset bảng socket được; thử lại sau khi khởi động lại máy trước khi triển khai thật lên cổng 8080. Không chặn phát triển — dùng cổng tạm (`$env:FLAP_PORT`) để kiểm thử |
| **Code Bước 1–6 chưa từng được commit** (phát hiện Bước 7, 2026-08-08): `git log` chỉ có 1 commit từ Bước 0; toàn bộ `backend/`, `frontend/`, `scripts/` đang ở trạng thái untracked | 🟠 Vừa | Không tự ý commit — hỏi người dùng trước; khi commit phải kiểm tra lại `git ls-files \| Select-String '\.xlsx$\|\.env$'` theo đúng mục 8 CLAUDE.md trước khi push |
