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
| **PyPI (`pip install`)** | **KHÔNG truy cập được** (kiểm tra 2026-08-04) — `pypi.org`/`files.pythonhosted.org` timeout ở tầng TCP (không phải lỗi SSL, `--trusted-host` không giúp được). `github.com`, `google.com`, `registry.npmjs.org` vẫn vào bình thường → chỉ chặn riêng PyPI. Không có mirror nội bộ. **Cách xử lý: tải `.whl` thủ công trên máy khác rồi cài offline — xem [py_pack.md](py_pack.md)** |
| `npm install` | **Bình thường** (kiểm tra 2026-08-07) — `registry.npmjs.org` không bị chặn, không cần wheelhouse-style workaround như Python |
| Fetch tới `ui.shadcn.com` (shadcn CLI) | **Lỗi khác hẳn PyPI:** `self-signed certificate in certificate chain` — mạng có proxy soi SSL (MITM) chèn chứng chỉ tự ký mà Node không tin, không phải chặn TCP. Xử lý tạm: `NODE_TLS_REJECT_UNAUTHORIZED=0` chỉ cho đúng lệnh `shadcn init`/`add` (rủi ro thấp vì chỉ tải component UI công khai) |

**Hệ quả quan trọng:** Python, Node và git đều không nằm trong PATH → luôn gọi bằng đường dẫn đầy đủ hoặc qua script trong `scripts/`. Đường dẫn dự án có dấu cách → luôn đặt trong dấu nháy kép. Cài gói Python **không thể** dùng `pip install` trực tiếp — luôn qua quy trình wheelhouse offline trong `py_pack.md`.

### 3.1 Trạng thái wheelhouse (kiểm tra 2026-08-07)

Thư mục wheel nằm ở **gốc dự án**: `FLAP/wheelhouse/` — **không phải** `backend/wheelhouse/` như [py_pack.md](py_pack.md) mô tả. Khi chạy lệnh cài phải trỏ `--find-links` vào đúng đường dẫn gốc này.

- **36 file `.whl`, 54,8 MB**, toàn bộ đúng `cp313` / `win_amd64`, không lẫn file `.tar.gz` nào.
- Đã kiểm chứng bằng `pip install --dry-run`: **30/31 gói giải phụ thuộc thành công**.
- ❌ **Thiếu đúng một gói: `tzdata`** — pandas khai nó là dependency bắt buộc trên Windows
  (`tzdata; sys_platform == "win32"`), khiến `pip install -r requirements.txt` **từ chối cài bất kỳ gói
  nào** dù chỉ thiếu 1 gói (toàn bộ resolve thất bại chung). Gói thuần Python, không kén nền tảng, tải bằng:
  ```powershell
  pip download -d wheelhouse tzdata --python-version 3.13 --platform win_amd64 --only-binary=:all:
  ```
- ✅ **Đã cài thành công** (2026-08-07) bằng cách né qua resolver: cài trực tiếp từng file `.whl` với
  `--no-deps` thay vì `-r requirements.txt`:
  ```powershell
  $wheels = Get-ChildItem wheelhouse\*.whl | ForEach-Object FullName
  backend\.venv\Scripts\python.exe -m pip install --no-index --no-deps $wheels
  ```
  Pandas vẫn `import` và chạy bình thường thiếu `tzdata` vì dự án chỉ dùng datetime **naive** (không
  timezone). Vẫn nên tải bổ sung `tzdata` để lần cài sau (khi `requirements.txt` có gói mới) dùng lại
  được cách cài chuẩn `-r requirements.txt` mà không bị chặn — xem [py_pack.md](py_pack.md).

Có vài wheel dư không dùng đến (`six`, `python_dateutil` chỉ pandas cần; `exceptiongroup`, `tomli` chỉ dành cho Python < 3.11) — vô hại, cứ để đó.

### 3.2 Phiên bản thư viện mới hơn dự kiến — đã kiểm chứng qua pytest, không cần chỉnh code

Bản `pip download` lấy về phiên bản mới nhất, và một số là **bản major mới**:

