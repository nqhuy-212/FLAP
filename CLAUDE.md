# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **Ngôn ngữ làm việc: tiếng Việt.** Tài liệu, commit message và trao đổi với người dùng đều bằng tiếng Việt.
> Lộ trình và tiến độ nằm ở [PLAN.md](PLAN.md). File này chứa **kiến thức nền** cần có để làm việc.

---

## 1. Dự án là gì

Dashboard theo dõi sản xuất cho **Regent Garment Factory Ltd** (công ty con của Crystal International Group), nhà máy may tại Việt Nam. Tự host trên một PC Windows 11, chia sẻ trong LAN nhà máy.

- **Giai đoạn 1:** đọc dữ liệu từ 5 file Excel xuất thủ công từ hệ thống MES/WMS.
- **Giai đoạn 2:** chuyển sang SQL Server mà **không phải sửa frontend** — nhờ lớp trừu tượng `DataSource`.

Hai nhóm màn hình: `/tv/*` cho TV treo tường (không thao tác) và `/pc/*` cho người dùng lọc, phân tích.

---

## 2. Quy ước làm việc bắt buộc

1. **Sau mỗi bước** trong `PLAN.md`: cập nhật `PLAN.md` (tiến độ, nhật ký) và `CLAUDE.md` (cấu trúc, schema, công nghệ mới và lý do dùng), rồi **dừng lại chờ người dùng xác nhận** mới sang bước tiếp theo.
2. **Không bao giờ commit dữ liệu nhà máy.** Xem mục 8.
3. **Không ghi vào thư mục `EXCEL files/`** — nguồn dữ liệu chỉ đọc.
4. Mọi thông số môi trường đi qua `.env`, không hardcode.

---

## 3. Môi trường máy (đã kiểm tra thực tế 2026-08-03)

