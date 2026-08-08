"""Cấu hình ứng dụng — đọc từ .env, không hardcode. Xem CLAUDE.md mục 7."""
from __future__ import annotations

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    port: int = 8080
    data_dir: Path = PROJECT_ROOT / "EXCEL files"
    history_dir: Path = PROJECT_ROOT / "data" / "history"
    log_dir: Path = PROJECT_ROOT / "logs"
    base_path: str = ""
    datasource: str = "excel"
    # Chỉ cần khi chạy `next dev` (frontend port riêng, vd 3000) gọi sang backend
    # port riêng (vd 8080). Production nhúng chung 1 port (quyết định #3) nên
    # cùng origin — trình duyệt không áp CORS, biến này không có tác dụng gì.
    #
    # Khai kiểu `str` (không phải `list[str]`): pydantic-settings tự parse env
    # var kiểu list bằng JSON *trước khi* field_validator chạy, nên chuỗi phân
    # tách bằng dấu phẩy thường (không phải cú pháp JSON) sẽ lỗi ngay lúc khởi
    # tạo Settings() — bug thật gặp ở Bước 4. Tách thủ công qua cors_origins_list.
    cors_origins: str = "http://localhost:3000"
    # Bảo vệ /api/system/* — log chứa tên thật nhân viên (CLAUDE.md mục 4.1),
    # không được xem không cần token. Rỗng = tắt hẳn endpoint (503), không mở
    # mặc định "cho tiện test".
    system_token: str = ""

    model_config = SettingsConfigDict(
        env_prefix="FLAP_",
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("data_dir", "history_dir", "log_dir")
    @classmethod
    def _resolve_relative_to_project_root(cls, value: Path) -> Path:
        return value if value.is_absolute() else PROJECT_ROOT / value

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