| Gói | Bản trong wheelhouse | Lưu ý |
|---|---|---|
| **pandas** | **3.0.5** | Major mới (Copy-on-Write mặc định, đổi dtype chuỗi mặc định). **Đã chạy `pytest` thật (34/34 PASS) — không phải sửa dòng code nào**, `read_excel`/`to_dict("records")` trong `excel_utils.py`/`excel_source.py` không đụng chỗ hành vi đổi |
| numpy | 2.5.1 | Đi kèm pandas 3 |
| pyarrow | 25.0.0 | Dùng cho snapshot Parquet — **đã kiểm chứng Bước 3**, `to_parquet`/`read_parquet` hoạt động bình thường kể cả cột kiểu `list[str]` (`bed_no`/`size_no`) |
| starlette | 1.3.1 | Major mới — **đã kiểm chứng Bước 2/3** (`StreamingResponse` cho SSE, `TestClient` KHÔNG dùng được vì thiếu `httpx`, xem [py_pack.md](py_pack.md)) |
| fastapi | 0.141.1 | **Đã kiểm chứng Bước 2/3** qua server thật, không phải sửa gì |
| pytest | 9.1.1 | Major mới — đã dùng để chạy bộ test Bước 1, hoạt động bình thường |

Lưu ý Python313 **hệ thống** đang có pandas 2.2.3 / numpy 2.2.3 — khác hẳn venv dự án. Luôn chạy bằng `backend\.venv\Scripts\python.exe`, đừng lẫn với Python hệ thống.

### 3.3 Frontend: Next.js mới hơn dữ liệu huấn luyện AI — luôn đọc doc cục bộ trước khi viết code

`npm create next-app@latest` (Bước 4, 2026-08-07) cài **Next.js 16.3.0** — mới hơn hẳn kiến thức huấn luyện
của Claude (biết tới ~Next.js 15). Bản thân `next dev`/`next build` **tự sinh** `frontend/AGENTS.md` cảnh
báo đúng việc này và yêu cầu đọc `node_modules/next/dist/docs/` trước khi code — **phải làm theo mỗi khi
động vào code Next.js**, đừng chỉ dựa vào hiểu biết cũ. File này do Next.js tự tạo lại (không phải người
viết), commit cùng code là đúng — xem CLAUDE.md gốc trong `frontend/CLAUDE.md` (`@AGENTS.md`, do
`create-next-app` sinh, không phải file này).

Đã kiểm chứng thực tế những API dự án dùng **không đổi** so với hiểu biết cũ: `output: 'export'`,
`basePath`/`assetPrefix`, `images.unoptimized`. Điểm khác duy nhất gặp phải: layout/page nhận type
`LayoutProps<"/...">`/`PageProps<"/...">` tự sinh thay vì tự khai kiểu props thủ công.