| Hạng mục | Kết quả |
|---|---|
| Python | 3.13.2 + pip 25.0.1 — `%LOCALAPPDATA%\Programs\Python\Python313\python.exe` (**không trong PATH**) |
| Node / npm | v24.11.0 / 11.6.1 — `D:\2025 nqhuy\Setup\node-v24.11.0-win-x64\` |
| git | 2.48.1 — `%LOCALAPPDATA%\Programs\Git\cmd\git.exe` (**không trong PATH**) |
| pythonw.exe | Có — dùng để chạy ngầm không cửa sổ console |
| **Quyền Admin** | **KHÔNG có** — không tự mở được firewall |
| Firewall | Bật cả Domain / Private / Public |
| SQL Server | SQLEXPRESS đang chạy + ODBC Driver 17 for SQL Server |
| Docker / Nginx | Chưa cài, và **không cần** (xem mục 6) |
| IP LAN | `192.168.156.46` (Ethernet 3), hostname `RG2RDD2875` |
| Shell | Windows PowerShell 5.1 — **không có** `&&`, `??`, `?:` |

**Hệ quả quan trọng:** Python, Node và git đều không nằm trong PATH → luôn gọi bằng đường dẫn đầy đủ hoặc qua script trong `scripts/`. Đường dẫn dự án có dấu cách → luôn đặt trong dấu nháy kép.

### Cấp phát port

| Port | Dự án |
|---|---|
| 8080 | **FLAP** (dự án này) |
| 8081, 8082… | Dành cho dashboard khác sau này |

---

## 4. Dữ liệu nguồn

5 file trong [EXCEL files/](EXCEL%20files/), xuất **thủ công, không đều** từ MES/WMS. Dữ liệu hiện tại trải từ cuối 07/2026 đến đầu 08/2026.

| File | Sheet | Số dòng | Nội dung |
|---|---|---|---|
| `WIP Report_1.1.xlsx` | `WIP_Detail`, `WIP_Sammary` *(sic)* | 352 / 41 | Tồn WIP theo trolley, mốc thời gian `Loading Date` → `In Vap Date` → `Back CCT Date`, bộ đếm tuổi `Wip_CCT`/`Wip_VAP`/`PDC_WIP` (ngày) |
| `DeliveryPanel_2.1.xlsx` | `TotalTrolley` | 26 | Trolley giao từ CCT sang VAP, `WorkCenter` (Printing / Heat transfer), cờ `IsRework` |
| `Heat_7.1.xlsx` | `Sheet1`, `Sheet2` | 101 / 5.166 | Sheet1: log lỗi vật tư kèm cột `ResultJson` chứa mảng JSON. Sheet2: log cấp phát nhãn nhiệt |
| `order_8.1.xlsx` | `SPD`, `PRT` | 17 / 14.465 | SPD: kế hoạch trải vải theo máy/bàn/cuộn. PRT: xác nhận lệnh in theo style/màu/vị trí |
| `Relaxed_3.1.xlsx` | `Sheet1` | 47.437 | Log xả vải theo cuộn, pallet, bin, tên nhân viên |

### 4.1 Các bẫy dữ liệu — nguyên nhân gây sai số âm thầm

Tất cả đã được kiểm chứng trực tiếp trên file:

- **Ngày giờ là số serial Excel thô** (vd `46234.748997`), hệ 1900 (không có cờ `date1904`).
  → `datetime(1899, 12, 30) + timedelta(days=serial)`
- **Ô trống là chuỗi `"NULL"`**, không phải cell rỗng. Lọc theo blank sẽ không bắt được.
- **Hai kiểu bố cục sheet:**
  - `WIP Report_1.1` và `DeliveryPanel_2.1`: 4 dòng banner đầu (tên công ty, tiêu đề, ngày giờ xuất), **header ở dòng 5, dữ liệu từ dòng 6**.
  - `Heat_7.1`, `order_8.1`, `Relaxed_3.1`: header ở dòng 1.
- **`Heat_7.1` Sheet2 là bảng join bị làm phẳng** → tên cột trùng nhau (`RID` ở cột C và AS, `Issue_Qty` ở B/O/BJ, `SO_Color_Code` ở F và AW, `Goods_Category` ở K và BA). **Phải lấy theo vị trí cột, không theo tên** — tra theo tên sẽ âm thầm lấy nhầm cột. Dòng nào toàn bộ cột AS–BZ là `NULL` là dòng master không có detail khớp.
- **Ô chứa nhiều giá trị:** `Bed_No` và `Size_NO` chứa danh sách ngăn bằng dấu phẩy (`"34003,34004"`, `"3XL,4XL,XXL"`). Muốn thống kê theo size phải tách trước.
- **Tên nhân viên tiếng Việt có dấu** (`NGÔ VĂN KHỞI`, `ĐINH TRỌNG NGỌC`) → đọc/ghi UTF-8 xuyên suốt, log cũng phải UTF-8.
- **`Relaxed_3.1`: `End_Date` luôn bằng `Start_Date` + đúng 1.0** → đây là cửa sổ xả vải 24 giờ được suy ra, không phải mốc thời gian quan sát được.

### 4.2 Mô hình nghiệp vụ

Luồng sản xuất: **cuộn vải → trải/cắt (bed) → trolley panel → CCT (in / ép nhiệt) → VAP → PDC**

Khoá liên kết, xếp theo độ chọn lọc giảm dần:

| Khoá | Ví dụ | Ý nghĩa |
|---|---|---|
| `Trolley_Code` | `201507` | Xe chứa panel — đơn vị được theo dõi qua WIP |
| `MO_No` | `5L2608015008` | Lệnh sản xuất = `SO_No` + 3 số |
| `SO_No` | `5L2608015` | Đơn hàng — **khoá duy nhất có mặt ở cả 5 file** |
| `Cust_Style` + `Flower_Code` + `Color_Code` + `Size_NO` | `346N597` + `D` + `00W` + `XL` | Xác định một SKU-hình in cụ thể |
| `wbCode`, `WS_Code` | `2CM0421`, `24LOD_05`, `2PRT_231` | Mã bundle / trạm làm việc |

---

## 5. Hợp đồng `DataSource` — trục xương sống của dự án

Đây là thứ gánh toàn bộ lời hứa *"Excel giờ, SQL sau"*. Mọi API **chỉ** được gọi qua interface này.

```python
class DataSource(Protocol):
    # === Loại 1: entity THÔ — ta tự tính mọi KPI từ đây ===
    def get_wip_trolleys(self)        -> list[WipTrolley]: ...
    def get_delivery_trolleys(self)   -> list[DeliveryTrolley]: ...
    def get_spread_plans(self)        -> list[SpreadPlan]: ...
    def get_print_orders(self)        -> list[PrintOrder]: ...
    def get_relax_rolls(self)         -> list[RelaxRoll]: ...
    def get_material_issues(self)     -> list[MaterialIssue]: ...
    def get_material_exceptions(self) -> list[MaterialException]: ...

    # === Loại 2: entity ĐÃ GỘP SẴN từ nguồn — KHÔNG tái tạo được ===
    def get_wip_summary(self)         -> list[WipSummary]: ...

    # === Siêu dữ liệu ===
    def get_snapshot_info(self)       -> SnapshotInfo: ...
