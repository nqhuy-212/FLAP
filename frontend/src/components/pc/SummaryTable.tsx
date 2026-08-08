"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { SortableHead } from "./SortableHead";
import { useSortableData } from "@/lib/useSortableData";
import type { WipSummary } from "@/lib/types";
import type { TranslationKey } from "@/i18n/dictionaries";

interface SummaryTableProps {
  rows: WipSummary[];
  onSelectMo: (moNo: string) => void;
  t: (key: TranslationKey) => string;
}

/** Bảng tổng hợp — dữ liệu SOURCE nguyên bản từ WIP_Sammary, không tính lại (CLAUDE.md mục 5.3). */
export function SummaryTable({ rows, onSelectMo, t }: SummaryTableProps) {
  const { sorted, sortKey, sortDir, toggleSort } = useSortableData(rows, "total_qty" as keyof WipSummary);

  if (rows.length === 0) {
    return <p className="p-6 text-sm text-muted-foreground">{t("noResults")}</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <SortableHead label={t("columnStyle")} active={sortKey === "cust_style"} direction={sortDir} onClick={() => toggleSort("cust_style")} />
            <SortableHead label={t("columnGraphic")} active={sortKey === "graphic"} direction={sortDir} onClick={() => toggleSort("graphic")} />
            <SortableHead label={t("columnMo")} active={sortKey === "mo_no"} direction={sortDir} onClick={() => toggleSort("mo_no")} />
            <SortableHead label={t("columnTrolleyCount")} active={sortKey === "total_trolley"} direction={sortDir} onClick={() => toggleSort("total_trolley")} align="right" />
            <SortableHead label={t("columnCutQty")} active={sortKey === "cut_qty"} direction={sortDir} onClick={() => toggleSort("cut_qty")} align="right" />
            <SortableHead label={t("columnDeductQty")} active={sortKey === "deduct_qty"} direction={sortDir} onClick={() => toggleSort("deduct_qty")} align="right" />
            <SortableHead label={t("columnQtyAfterDeduct")} active={sortKey === "qty_after_deduct"} direction={sortDir} onClick={() => toggleSort("qty_after_deduct")} align="right" />
            <SortableHead label={t("columnQty")} active={sortKey === "total_qty"} direction={sortDir} onClick={() => toggleSort("total_qty")} align="right" />
            <SortableHead label={t("columnAvgWipCct")} active={sortKey === "avg_wip_cct"} direction={sortDir} onClick={() => toggleSort("avg_wip_cct")} align="right" />
            <SortableHead label={t("columnAvgWipVap")} active={sortKey === "avg_wip_vap"} direction={sortDir} onClick={() => toggleSort("avg_wip_vap")} align="right" />
            <SortableHead label={t("columnAvgWipPdc")} active={sortKey === "avg_wip_pdc"} direction={sortDir} onClick={() => toggleSort("avg_wip_pdc")} align="right" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map((row) => (
            <TableRow
              key={row.mo_no}
              className="cursor-pointer"
              onClick={() => onSelectMo(row.mo_no)}
            >
              <TableCell className="font-medium">{row.cust_style}</TableCell>
              <TableCell>{row.graphic}</TableCell>
              <TableCell className="text-muted-foreground">{row.mo_no}</TableCell>
              <TableCell className="text-right tabular-nums">{row.total_trolley}</TableCell>
              <TableCell className="text-right tabular-nums">{fmt(row.cut_qty)}</TableCell>
              <TableCell className="text-right tabular-nums">{fmt(row.deduct_qty)}</TableCell>
              <TableCell className="text-right tabular-nums">{fmt(row.qty_after_deduct)}</TableCell>
              <TableCell className="text-right font-medium tabular-nums">{fmt(row.total_qty)}</TableCell>
              <TableCell className="text-right tabular-nums">{fmt(row.avg_wip_cct)}</TableCell>
              <TableCell className="text-right tabular-nums">{fmt(row.avg_wip_vap)}</TableCell>
              <TableCell className="text-right tabular-nums">{fmt(row.avg_wip_pdc)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

function fmt(value: number | null): string {
  if (value === null) return "—";
  return value.toLocaleString("en-US", { maximumFractionDigits: 2 });
}