⚠️ **`next build` cũng nạp `.env.local`, không chỉ `next dev`** — khác kỳ vọng thường gặp ở các bản cũ hơn.
Biến chỉ dùng khi dev (`NEXT_PUBLIC_API_BASE_URL` trỏ sang backend port riêng) phải để trong
`frontend/.env.development.local` (chỉ nạp khi `NODE_ENV=development`), nếu không bundle production sẽ
đóng băng nhầm URL dev thay vì dùng đường dẫn tương đối cùng origin (quyết định #3).

### 3.4 ESLint react-hooks nghiêm hơn hẳn — chặn hẳn 1 kiểu code quen thuộc

Bản `eslint-config-next` đi kèm Next 16 bật cả một họ rule `react-hooks/*` nghiêm hơn nhiều so với hiểu
biết cũ — không chỉ warning mà **chặn build**. Đã gặp 2 rule khác nhau, cả hai đều đúng và nên sửa theo
khuyến nghị của rule chứ không tắt lint:
- `react-hooks/refs` (Bước 4, `useLiveData.ts`): gán `ref.current = ...` ngay trong thân render (không
  phải trong effect/handler) là lỗi.
- `react-hooks/set-state-in-effect` (Bước 6): gọi `setState` đồng bộ ngay trong thân `useEffect` (không
  qua sự kiện bất đồng bộ) là lỗi. Bắt được 2 chỗ: "đọc `localStorage`/tính giá trị ban đầu trong effect
  rồi `setState`" và "effect tự sửa state khi state cha đổi". Cách sửa đúng theo rule này:
- **Giá trị khởi tạo đọc từ bên ngoài** (localStorage, `window`) → dùng lazy initializer
  `useState(() => tínhGiáTrị())` thay vì `useState(default)` + effect gọi `setState` sau khi mount.
- **State "phái sinh" cần tự sửa khi dependency đổi** (vd lựa chọn đang xem bị bộ lọc loại khỏi danh
  sách) → **đừng lưu nó như 1 state riêng cần đồng bộ**, tính thẳng giá trị hiệu lực mỗi lần render
  (`const effective = raw && stillValid(raw) ? raw : null`) và dùng biến đó cho toàn bộ UI/logic. Đây
  chính là khuyến nghị "you might not need an effect" của React, rule chỉ đang ép thực hiện đúng.

### 3.5 base-ui Select — `Select.Value` mặc định hiện **giá trị thô**, không tự tra nhãn

shadcn ở dự án này dùng `@base-ui/react` (không phải Radix). `<SelectValue>` không tự map `value` sang
nhãn hiển thị của `<SelectItem>` tương ứng trừ khi truyền `items` cho `<Select.Root>` **hoặc** truyền
children dạng hàm cho `<SelectValue>`: `<SelectValue>{(v) => nhãn(v)}</SelectValue>`. Thiếu bước này,
dropdown "Tất cả" sẽ hiện đúng chuỗi giá trị nội bộ (vd `"__all__"`) thay vì nhãn đã dịch — bug thật gặp ở
Bước 6, phát hiện qua ảnh chụp màn hình thật (`tsc`/ESLint không bắt được vì không phải lỗi kiểu/logic).

### 3.6 Font thương mại (Century Gothic) không nhúng được — chỉ khai `font-family`, cậy máy có sẵn

Trang `/tv/wip` dùng font **Century Gothic** theo yêu cầu người dùng (2026-08-08). Đây là font bản quyền
Monotype, **không có trên Google Fonts** → không dùng được `next/font/google`, không có file `.woff2` hợp
pháp nào để tự host. Xử lý: khai thẳng `font-family: '"Century Gothic", CenturyGothic, Verdana, sans-serif'`
(`components/tv/colors.ts` → `TV_FONT_FAMILY`) — trình duyệt dùng bản cài sẵn trên máy (thường có qua MS
Office, phổ biến ở máy văn phòng) và tự rơi về Verdana nếu máy không có font này. **Hệ quả đã gặp thật:**
Verdana rộng hơn hẳn font mặc định cũ (Geist), làm bảng 5 cột tràn xuống 2 dòng/ô dù layout không đổi —
bài học: mỗi lần đổi font cho trang TV phải build + chụp ảnh kiểm tra lại độ rộng cột/bảng, không chỉ tin
`tsc`/ESLint (không bắt được lỗi loại này).

### 3.7 Kiểm tra hình ảnh thật cho trang TV — cài tạm `playwright-core`, gỡ ngay sau khi xong

Không có Chromium tải sẵn và mạng chặn tải nhị phân lớn, nhưng máy có **Edge cài sẵn**
(`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`). Từ Bước 4 đã dùng `playwright-core` +
`channel: msedge` để kiểm tra bằng ảnh chụp thật, nhưng gói này **không phải dependency của app** — cài
bằng `npm install playwright-core --no-save` (không đụng `package.json`), viết script `.mjs` tạm **bên
trong** `frontend/` (không phải ở thư mục scratchpad — Node chỉ resolve `node_modules` từ thư mục chứa
script trở lên), chạy xong thì `npm uninstall playwright-core` + xoá script tạm. Bất kỳ thay đổi giao diện
TV nào (màu, font, layout) đều nên kiểm bằng vòng lặp này trước khi báo hoàn thành — nhiều bug thật ở trang
TV (bảng tràn dòng, tiêu đề wrap 2 dòng) chỉ lộ ra qua ảnh chụp, không phải qua `tsc`/ESLint/`next build`.

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
| `WIP Report_1.1.xlsx` | `WIP_Detail`, `WIP_Sammary` *(sic)* | 352 / 41 † | Tồn WIP theo trolley, mốc thời gian `Loading Date` → `In Vap Date` → `Back CCT Date`, bộ đếm tuổi `Wip_CCT`/`Wip_VAP`/`PDC_WIP` (ngày) |
| `DeliveryPanel_2.1.xlsx` | `TotalTrolley` | 26 | Trolley giao từ CCT sang VAP, `WorkCenter` (Printing / Heat transfer), cờ `IsRework` |
| `Heat_7.1.xlsx` | `Sheet1`, `Sheet2` | 101 / 5.166 | Sheet1: log lỗi vật tư kèm cột `ResultJson` chứa mảng JSON. Sheet2: log cấp phát nhãn nhiệt |
| `order_8.1.xlsx` | `SPD`, `PRT` | 17 / 14.465 | SPD: kế hoạch trải vải theo máy/bàn/cuộn. PRT: xác nhận lệnh in theo style/màu/vị trí |
| `Relaxed_3.1.xlsx` | `Sheet1` | 47.437 | Log xả vải theo cuộn, pallet, bin, tên nhân viên |

† Cột "Số dòng" của `WIP Report_1.1.xlsx` đếm bằng `max_row` — **tổng dòng vật lý của sheet, gồm cả 5
dòng banner/header**, không phải số dòng dữ liệu thật. Đã kiểm chứng bằng `pytest` (Bước 1, 2026-08-07):
số dòng dữ liệu thật là **347** (`WIP_Detail`) và **36** (`WIP_Sammary`) — tức `max_row` trừ 5.

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
- **`pandas.NaT` là subclass của `datetime`** — ô ngày trống mà pandas tự parse cột thành `datetime64`
  (thay vì trả serial thô) sẽ cho ra `NaT`, và `isinstance(NaT, datetime)` là `True`. Code nào kiểm tra
  "đã là datetime thật thì giữ nguyên" bằng `isinstance(value, datetime)` **phải kiểm `pd.isna(value)`
  trước**, nếu không `NaT` sẽ lọt qua như một giá trị hợp lệ (bug thật gặp ở Bước 2, làm `/api/wip/detail`
  lỗi 500 khi serialize JSON — xem `excel_serial_to_datetime` trong `core/excel_utils.py`).
- **`Area` và `wbCode` trong `WIP_Detail` có ô trống thật** (5 và 4 dòng trong 347 dòng) — đây là `None`
  hợp lệ, không phải lỗi đọc file. Field nào ép kiểu bằng `str(clean_null(x))` cho các cột này sẽ biến
  `None` thành **chuỗi `"None"` sai** một cách âm thầm (không lỗi, không cảnh báo — chỉ hiện sai số liệu).
  Cột nào có thể trống thật trong dữ liệu phải khai `str | None` trong model, không được ép `str(...)`.

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
| `area_breakdown` (phân bổ theo khu vực) | `COMPUTED` | Bước 2, `services/kpi.py`. Gộp cả trolley không có `Area` (`None` — có thật trong dữ liệu) |
| `age_buckets` (nhóm tuổi WIP 0-3/4-7/8-14/>14 ngày) | `COMPUTED` | Bước 2. Tuổi = cột `Wip_CCT`/`Wip_VAP`/`PDC_WIP` khớp đúng `Area` hiện tại — **không phải cộng cả 3 cột**, vì mỗi trolley có sẵn cả 3 giá trị nhưng chỉ cột khớp Area phản ánh đúng thời gian chờ hiện tại |
| `top_aging` (Top 10 style-MO tồn lâu nhất) | `COMPUTED` | Bước 2. Xếp theo tuổi **lớn nhất** (`max`) trong các trolley cùng `MO_No` |
| `loading_trend` (xu hướng theo `Loading Date`) | `COMPUTED` | Bước 2. Gộp theo ngày (bỏ giờ), bỏ trolley không có `Loading Date` |
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
| 7 | **Cache RAM cho trạng thái hiện tại + Parquet cho lịch sử** | ~67.000 dòng thừa sức nằm trong RAM. Nhưng file bị **ghi đè** nên quá khứ mất vĩnh viễn → phải lưu snapshot Parquet vào `data/history/`, **quyết ngay từ Bước 3 vì không hồi tố được**. Phần Parquet đã làm (Bước 3); phần cache RAM **chưa cần code riêng** — `ExcelDataSource` đọc thẳng từ đĩa mỗi request và vẫn đủ nhanh với ~350 dòng thật (đã kiểm chứng Bước 2-6 qua nhiều lần gọi API/browser). Chỉ làm `services/cache.py` nếu sau này thấy chậm thật (vd khi có `Relaxed_3.1` 47.437 dòng ở Bước 8) |
| 8 | **Đọc Excel bằng `python-calamine`** | pandas 2.2+ hỗ trợ `engine="calamine"`, nhanh hơn openpyxl nhiều lần — đáng kể với `Relaxed_3.1` 47.437 dòng. openpyxl làm dự phòng (wheelhouse có cả hai) |
| 9 | **uvicorn đúng 1 worker — cố ý** | EventBus nằm trong RAM và watcher chỉ được chạy một lần. Nhiều worker → mỗi worker một EventBus và một watcher riêng, client nối vào worker A không nhận được sự kiện của worker B, file bị đọc lặp N lần. Cần scale thật thì mới chuyển pub/sub sang Redis. ⚠️ **Bẫy đã gặp (Bước 5):** `uvicorn.run(..., reload=True)` không truyền `reload_dirs` mặc định theo dõi **cả** `Path.cwd()` (`backend/`), tức cả `.venv/` — cache `.pyc` sinh ra khi chạy thật (vd lần đầu `pyarrow` chạy) bị hiểu nhầm là đổi code, worker bị restart ngầm, **EventBus cũ mất theo, mọi client SSE đang nối rớt kết nối lặng lẽ** (không lỗi, không log — watcher vẫn phát hiện file đổi và ghi log bình thường, chỉ là không còn ai lắng nghe). Đã sửa: `reload_dirs=["app"]` trong `main.py`, chỉ theo dõi mã nguồn |
| 10 | **Không dùng Docker** | Cần Admin để cài. Quan trọng hơn: `EXCEL files` phải bind-mount vào container Linux, mà **inotify không bắn ổn định qua bind mount** → phá hỏng đúng tính năng cốt lõi. Docker giải bài toán nhiều môi trường triển khai; ở đây chỉ có một PC cố định |
| 11 | **Không dùng Nginx** (giai đoạn này) | Vài chục client thì `StaticFiles` + `GZipMiddleware` thừa sức. Nginx mặc định bật `proxy_buffering` — thứ này **làm chết SSE**. Chỉ thêm khi >100 client, cần HTTPS, hoặc nhiều app chung port 80 |
| 12 | **Chạy ngầm bằng `pythonw` + Task Scheduler** | Không cửa sổ console, tự khởi động, tự restart khi lỗi, không cần Admin |

### 6.1 Bẫy `pythonw` — bắt buộc xử lý

Dưới `pythonw`, **`sys.stdout` và `sys.stderr` là `None`**. Bất kỳ thư viện nào gọi `print()` sẽ ném `AttributeError` và app **chết câm lặng, không để lại dấu vết**.

→ Việc **đầu tiên** trong `run_server.py`: gán lại `sys.stdout`/`sys.stderr` vào file log, bật `faulthandler`, bọc toàn bộ trong `try/except` ghi `crash.log`.

✅ **Đã hiện thực ở Bước 7** (`backend/run_server.py`): `crash.log` mở trực tiếp bằng `open()` (không qua
`logging_config.py`/`TimedRotatingFileHandler`) ngay ở đầu file, **trước cả** import `app.config` —
`Settings()` đọc `.env` cũng có thể ném lỗi, phải có chỗ ghi lại trước khi bất kỳ import nào khác chạy.
Ghi PID vào `logs/flap.pid` để `scripts/stop.cmd`/`restart.cmd` dừng đúng tiến trình (không có cửa sổ để
Ctrl+C dưới `pythonw`). Chạy production bằng `uvicorn.run(..., reload=False, workers=1, log_config=None)`.

⚠️ **Bẫy khác gặp khi kiểm chứng Bước 7 — không phải bẫy `pythonw`, nhưng cùng nhóm "log biến mất im
lặng":** `uvicorn.run()` mặc định tự `dictConfig` lại logging của chính nó (logger `uvicorn.access`/
`uvicorn.error`) **sau khi** đã import xong app (tức sau `configure_logging()` chạy trong `create_app()`)
— ghi đè mất handler ghi vào `access.log` bằng handler console mặc định của uvicorn. Request vẫn chạy
đúng, HTTP vẫn trả đúng mã, chỉ là `access.log` **rỗng vĩnh viễn, không lỗi, không cảnh báo** — chỉ phát
hiện được bằng cách gọi request thật rồi đọc lại file. Sửa: truyền `log_config=None` cho `uvicorn.run()`
để giữ nguyên cấu hình logging đã đặt trong `configure_logging()`.

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

