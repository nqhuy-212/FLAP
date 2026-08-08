"""Model tạm cho các entity chưa khảo sát schema thật.

Chỉ WIP Report được đọc ở Bước 1. Các model dưới đây giữ chỗ cho chữ ký
Protocol trong datasource/base.py; sẽ định nghĩa đủ trường khi đọc từng
file thật ở Bước 8 (DeliveryPanel, Heat, order, Relaxed).
"""
from __future__ import annotations

from pydantic import BaseModel


class DeliveryTrolley(BaseModel):
    pass


class SpreadPlan(BaseModel):
    pass


class PrintOrder(BaseModel):
    pass


class RelaxRoll(BaseModel):
    pass


class MaterialIssue(BaseModel):
    pass


class MaterialException(BaseModel):
    pass
