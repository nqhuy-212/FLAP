"use client";

import { Suspense, useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";

import { getWipKpi } from "@/lib/api";
import { useLiveData } from "@/lib/useLiveData";
import type { WipKpi } from "@/lib/types";
import { getDictionary, isLang, type Lang } from "@/i18n/dictionaries";
import { TV_COLORS, AGE_BUCKET_RAMP, TV_FONT_FAMILY } from "@/components/tv/colors";
import { Card } from "@/components/tv/Card";
import { StatTile } from "@/components/tv/StatTile";
import { HorizontalBarChart } from "@/components/tv/HorizontalBarChart";
import { TrendChart } from "@/components/tv/TrendChart";
import { TopAgingTable } from "@/components/tv/TopAgingTable";
import { ConnectionIndicator } from "@/components/tv/ConnectionIndicator";

export default function TvWipPage() {
  return (
    <Suspense fallback={<TvShell><FullscreenMessage text="..." /></TvShell>}>
      <TvWipDashboard />
    </Suspense>
  );
}

function TvWipDashboard() {
  const searchParams = useSearchParams();
  const langParam = searchParams.get("lang");
  const lang: Lang = isLang(langParam) ? langParam : "vi";
  const dict = getDictionary(lang);
  const t = useCallback((key: keyof typeof dict) => dict[key], [dict]);
  // Tiêu đề trang luôn hiện song ngữ (yêu cầu người dùng 2026-08-08) — độc lập
  // với `lang` từ URL, thứ chỉ điều khiển nhãn còn lại (card title, cột bảng...).
  const dictVi = getDictionary("vi");
  const dictEn = getDictionary("en");

  const [kpi, setKpi] = useState<WipKpi | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const reload = useCallback(() => {
    getWipKpi()
      .then((data) => {
        setKpi(data);
        setError(null);
        setLastUpdated(new Date());
      })
      .catch((err: unknown) => setError(err instanceof Error ? err.message : String(err)));
    // Không xoá `kpi` cũ khi lỗi/đang tải lại — giữ nguyên bản render trước đó
    // (xem dataviz skill: "Skeleton flash on refetch" là anti-pattern).
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  const status = useLiveData(() => reload());

  const numberFormat = useMemo(() => new Intl.NumberFormat(lang === "vi" ? "vi-VN" : "en-US"), [lang]);
  const format = useCallback((v: number) => numberFormat.format(v), [numberFormat]);

  if (error && !kpi) {
    return (
      <TvShell>
        <FullscreenMessage text={`${t("error")}: ${error}`} />
      </TvShell>
    );
  }

  if (!kpi) {
    return (
      <TvShell>
        <FullscreenMessage text={t("loading")} />
      </TvShell>
    );
  }

  return (
    <TvShell>
      <header
        className="flex items-center justify-between px-12 py-6"
        style={{ borderBottom: `1px solid ${TV_COLORS.border}` }}
      >
        <div className="flex flex-col gap-1">
          <h1 className="text-[40px] font-semibold leading-tight tracking-tight" style={{ color: TV_COLORS.textPrimary }}>
            {dictVi.appTitle} — {dictVi.wipOverview}
          </h1>
          <p className="text-[32px] leading-none" style={{ color: TV_COLORS.muted, opacity: 0.78 }}>
            {dictEn.appTitle} — {dictEn.wipOverview}
          </p>
        </div>
        <ConnectionIndicator status={status} lastUpdated={lastUpdated} lang={lang} t={t} />
      </header>

      <main className="grid flex-1 grid-rows-[260px_1fr] gap-5 px-12 py-6">
        {/* Hàng 1: 2 hero figure + phân bổ theo khu vực */}
        <div className="grid grid-cols-[420px_420px_1fr] gap-5">
          <Card title={dictVi.totalTrolley} subtitle={dictEn.totalTrolley}>
            <StatTile value={format(kpi.total_trolley)} />
          </Card>
          <Card title={dictVi.totalQty} subtitle={dictEn.totalQty}>
            <StatTile value={format(kpi.total_qty)} />
          </Card>
          <Card title={dictVi.areaBreakdown} subtitle={dictEn.areaBreakdown}>
            <HorizontalBarChart
              data={kpi.area_breakdown.map((b) => ({
                label: b.area ?? t("noArea"),
                value: b.trolley_count,
                color: TV_COLORS.singleSeries,
              }))}
              formatValue={format}
              width={900}
              height={Math.max(34, Math.min(46, 168 / Math.max(1, kpi.area_breakdown.length)))}
              labelColumnWidth={190}
              valueColumnWidth={130}
              barThickness={20}
              labelFontSize={22}
              valueFontSize={24}
            />
          </Card>
        </div>

        {/* Hàng 2: nhóm tuổi WIP · top tồn lâu nhất · xu hướng theo ngày.
            Cột giữa (bảng) rộng hơn 2 cột hai bên — Century Gothic rộng hơn
            font mặc định trước đó, bảng 5 cột cần nhiều chỗ hơn biểu đồ. */}
        <div className="grid gap-5 overflow-hidden" style={{ gridTemplateColumns: "0.85fr 1.3fr 0.85fr" }}>
          <Card title={dictVi.ageBuckets} subtitle={dictEn.ageBuckets}>
            <HorizontalBarChart
              data={kpi.age_buckets.map((b, i) => ({
                label: `${b.label} ${t("days")}`,
                value: b.trolley_count,
                color: AGE_BUCKET_RAMP[i] ?? AGE_BUCKET_RAMP[AGE_BUCKET_RAMP.length - 1],
              }))}
              formatValue={format}
              width={430}
              height={110}
              labelColumnWidth={120}
              valueColumnWidth={90}
              barThickness={18}
              labelFontSize={19}
              valueFontSize={21}
            />
          </Card>
          <Card title={dictVi.topAging} subtitle={dictEn.topAging} className="overflow-hidden">
            <TopAgingTable items={kpi.top_aging} t={t} tVi={(k) => dictVi[k]} tEn={(k) => dictEn[k]} />
          </Card>
          <Card title={dictVi.loadingTrend} subtitle={dictEn.loadingTrend}>
            <TrendChart
              data={kpi.loading_trend.map((p) => ({ date: p.date, value: p.trolley_count }))}
              formatValue={format}
              width={430}
              height={470}
            />
          </Card>
        </div>
      </main>
    </TvShell>
  );
}

function TvShell({ children }: { children: React.ReactNode }) {
  return (
    <div
      className="flex h-screen w-screen items-center justify-center overflow-hidden"
      style={{ backgroundColor: TV_COLORS.pagePlane }}
    >
      <div
        className="flex h-[1080px] w-[1920px] flex-col overflow-hidden"
        style={{ backgroundColor: TV_COLORS.pagePlane, fontFamily: TV_FONT_FAMILY }}
      >
        {children}
      </div>
    </div>
  );
}

function FullscreenMessage({ text }: { text: string }) {
  return (
    <div className="flex h-full items-center justify-center">
      <span className="text-[40px]" style={{ color: TV_COLORS.textSecondary }}>
        {text}
      </span>
    </div>
  );
}
