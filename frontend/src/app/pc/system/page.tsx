"use client";

import { useCallback, useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useI18n } from "@/i18n/context";
import { getSystemStatus } from "@/lib/api";
import type { SystemStatus } from "@/lib/types";

const TOKEN_STORAGE_KEY = "flap.system.token";
const REFRESH_MS = 15_000;

function getInitialToken(): string {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(TOKEN_STORAGE_KEY) ?? "";
}

function formatUptime(seconds: number, lang: "vi" | "en"): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const unitH = lang === "vi" ? "g" : "h";
  const unitM = lang === "vi" ? "p" : "m";
  return `${h}${unitH} ${m}${unitM}`;
}

export default function PcSystemPage() {
  const { lang, setLang, t } = useI18n();

  // Đọc token đã lưu từ localStorage bằng lazy initializer thay vì effect +
  // setState lúc mount (bài học Bước 6: react-hooks/set-state-in-effect).
  const [token, setToken] = useState<string>(getInitialToken);
  const [authedToken, setAuthedToken] = useState<string | null>(null);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback((tokenValue: string) => {
    setLoading(true);
    getSystemStatus(tokenValue)
      .then((data) => {
        setStatus(data);
        setError(null);
        setAuthedToken(tokenValue);
        window.localStorage.setItem(TOKEN_STORAGE_KEY, tokenValue);
      })
      .catch((err: unknown) => {
        setStatus(null);
        setAuthedToken(null);
        setError(err instanceof Error ? err.message : String(err));
      })
      .finally(() => setLoading(false));
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    load(token);
  };

  // Tự làm mới mỗi 15s SAU KHI đã xác thực — setState nằm trong callback bất
  // đồng bộ của timer, không phải gán thẳng trong thân effect.
  useEffect(() => {
    if (!authedToken) return;
    const id = setInterval(() => load(authedToken), REFRESH_MS);
    return () => clearInterval(id);
  }, [authedToken, load]);

  return (
    <main className="mx-auto flex max-w-[1200px] flex-1 flex-col gap-6 p-8">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">{t("systemStatus")}</h1>
        <div className="flex items-center gap-2">
          <Button size="sm" variant={lang === "vi" ? "default" : "outline"} onClick={() => setLang("vi")}>
            VI
          </Button>
          <Button size="sm" variant={lang === "en" ? "default" : "outline"} onClick={() => setLang("en")}>
            EN
          </Button>
        </div>
      </header>

      <Card>
        <CardContent className="pt-6">
          <form className="flex flex-wrap items-end gap-3" onSubmit={handleSubmit}>
            <div className="flex flex-1 min-w-[240px] flex-col gap-1.5">
              <Label htmlFor="system-token">{t("systemToken")}</Label>
              <Input
                id="system-token"
                type="password"
                autoComplete="off"
                placeholder={t("systemTokenPlaceholder")}
                value={token}
                onChange={(e) => setToken(e.target.value)}
              />
            </div>
            <Button type="submit" disabled={!token || loading}>
              {t("systemUnlock")}
            </Button>
            {authedToken && (
              <Button
                type="button"
                variant="outline"
                onClick={() => load(authedToken)}
                disabled={loading}
                aria-label={t("systemRefresh")}
              >
                <RefreshCw className={`size-4 ${loading ? "animate-spin" : ""}`} />
              </Button>
            )}
          </form>
          {error && (
            <p className="mt-3 text-sm text-destructive">
              {error === "invalid_token"
                ? t("systemTokenInvalid")
                : error === "token_not_configured"
                  ? t("systemTokenInvalid")
                  : error}
            </p>
          )}
          {!status && !error && <p className="mt-3 text-sm text-muted-foreground">{t("systemTokenRequired")}</p>}
        </CardContent>
      </Card>

      {status && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {t("systemDatasource")}
                </CardTitle>
              </CardHeader>
              <CardContent className="text-xl font-semibold">{status.datasource}</CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">{t("systemUptime")}</CardTitle>
              </CardHeader>
              <CardContent className="text-xl font-semibold">
                {formatUptime(status.uptime_seconds, lang)}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium text-muted-foreground">{t("systemWatcher")}</CardTitle>
              </CardHeader>
              <CardContent>
                <Badge variant={status.watcher_running ? "default" : "destructive"}>
                  {status.watcher_running ? t("systemWatcherRunning") : t("systemWatcherStopped")}
                </Badge>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>{t("systemSnapshotFiles")}</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-2 text-sm">
              {status.snapshot.files.map((f) => (
                <div key={f.name} className="flex flex-wrap items-center justify-between gap-2 border-b py-1.5 last:border-0">
                  <span className="font-medium">{f.name}</span>
                  <span className="text-muted-foreground">
                    {f.row_count} · {new Date(f.modified_at).toLocaleString(lang === "vi" ? "vi-VN" : "en-US")}
                  </span>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t("systemLogs")}</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              {status.logs.map((log) => (
                <div key={log.name} className="flex flex-col gap-1">
                  <span className="text-xs font-medium text-muted-foreground">{log.name}</span>
                  <pre className="h-48 overflow-auto rounded-md border bg-muted/40 p-2 text-xs whitespace-pre-wrap break-all">
                    {log.lines.length > 0 ? log.lines.join("\n") : "—"}
                  </pre>
                </div>
              ))}
            </CardContent>
          </Card>
        </>
      )}
    </main>
  );
}
