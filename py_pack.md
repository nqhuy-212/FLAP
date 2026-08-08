# py_pack.md — Cài gói Python thủ công (máy nhà máy không vào được PyPI)

> Xem lý do trong [CLAUDE.md mục 3](CLAUDE.md#3-môi-trường-máy-đã-kiểm-tra-thực-tế-2026-08-03).
> `pypi.org` / `files.pythonhosted.org` bị chặn ở tầng TCP trên mạng nhà máy (đã kiểm chứng, không phải
> lỗi SSL, `--trusted-host` không giúp được). Giải pháp: tải file `.whl` trên một máy có mạng, copy thủ
> công sang máy này, cài offline bằng `pip install --no-index`.

## Trạng thái hiện tại (2026-08-07, sau Bước 3)

✅ **36 gói đã cài** vào `backend\.venv` — đủ để `pytest` chạy xanh toàn bộ (70/70 test PASS qua Bước 1-3,
kể cả FastAPI + SSE + watcher + Parquet). Wheelhouse nằm ở **gốc dự án**: `FLAP/wheelhouse/` (không phải
`backend/wheelhouse/`).

⚠️ **Thiếu `httpx`** — không nằm trong `requirements.txt` gốc (Bước 1) nên chưa từng tải. Cần cho
`fastapi.testclient.TestClient` (test tự động cho endpoint HTTP/SSE thay vì phải dựng server thật để kiểm
tra thủ công như Bước 2-3 đang làm). Chưa chặn gì hiện tại — chỉ tải khi thật sự cần viết test kiểu này:
```powershell
pip download -d wheelhouse httpx --python-version 3.13 --platform win_amd64 --only-binary=:all:
```

❌ **Còn thiếu `tzdata`** — pandas khai `tzdata; sys_platform == "win32"` là dependency bắt buộc trên
Windows, khiến `pip install -r requirements.txt` bình thường **từ chối cài bất kỳ gói nào** (toàn bộ set
resolve thất bại vì thiếu 1 gói). Cách đã xử lý tạm thời: cài trực tiếp từng file `.whl` có sẵn bằng
`pip install --no-index --no-deps <danh sách wheel>`, bỏ qua bước pip tự đòi `tzdata`.

**Vì sao vẫn chạy được dù thiếu `tzdata`:** gói này chỉ cần khi làm việc với datetime **có timezone**
(`tz-aware`). Toàn bộ ngày giờ trong dự án (`excel_serial_to_datetime`) là **naive datetime**, không gắn
timezone, nên `pandas.import` và mọi test hiện tại chạy bình thường. **Vẫn nên tải bổ sung `tzdata`** để
lần cài sau (Bước 2 trở đi, khi thêm gói mới) không bị chặn bởi cùng lỗi thiếu dependency này — xem hướng
dẫn tải bên dưới.

---

## Cách tải wheel trên máy có mạng (máy cá nhân)

Yêu cầu máy đó chạy **Windows 64-bit** (để tải đúng kiến trúc `win_amd64`; không cần cùng Python
version vì các flag dưới đây ép pip tải wheel cho đúng Python 3.13, bất kể máy tải đang chạy Python
bản nào — chỉ cần có `pip` từ Python 3.8+).

### Gói còn thiếu cần tải ngay — chỉ 1 gói

```powershell
pip download -d wheelhouse tzdata --python-version 3.13 --platform win_amd64 --only-binary=:all:
```

Gói thuần Python (`py2.py3-none-any`), không kén nền tảng — chỉ cần tải đúng gói này, không cần tải lại
36 gói đã có.

### Quy trình đầy đủ (khi thêm gói mới vào `requirements.txt` ở các bước sau)

1. Copy [backend/requirements.txt](backend/requirements.txt) sang máy có mạng (hoặc chỉ chép nội dung).
2. Mở PowerShell/CMD tại thư mục chứa `requirements.txt`, chạy:

   ```powershell
   pip download -d wheelhouse -r requirements.txt --python-version 3.13 --platform win_amd64 --only-binary=:all:
   ```

   Giải thích từng flag:
   - `-d wheelhouse` — tải mọi file `.whl` (kể cả dependency kéo theo, tự động resolve) vào thư mục
     `wheelhouse/` cạnh đó. **Không cần tự liệt kê dependency** — pip tự tính. Gói đã có sẵn trong
     `wheelhouse/` sẽ tự động được bỏ qua nếu chạy lại đúng thư mục cũ.
   - `--python-version 3.13` — khớp đúng Python 3.13.2 trên máy nhà máy.
   - `--platform win_amd64` — khớp đúng Windows 64-bit trên máy nhà máy (phòng khi máy tải là macOS/Linux
     hoặc 32-bit).
   - `--only-binary=:all:` — chỉ lấy file `.whl` dựng sẵn, **không** lấy source `.tar.gz` (source thì máy
     nhà máy sẽ phải tự biên dịch — không có công cụ build C/C++ nên sẽ lỗi).

3. Kiểm tra thư mục `wheelhouse/` có toàn file `.whl` — nếu thấy `.tar.gz`/`.zip` lẫn vào, một gói nào đó
   không có sẵn wheel cho `win_amd64`, cần báo lại.

4. Copy nguyên thư mục `wheelhouse/` (USB / network share nội bộ) đè vào **gốc dự án**:

   ```
   D:\2025 nqhuy\Projects\AI appication\Claude\Claude code\FLAP\wheelhouse\
   ```

   (Đã có `wheelhouse/` và `*.7z` trong `.gitignore` — không lo commit nhầm dù nén thành `.7z` để copy.)

5. Báo lại "đã tải/copy xong" — sẽ cài bằng:

   ```powershell
   backend\.venv\Scripts\python.exe -m pip install --no-index --no-deps (Get-ChildItem wheelhouse\*.whl | ForEach-Object FullName)
   ```

   (Dùng `--no-deps` cài trực tiếp từng wheel thay vì `-r requirements.txt`, vì cách thường sẽ bị chặn
   toàn bộ nếu thiếu dù chỉ 1 dependency — xem lý do ở mục "Trạng thái hiện tại" phía trên. Cách này an
   toàn khi đã biết trước toàn bộ wheel trong thư mục tương thích với nhau.)
