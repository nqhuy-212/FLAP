"""Dependency dùng chung cho các route — lấy DataSource từ app.state."""
from __future__ import annotations

from fastapi import Request

from app.datasource.base import DataSource


def get_data_source(request: Request) -> DataSource:
    return request.app.state.data_source
