/**
 * Kiểu dữ liệu khớp với Pydantic models ở backend (backend/app/models/).
 * Backend trả mã gốc, không dịch — bản dịch nhãn nằm ở src/i18n/ (CLAUDE.md quyết định #5).
 */

export interface WipTrolley {
  trolley_code: string;
  wb_code: string | null;
  area: string | null;
  so_no: string;
  mo_no: string;
  cust_style: string;
  flower_code: string;
  color_code: string;
  print_to_edge: string | null;
  bed_no: string[];
  size_no: string[];
  qty: number | null;
  loading_ws: string;
  loading_date: string | null;
  in_vap_date: string | null;
  back_cct_date: string | null;
  wip_cct: number | null;
  wip_vap: number | null;
  pdc_wip: number | null;
}

export interface WipSummary {
  cust_style: string;
  graphic: string;
  mo_no: string;
  total_trolley: number;
  cut_qty: number | null;
  deduct_qty: number | null;
  qty_after_deduct: number | null;
  total_qty: number | null;
  avg_wip_cct: number | null;
  avg_wip_vap: number | null;
  avg_wip_pdc: number | null;
}

export interface AreaBreakdown {
  area: string | null;
  trolley_count: number;
  total_qty: number;
}

export interface AgeBucket {
  label: "0-3" | "4-7" | "8-14" | ">14";
  trolley_count: number;
  total_qty: number;
}

export interface TopAgingItem {
  mo_no: string;
  cust_style: string;
  max_age_days: number;
  trolley_count: number;
  total_qty: number;
}

export interface LoadingTrendPoint {
  date: string;
  trolley_count: number;
  total_qty: number;
}

export interface WipKpi {
  total_trolley: number;
  total_qty: number;
  area_breakdown: AreaBreakdown[];
  age_buckets: AgeBucket[];
  top_aging: TopAgingItem[];
  loading_trend: LoadingTrendPoint[];
}

export interface SourceFileInfo {
  name: string;
  generated_at: string | null;
  modified_at: string;
  row_count: number;
}

export interface SnapshotInfo {
  source: string;
  files: SourceFileInfo[];
}

export interface HealthResponse {
  status: string;
  datasource: string;
  snapshot: SnapshotInfo;
}

export interface LogTail {
  name: string;
  lines: string[];
}

export interface SystemStatus {
  status: string;
  datasource: string;
  uptime_seconds: number;
  watcher_running: boolean;
  snapshot: SnapshotInfo;
  logs: LogTail[];
}