```

### 5.1 Vì sao phải tách loại 2

Đã kiểm chứng: `WIP_Sammary` chứa `Cut_Qty`, `Deduct_Qty`, `Qty_After_Deduct` **không hề tồn tại trong `WIP_Detail`** — chúng đến từ dữ liệu cắt ở hệ thống khác.

- Nếu hợp đồng chỉ có entity thô → mất vĩnh viễn ba chỉ tiêu này.
- Nếu bê nguyên hình dạng sheet vào hợp đồng → sang SQL phải tái tạo đúng logic gộp của MES mà ta không nắm được.

### 5.2 Quy tắc gộp — đã kiểm chứng bằng số thật

Kiểm trên MO `5V2607331001` (7 trolley):

| Chỉ tiêu | Giá trị | Quy tắc đúng |
|---|---|---|
| `Total_Qty` | 2836 | Cộng tất cả |
| `Avg_Wip_CCT` | 1,1428571428571428 | Trung bình **bỏ ô trống** → mẫu số **7** |
| `Avg_Wip_VAP` | 7,666666666666667 | Trung bình **bỏ ô trống** → mẫu số **6** |
| `Total_Trolley` | 7 | Đếm **cả** dòng có `Qty` trống (trolley `202309`) |

⚠️ **Mẫu số khác nhau giữa các cột.** Dùng chung `len(rows)` cho mọi phép trung bình sẽ ra số sai **mà không báo lỗi**, rồi hiện thẳng lên TV xưởng.

→ Viết **hai helper riêng, tên rõ ràng**: hàm trung bình bỏ null **theo từng cột**; hàm đếm **không** bỏ null.

### 5.3 Bảng nguồn gốc chỉ tiêu

Mỗi chỉ tiêu phải khai báo nguồn gốc. Cập nhật bảng này mỗi khi thêm chỉ tiêu mới.

| Chỉ tiêu | Nguồn gốc | Ghi chú |
|---|---|---|
| `Total_Qty`, `Total_Trolley`, `Avg_Wip_*` | `COMPUTED` | Ta tự tính từ entity thô — sang SQL vẫn đúng |
| Phân bổ CCT/VAP, nhóm tuổi WIP, Top 10 tồn lâu | `COMPUTED` | |
| `Cut_Qty`, `Deduct_Qty`, `Qty_After_Deduct` | `SOURCE` | **Lấy nguyên từ nguồn.** Sang SQL phải tìm lại đường lấy, nếu không sẽ mất chỉ tiêu |

---

## 6. Quyết định kỹ thuật và lý do

| # | Quyết định | Lý do |
|:--:|---|---|
| 1 | **Next.js + FastAPI**, không dùng Dash/Taipy | Dash và Taipy tự là web server → chồng chéo với yêu cầu FastAPI, và khó đạt mức giao diện chuyên nghiệp. Next.js cho toàn quyền CSS, tách TV/PC thành hai layout khác hẳn, i18n chuẩn |
| 2 | **SSE thay vì WebSocket** | Chỉ cần đẩy một chiều. `EventSource` **tự động kết nối lại** khi rớt mạng — thiết yếu với TV chạy 24/7. WebSocket phải tự viết reconnect |
| 3 | **Next.js build tĩnh, nhúng vào FastAPI → 1 port** | Không có quyền Admin nên mỗi lần xin IT mở port là một lần chờ. Một port thay vì hai giảm một nửa rắc rối |
| 4 | **Watcher chống file ghi dở** | Excel xuất thủ công, file có thể đang copy hoặc đang mở. Xử lý: debounce 2s, retry khi `PermissionError`, bỏ qua `~$*.xlsx`, **so hash nội dung** để không đẩy thông báo giả. Kèm poll dự phòng 30s vì copy qua network drive đôi khi không sinh event |
| 5 | **Backend trả mã gốc, không trả chữ đã dịch** | Trả `"CCT"`, `"HeatTransfer"` chứ không trả "Khu vực in". Bản dịch nằm một chỗ ở frontend; dịch ở backend thì thêm ngôn ngữ phải sửa cả hai tầng |
| 6 | **KPI tính ở backend** | TV và PC dùng chung một endpoint → không bao giờ hiện hai con số khác nhau cho cùng chỉ tiêu |
| 7 | **Cache RAM cho trạng thái hiện tại + Parquet cho lịch sử** | ~67.000 dòng thừa sức nằm trong RAM. Nhưng file bị **ghi đè** nên quá khứ mất vĩnh viễn → phải lưu snapshot Parquet vào `data/history/`, **quyết ngay từ Bước 3 vì không hồi tố được** |
| 8 | **Đọc Excel bằng `python-calamine`** | pandas 2.2+ hỗ trợ `engine="calamine"`, nhanh hơn openpyxl nhiều lần — đáng kể với `Relaxed_3.1` 47.437 dòng. openpyxl làm dự phòng |
| 9 | **uvicorn đúng 1 worker — cố ý** | EventBus nằm trong RAM và watcher chỉ được chạy một lần. Nhiều worker → mỗi worker một EventBus và một watcher riêng, client nối vào worker A không nhận được sự kiện của worker B, file bị đọc lặp N lần. Cần scale thật thì mới chuyển pub/sub sang Redis |
| 10 | **Không dùng Docker** | Cần Admin để cài. Quan trọng hơn: `EXCEL files` phải bind-mount vào container Linux, mà **inotify không bắn ổn định qua bind mount** → phá hỏng đúng tính năng cốt lõi. Docker giải bài toán nhiều môi trường triển khai; ở đây chỉ có một PC cố định |
| 11 | **Không dùng Nginx** (giai đoạn này) | Vài chục client thì `StaticFiles` + `GZipMiddleware` thừa sức. Nginx mặc định bật `proxy_buffering` — thứ này **làm chết SSE**. Chỉ thêm khi >100 client, cần HTTPS, hoặc nhiều app chung port 80 |
| 12 | **Chạy ngầm bằng `pythonw` + Task Scheduler** | Không cửa sổ console, tự khởi động, tự restart khi lỗi, không cần Admin |

### 6.1 Bẫy `pythonw` — bắt buộc xử lý

Dưới `pythonw`, **`sys.stdout` và `sys.stderr` là `None`**. Bất kỳ thư viện nào gọi `print()` sẽ ném `AttributeError` và app **chết câm lặng, không để lại dấu vết**.

→ Việc **đầu tiên** trong `run_server.py`: gán lại `sys.stdout`/`sys.stderr` vào file log, bật `faulthandler`, bọc toàn bộ trong `try/except` ghi `crash.log`.

### 6.2 Log

Toàn bộ UTF-8 (bắt buộc — tên nhân viên có dấu), xoay vòng theo ngày:

| File | Nội dung | Giữ |
|---|---|---|
| `logs/app.log` | Nhật ký ứng dụng | 30 ngày |
| `logs/access.log` | Truy cập HTTP | 14 ngày |
| `logs/error.log` | Từ WARNING trở lên | 90 ngày |
| `logs/data-events.log` | Mỗi lần dữ liệu đổi: file, thời điểm, số dòng, hash | 90 ngày |
| `logs/crash.log` | faulthandler + lỗi không bắt được | không xoá |

`data-events.log` là bằng chứng *"lần cập nhật dữ liệu gần nhất là lúc nào"* — quan trọng vì Excel xuất thủ công.

---

## 7. Cấu hình và bí mật

- `.env` (**gitignore**) chứa giá trị thật; `.env.example` (**có commit**) chỉ liệt kê tên biến và mô tả.
- `config.py` dùng `pydantic-settings`, có kiểm tra kiểu.
- Biến có **tiền tố riêng**: `FLAP_PORT`, `FLAP_DATA_DIR`, `FLAP_BASE_PATH`, `FLAP_DATASOURCE`, `FLAP_SQL_*` — để nhiều dự án chạy chung PC không giẫm chân nhau.
- **Ưu tiên Windows Authentication cho SQL Server** (`Trusted_Connection=yes`): máy trong domain, SQL Server hỗ trợ sẵn → **không phải lưu mật khẩu ở đâu cả**.
- **Che mật khẩu khi ghi log.** Lỗi kết nối SQL thường in nguyên connection string → password rơi vào `app.log`, mà log lại hay được gửi đi khi nhờ hỗ trợ. Viết `mask_dsn()` và dùng ở mọi chỗ log liên quan kết nối.

---

## 8. Bảo mật dữ liệu — đọc trước khi chạy bất kỳ lệnh git nào

🔴 **Dữ liệu trong `EXCEL files/` tuyệt đối không được lên GitHub.**

- `Relaxed_3.1.xlsx` chứa **tên thật nhân viên**.
- 4 file còn lại là số liệu sản xuất nội bộ của Crystal International Group.

`.gitignore` đã chặn `EXCEL files/`, `*.xlsx`, `data/`, `logs/`, `.env`. **Trước mỗi lần push, kiểm tra lại:**

```powershell
& "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe" ls-files | Select-String -Pattern '\.xlsx$|\.env$'
```

Không ra kết quả nào mới được push. Nếu lỡ push rồi thì xoá commit khỏi lịch sử là **chưa đủ** — phải coi như dữ liệu đã lộ.

Repo: `https://github.com/nqhuy-212/FLAP.git` — **cần để ở chế độ Private.**