✅ **Đã hiện thực ở Bước 3** (`logging_config.py` + `services/watcher.py` + `main.py`): 2 dòng log mỗi lần
`WIP Report_1.1.xlsx` đổi thật — `file=... hash=...` (từ watcher, bắn ngay khi phát hiện thay đổi, áp dụng
cho cả 5 file) và `file=... rows=... snapshot=saved` (từ callback lưu Parquet, chỉ WIP Report vì 4 file
kia chưa hiện thực đọc).

✅ **`app.log`/`access.log`/`error.log` đã hiện thực ở Bước 7** (`configure_logging()` trong
`logging_config.py`, gọi 1 lần trong `create_app()` nên có hiệu lực cả dev lẫn production): `app.log` nhận
log của logger `flap.app` (khởi động/tắt watcher, khởi động `run_server.py`); `access.log` nhận log của
`uvicorn.access` (mỗi request HTTP — cần `log_config=None` khi gọi `uvicorn.run()`, xem mục 6.1); `error.log`
gắn vào root logger, lọc `WARNING` trở lên, bắt được cảnh báo/lỗi từ **mọi** logger có `propagate=True`
(gồm cả `uvicorn.error`). Kiểm chứng thật: gọi 8 request qua server production, `access.log` ghi đúng 8
dòng kèm mã trạng thái, `app.log` ghi đúng thời điểm khởi động + watcher start, tiếng Việt có dấu giữ
nguyên UTF-8 (kiểm bằng đọc file trực tiếp — `Get-Content` của PowerShell 5.1 hiển thị mojibake do
codepage console, không phải lỗi file thật, xem PLAN.md Bước 7).

