import { TV_COLORS } from "./colors";
import type { ConnectionStatus } from "@/lib/useLiveData";
import type { TranslationKey } from "@/i18n/dictionaries";

const STATUS_COLOR: Record<ConnectionStatus, string> = {
  connected: "#0ca30c", // status good (dark-surface contrast 5.19 — xem palette.md)
  connecting: "#fab219", // status warning
  disconnected: "#d03b3b", // status critical
};

const STATUS_KEY: Record<ConnectionStatus, TranslationKey> = {
  connected: "connected",
  connecting: "connecting",
  disconnected: "disconnected",
};

interface ConnectionIndicatorProps {
  status: ConnectionStatus;
  lastUpdated: Date | null;
  lang: "vi" | "en";
  t: (key: TranslationKey) => string;
}

/** Đèn báo kết nối — màu status luôn đi kèm chấm tròn + nhãn chữ, không dùng màu đơn độc. */
export function ConnectionIndicator({ status, lastUpdated, lang, t }: ConnectionIndicatorProps) {
  return (
    <div className="flex items-center gap-8 text-[26px]" style={{ color: TV_COLORS.textSecondary }}>
      <div className="flex items-center gap-3">
        <span
          className="inline-block h-4 w-4 rounded-full"
          style={{ backgroundColor: STATUS_COLOR[status] }}
          aria-hidden
        />
        <span>{t(STATUS_KEY[status])}</span>
      </div>
      {lastUpdated && (
        <span>
          {t("lastUpdated")}: {lastUpdated.toLocaleTimeString(lang === "vi" ? "vi-VN" : "en-US")}
        </span>
      )}
    </div>
  );
}
