"""Test config.py — đặc biệt cors_origins, nơi từng lỗi thật ở Bước 4.

pydantic-settings tự parse env var kiểu `list[str]` bằng JSON trước khi
field_validator chạy, nên set FLAP_CORS_ORIGINS bằng chuỗi phân tách dấu phẩy
thường sẽ làm `Settings()` lỗi ngay lúc khởi tạo nếu field khai kiểu list.
Test này dùng lại instance `settings` thật (đã khởi tạo thành công lúc import
app.config, tức Settings() không lỗi với giá trị trong .env hiện tại) và kiểm
tra riêng hàm tách chuỗi.
"""
from app.config import Settings


def test_cors_origins_list_splits_comma_separated():
    s = Settings(cors_origins="http://localhost:3000,http://localhost:3001")
    assert s.cors_origins_list == ["http://localhost:3000", "http://localhost:3001"]


def test_cors_origins_list_strips_whitespace():
    s = Settings(cors_origins=" http://localhost:3000 , http://localhost:3001 ")
    assert s.cors_origins_list == ["http://localhost:3000", "http://localhost:3001"]


def test_cors_origins_list_empty_string_gives_empty_list():
    s = Settings(cors_origins="")
    assert s.cors_origins_list == []


def test_default_settings_construct_without_error():
    # Bug thật ở Bước 4: nếu cors_origins khai kiểu list[str], Settings() lỗi
    # ngay khi FLAP_CORS_ORIGINS trong .env là chuỗi phân tách dấu phẩy thường
    # (không phải JSON) — test này tự nó là bằng chứng không còn lỗi đó.
    s = Settings()
    assert isinstance(s.cors_origins_list, list)