---

## 9. Đọc file Excel không cần thư viện

Khi cần khảo sát nhanh mà chưa có venv, `.xlsx` là file zip chứa XML:

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($path)
# xl/workbook.xml       -> tên sheet
# xl/worksheets/sheetN.xml -> ô dữ liệu
# xl/sharedStrings.xml  -> bảng chuỗi
```

⚠️ Ô có `t="s"` chứa **chỉ số** trỏ vào `sharedStrings.xml`, không phải chữ. Không tra bảng thì mọi cột chuỗi sẽ đọc ra thành số nguyên.

---

## 10. Mở rộng nhiều dashboard trên cùng PC

Nút thắt không phải CPU/RAM mà là **port và firewall** — không có Admin nên mỗi dự án mới là một lần xin IT nữa.

**Bốn việc rẻ tiền làm ngay:**
1. Mọi route đi sau tiền tố lấy từ config (`FLAP_BASE_PATH`), backend dùng `root_path` của FastAPI.
2. **Frontend đặt `basePath` + `assetPrefix` ngay từ đầu** — chỗ dễ vỡ nhất; để trống rồi sau mới thêm thì toàn bộ đường dẫn ảnh/CSS/JS trong bản build tĩnh sẽ hỏng.
3. Biến môi trường có tiền tố riêng, log riêng, tên task Task Scheduler riêng (`FLAP Dashboard`).
4. Tuân thủ bảng cấp phát port ở mục 3.

**Khi có dự án thứ hai:** dùng **reverse proxy một port duy nhất** — đây là lúc quyết định #11 (không dùng Nginx) đảo chiều, vì chỉ phải xin IT mở port đúng một lần. Khi đó **chọn Caddy chứ không phải Nginx**: chạy từ một `.exe` đơn lẻ (không cần Admin), config ngắn hơn nhiều, và **mặc định không buffer nên không làm chết SSE**.

**Về khung dùng chung** (`excel_utils`, `EventBus`, `watcher`, `logging_config`, layout TV/PC): bây giờ viết trong `backend/app/core/` **theo lối thư viện** — không hardcode chữ "FLAP", không import ngược ra ngoài. **Chỉ tách thành package riêng khi thật sự có dự án thứ hai**; tách sớm khi chưa có người dùng thứ hai gần như chắc chắn cho ra trừu tượng sai.
