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
import type { WipTrolley } from "@/lib/types";
import type { Lang, TranslationKey } from "@/i18n/dictionaries";

interface DetailTableProps {
  rows: WipTrolley[];
  lang: Lang;
  t: (key: TranslationKey) => string;
}

/** Chi tiết trolley — entity thô, COMPUTED phía backend, có thể sắp xếp theo mọi cột. */
export function DetailTable({ rows, lang, t }: DetailTableProps) {
  const { sorted, sortKey, sortDir, toggleSort } = useSortableData(rows, "trolley_code" as keyof WipTrolley);

  if (rows.length === 0) {
    return <p className="p-6 text-sm text-muted-foreground">{t("noResults")}</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            <SortableHead label={t("columnTrolleyCode")} active={sortKey === "trolley_code"} direction={sortDir} onClick={() => toggleSort("trolley_code")} />
            <SortableHead label={t("columnWbCode")} active={sortKey === "wb_code"} direction={sortDir} onClick={() => toggleSort("wb_code")} />
            <SortableHead label={t("columnArea")} active={sortKey === "area"} direction={sortDir} onClick={() => toggleSort("area")} />
            <SortableHead label={t("columnColor")} active={sortKey === "color_code"} direction={sortDir} onClick={() => toggleSort("color_code")} />
            <SortableHead label={t("columnQty")} active={sortKey === "qty"} direction={sortDir} onClick={() => toggleSort("qty")} align="right" />
            <SortableHead label={t("columnLoadingWs")} active={sortKey === "loading_ws"} direction={sortDir} onClick={() => toggleSort("loading_ws")} />
            <SortableHead label={t("columnLoadingDate")} active={sortKey === "loading_date"} direction={sortDir} onClick={() => toggleSort("loading_date")} />
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map((row) => (
            <TableRow key={row.trolley_code}>
              <TableCell className="font-medium">{row.trolley_code}</TableCell>
              <TableCell className="text-muted-foreground">{row.wb_code ?? "—"}</TableCell>
              <TableCell>{row.area ?? t("noArea")}</TableCell>
              <TableCell>{row.color_code}</TableCell>
              <TableCell className="text-right tabular-nums">{row.qty ?? "—"}</TableCell>
              <TableCell>{row.loading_ws}</TableCell>
              <TableCell className="tabular-nums">{formatDate(row.loading_date, lang)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

function formatDate(iso: string | null, lang: Lang): string {
  if (!iso) return "—";
  const date = new Date(iso);
  return date.toLocaleDateString(lang === "vi" ? "vi-VN" : "en-US");
}
