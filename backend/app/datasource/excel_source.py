"""ExcelDataSource — hiện thực DataSource đọc trực tiếp file Excel xuất thủ công.

Bước 1 chỉ đọc `WIP Report_1.1.xlsx`. Các entity còn lại (DeliveryPanel, Heat,
order, Relaxed) sẽ hiện thực ở Bước 8 khi khảo sát schema thật của từng file.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from app.core.excel_utils import (
    clean_null,
    excel_serial_to_datetime,
    read_banner_generated_at,
    read_banner_sheet,
    split_multi_value,
)
from app.models.meta import SnapshotInfo, SourceFileInfo
from app.models.other import (
    DeliveryTrolley,
    MaterialException,
    MaterialIssue,
    PrintOrder,
    RelaxRoll,
    SpreadPlan,
)
from app.models.wip import WipSummary, WipTrolley

WIP_REPORT_FILENAME = "WIP Report_1.1.xlsx"
WIP_DETAIL_SHEET = "WIP_Detail"
WIP_SUMMARY_SHEET = "WIP_Sammary"  # (sic) — tên sheet gốc viết sai chính tả trong MES
WIP_HEADER_ROW = 5


def _int_or_none(value) -> int | None:
    cleaned = clean_null(value)
    return None if cleaned is None else int(cleaned)


def _float_or_none(value) -> float | None:
    cleaned = clean_null(value)
    return None if cleaned is None else float(cleaned)


class ExcelDataSource:
    """Đọc dữ liệu từ thư mục chứa các file Excel MES/WMS xuất thủ công."""

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)

    def _wip_report_path(self) -> Path:
        return self.data_dir / WIP_REPORT_FILENAME

    def get_wip_trolleys(self) -> list[WipTrolley]:
        df = read_banner_sheet(self._wip_report_path(), WIP_DETAIL_SHEET, WIP_HEADER_ROW)
        return [
            WipTrolley(
                trolley_code=str(clean_null(rec["Trolley_Code"])),
                wb_code=clean_null(rec["wbCode"]),
                area=clean_null(rec["Area"]),
                so_no=str(clean_null(rec["SO_No"])),
                mo_no=str(clean_null(rec["MO_No"])),
                cust_style=str(clean_null(rec["Cust_Style"])),
                flower_code=str(clean_null(rec["Flower_Code"])),
                color_code=str(clean_null(rec["Color_Code"])),
                print_to_edge=clean_null(rec["Print to Edge"]),
                bed_no=split_multi_value(rec["Bed_No"]),
                size_no=split_multi_value(rec["Size_NO"]),
                qty=_int_or_none(rec["Qty"]),
                loading_ws=str(clean_null(rec["Loading_WS"])),
                loading_date=excel_serial_to_datetime(rec["Loading Date"]),
                in_vap_date=excel_serial_to_datetime(rec["In Vap Date"]),
                back_cct_date=excel_serial_to_datetime(rec["Back CCT Date"]),
                wip_cct=_int_or_none(rec["Wip_CCT"]),
                wip_vap=_int_or_none(rec["Wip_VAP"]),
                pdc_wip=_int_or_none(rec["PDC_WIP"]),
            )
            for rec in df.to_dict(orient="records")
        ]

    def get_wip_summary(self) -> list[WipSummary]:
        df = read_banner_sheet(self._wip_report_path(), WIP_SUMMARY_SHEET, WIP_HEADER_ROW)
        return [
            WipSummary(
                cust_style=str(clean_null(rec["Cust_Style"])),
                graphic=str(clean_null(rec["Graphic"])),
                mo_no=str(clean_null(rec["MO_No"])),
                total_trolley=_int_or_none(rec["Total_Trolley"]),
                cut_qty=_int_or_none(rec["Cut_Qty"]),
                deduct_qty=_int_or_none(rec["Deduct_Qty"]),
                qty_after_deduct=_int_or_none(rec["Qty_After_Deduct"]),
                total_qty=_int_or_none(rec["Total_Qty"]),
                avg_wip_cct=_float_or_none(rec["Avg_Wip_CCT"]),
                avg_wip_vap=_float_or_none(rec["Avg_Wip_VAP"]),
                avg_wip_pdc=_float_or_none(rec["Avg_Wip_PDC"]),
            )
            for rec in df.to_dict(orient="records")
        ]

    def get_snapshot_info(self) -> SnapshotInfo:
        path = self._wip_report_path()
        stat = path.stat()
        file_info = SourceFileInfo(
            name=path.name,
            generated_at=read_banner_generated_at(path, WIP_DETAIL_SHEET),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            row_count=len(self.get_wip_trolleys()),
        )
        return SnapshotInfo(source="excel", files=[file_info])

    # === Chưa hiện thực — khảo sát schema thật ở Bước 8 ===
    def get_delivery_trolleys(self) -> list[DeliveryTrolley]:
        raise NotImplementedError("DeliveryPanel_2.1 sẽ đọc ở Bước 8")

    def get_spread_plans(self) -> list[SpreadPlan]:
        raise NotImplementedError("order_8.1 (SPD) sẽ đọc ở Bước 8")

    def get_print_orders(self) -> list[PrintOrder]:
        raise NotImplementedError("order_8.1 (PRT) sẽ đọc ở Bước 8")

    def get_relax_rolls(self) -> list[RelaxRoll]:
        raise NotImplementedError("Relaxed_3.1 sẽ đọc ở Bước 8")

    def get_material_issues(self) -> list[MaterialIssue]:
        raise NotImplementedError("Heat_7.1 Sheet2 sẽ đọc ở Bước 8")

    def get_material_exceptions(self) -> list[MaterialException]:
        raise NotImplementedError("Heat_7.1 Sheet1 sẽ đọc ở Bước 8")
