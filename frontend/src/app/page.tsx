"use client";

import { useCallback, useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useI18n } from "@/i18n/context";
import { getWipKpi } from "@/lib/api";
import type { ConnectionStatus } from "@/lib/useLiveData";
import { useLiveData } from "@/lib/useLiveData";
import type { WipKpi } from "@/lib/types";

const STATUS_VARIANT: Record<ConnectionStatus, "secondary" | "default" | "destructive"> = {
  connecting: "secondary",
  connected: "default",
  disconnected: "destructive",
};

export default function Home() {
  const { lang, setLang, t } = useI18n();
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
  }, []);

  useEffect(() => {
    reload();
  }, [reload]);

  const status = useLiveData(() => reload());

  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-6 p-8">
      <div className="flex items-center gap-2">
        <Button
          size="sm"
          variant={lang === "vi" ? "default" : "outline"}
          onClick={() => setLang("vi")}
        >
          VI
        </Button>
        <Button
          size="sm"
          variant={lang === "en" ? "default" : "outline"}
          onClick={() => setLang("en")}
        >
          EN
        </Button>
      </div>

      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>{t("appTitle")}</CardTitle>
          <CardDescription>{t("wipOverview")}</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          {error && (
            <div className="flex flex-col gap-2 text-sm text-destructive">
              <p>
                {t("error")}: {error}
              </p>
              <Button size="sm" variant="outline" onClick={reload}>
                {t("retry")}
              </Button>
            </div>
          )}

          {!kpi && !error && <p className="text-sm text-muted-foreground">{t("loading")}</p>}

          {kpi && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-muted-foreground">{t("totalTrolley")}</p>
                <p className="text-2xl font-semibold">{kpi.total_trolley.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{t("totalQty")}</p>
                <p className="text-2xl font-semibold">{kpi.total_qty.toLocaleString()}</p>
              </div>
            </div>
          )}

          <div className="flex items-center justify-between border-t pt-3 text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <span>{t("connectionStatus")}:</span>
              <Badge variant={STATUS_VARIANT[status]}>{t(status)}</Badge>
            </div>
            {lastUpdated && (
              <span>
                {t("lastUpdated")}: {lastUpdated.toLocaleTimeString(lang === "vi" ? "vi-VN" : "en-US")}
              </span>
            )}
          </div>
        </CardContent>
      </Card>
    </main>
  );
}
