"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Moon, Settings, Sun } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { getWipDetail, getWipSummary } from "@/lib/api";
import { useLiveData } from "@/lib/useLiveData";
import { useTheme } from "@/lib/theme";
import { useI18n } from "@/i18n/context";
import { downloadCsv } from "@/lib/csv";
import type { WipSummary, WipTrolley } from "@/lib/types";
import { FilterBar, EMPTY_FILTERS, type WipFilters } from "@/components/pc/FilterBar";
import { SummaryTable } from "@/components/pc/SummaryTable";
import { DetailTable } from "@/components/pc/DetailTable";

export default function PcWipPage() {
  const { lang, setLang, t } = useI18n();
  const { theme, toggleTheme } = useTheme();

  const [trolleys, setTrolleys] = useState<WipTrolley[]>([]);
  const [summaries, setSummaries] = useState<WipSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [filters, setFilters] = useState<WipFilters>(EMPTY_FILTERS);
  const [selectedMo, setSelectedMo] = useState<string | null>(null);

  const reload = useCallback(() => {
    Promise.all([getWipDetail(), getWipSummary()])
      .then(([detail, summary]) => {
        setTrolleys(detail);
        setSummaries(summary);
        setError(null);
        setLastUpdated(new Date());
      })
      .catch((err: unknown) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  const status = useLiveData(() => reload());

  const filterOptions = useMemo(
    () => ({
      styles: uniqueSorted(trolleys.map((t) => t.cust_style)),
      colors: uniqueSorted(trolleys.map((t) => t.color_code)),
      areas: uniqueSorted(trolleys.map((t) => t.area).filter((a): a is string => a !== null)),
      workstations: uniqueSorted(trolleys.map((t) => t.loading_ws)),
    }),
    [trolleys],
  );

  const filteredTrolleys = useMemo(() => applyFilters(trolleys, filters), [trolleys, filters]);

  const visibleMoNumbers = useMemo(
    () => new Set(filteredTrolleys.map((t) => t.mo_no)),
    [filteredTrolleys],
  );

  const visibleSummaries = useMemo(
    () => summaries.filter((s) => visibleMoNumbers.has(s.mo_no)),
    [summaries, visibleMoNumbers],
  );

  // Không lưu "MO đang chọn đã bị lọc mất" như 1 trạng thái riêng cần effect
  // sửa lại — tính thẳng giá trị hiệu lực mỗi lần render (đơn giản hơn, đúng
  // khuyến nghị "bạn có thể không cần effect" thay vì setState trong effect).
  const effectiveSelectedMo = selectedMo && visibleMoNumbers.has(selectedMo) ? selectedMo : null;

  const drillDownRows = useMemo(
    () => (effectiveSelectedMo ? filteredTrolleys.filter((t) => t.mo_no === effectiveSelectedMo) : []),
    [filteredTrolleys, effectiveSelectedMo],
  );

  const handleExportCsv = () => {
    if (effectiveSelectedMo) {
      downloadCsv(
        drillDownRows,
        [
          { key: "trolley_code", header: t("columnTrolleyCode") },
          { key: "wb_code", header: t("columnWbCode") },
          { key: "area", header: t("columnArea") },
          { key: "so_no", header: t("columnSoNo") },
          { key: "mo_no", header: t("columnMo") },
          { key: "cust_style", header: t("columnStyle") },
          { key: "color_code", header: t("columnColor") },
          { key: "qty", header: t("columnQty") },
          { key: "loading_ws", header: t("columnLoadingWs") },
          { key: "loading_date", header: t("columnLoadingDate") },
        ],
        `wip_detail_${effectiveSelectedMo}.csv`,
      );
    } else {
      downloadCsv(
        visibleSummaries,
        [
          { key: "cust_style", header: t("columnStyle") },
          { key: "graphic", header: t("columnGraphic") },
          { key: "mo_no", header: t("columnMo") },
          { key: "total_trolley", header: t("columnTrolleyCount") },
          { key: "cut_qty", header: t("columnCutQty") },
          { key: "deduct_qty", header: t("columnDeductQty") },
          { key: "qty_after_deduct", header: t("columnQtyAfterDeduct") },
          { key: "total_qty", header: t("columnQty") },
          { key: "avg_wip_cct", header: t("columnAvgWipCct") },
          { key: "avg_wip_vap", header: t("columnAvgWipVap") },
          { key: "avg_wip_pdc", header: t("columnAvgWipPdc") },
        ],
        "wip_summary.csv",
      );
    }
  };

  const selectedSummary = effectiveSelectedMo
    ? summaries.find((s) => s.mo_no === effectiveSelectedMo)
    : undefined;

  return (
    <main className="mx-auto flex max-w-[1600px] flex-1 flex-col gap-6 p-8">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">{t("appTitle")} — {t("wipOverview")}</h1>
          <div className="mt-1 flex items-center gap-3 text-sm text-muted-foreground">
            <span>{t(status)}</span>
            {lastUpdated && (
              <span>
                {t("lastUpdated")}: {lastUpdated.toLocaleTimeString(lang === "vi" ? "vi-VN" : "en-US")}
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" variant={lang === "vi" ? "default" : "outline"} onClick={() => setLang("vi")}>
            VI
          </Button>
          <Button size="sm" variant={lang === "en" ? "default" : "outline"} onClick={() => setLang("en")}>
            EN
          </Button>
          <Button size="sm" variant="outline" onClick={toggleTheme} aria-label="toggle theme">
            {theme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
          </Button>
          <Link
            href="/pc/system"
            className={buttonVariants({ variant: "outline", size: "sm" })}
            aria-label="system status"
          >
            <Settings className="size-4" />
          </Link>
        </div>
      </header>

      {error && (
        <div className="flex items-center gap-3 rounded-lg border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive">
          <span>{t("error")}: {error}</span>
          <Button size="sm" variant="outline" onClick={reload}>
            {t("retry")}
          </Button>
        </div>
      )}

      <FilterBar
        filters={filters}
        onChange={(patch) => setFilters((f) => ({ ...f, ...patch }))}
        onClear={() => setFilters(EMPTY_FILTERS)}
        options={filterOptions}
        t={t}
      />

      <section className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {effectiveSelectedMo ? (
              <>
                <Button size="sm" variant="ghost" onClick={() => setSelectedMo(null)}>
                  {t("backToSummary")}
                </Button>
                <h2 className="text-lg font-medium">
                  {t("detailTable")} — {selectedSummary?.cust_style ?? effectiveSelectedMo} ({effectiveSelectedMo})
                </h2>
              </>
            ) : (
              <>
                <h2 className="text-lg font-medium">{t("summaryTable")}</h2>
                <Badge variant="secondary">
                  {visibleSummaries.length} {t("matchingRows")}
                </Badge>
              </>
            )}
          </div>
          <Button size="sm" variant="outline" onClick={handleExportCsv}>
            {t("exportCsv")}
          </Button>
        </div>

        {effectiveSelectedMo ? (
          <DetailTable rows={drillDownRows} lang={lang} t={t} />
        ) : (
          <SummaryTable rows={visibleSummaries} onSelectMo={setSelectedMo} t={t} />
        )}
      </section>
    </main>
  );
}

function uniqueSorted(values: string[]): string[] {
  return Array.from(new Set(values)).sort((a, b) => a.localeCompare(b));
}

function applyFilters(trolleys: WipTrolley[], filters: WipFilters): WipTrolley[] {
  return trolleys.filter((t) => {
    if (filters.style && t.cust_style !== filters.style) return false;
    if (filters.color && t.color_code !== filters.color) return false;
    if (filters.area && t.area !== filters.area) return false;
    if (filters.workstation && t.loading_ws !== filters.workstation) return false;
    if (filters.dateFrom || filters.dateTo) {
      if (!t.loading_date) return false;
      const day = t.loading_date.slice(0, 10);
      if (filters.dateFrom && day < filters.dateFrom) return false;
      if (filters.dateTo && day > filters.dateTo) return false;
    }
    return true;
  });
}