---

## 7. Cấu hình và bí mật

- `.env` (**gitignore**) chứa giá trị thật; `.env.example` (**có commit**) chỉ liệt kê tên biến và mô tả.
- `config.py` dùng `pydantic-settings`, có kiểm tra kiểu.
- Biến có **tiền tố riêng**: `FLAP_PORT`, `FLAP_DATA_DIR`, `FLAP_HISTORY_DIR`, `FLAP_LOG_DIR`, `FLAP_BASE_PATH`, `FLAP_DATASOURCE`, `FLAP_CORS_ORIGINS`, `FLAP_SYSTEM_TOKEN`, `FLAP_SQL_*` — để nhiều dự án chạy chung PC không giẫm chân nhau.
- `FLAP_SYSTEM_TOKEN` bảo vệ `GET /api/system/status` (trang `/pc/system`, Bước 7) — log trả về trong
  endpoint này chứa **tên thật nhân viên** nên không được xem không cần xác thực. Để trống = tắt hẳn
  endpoint (503), không mặc định mở "cho tiện test". **Bắt buộc đặt giá trị riêng** trước khi chạy trên
  LAN nhà máy — không dùng giá trị mẫu trong `.env` hiện tại của máy dev.
- `FLAP_CORS_ORIGINS` (mặc định `http://localhost:3000`) **chỉ cần khi `next dev` chạy port riêng** gọi sang backend port riêng lúc phát triển. Production nhúng chung 1 port (quyết định #3) nên cùng origin, biến này không có tác dụng gì — không cần đổi khi triển khai thật.
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

✅ **Lỗ hổng đã vá (2026-08-07):** từng có lúc `.gitignore` chỉ chặn thư mục `wheelhouse/` mà không chặn file nén `wheelhouse.7z` (53,8 MB) ở gốc dự án — đã thêm `*.7z` vào `.gitignore`, xác nhận bằng `git check-ignore -v wheelhouse.7z`.

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
