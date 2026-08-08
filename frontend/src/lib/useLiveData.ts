"use client";

import { useEffect, useRef, useState } from "react";

import { apiUrl } from "./api";

export type ConnectionStatus = "connecting" | "connected" | "disconnected";

interface DataChangedPayload {
  file: string;
}

/**
 * Bọc EventSource cho /api/stream. `EventSource` tự kết nối lại khi rớt mạng
 * (CLAUDE.md quyết định #2) — hook chỉ cần phản ánh trạng thái, không tự retry.
 */
export function useLiveData(onDataChanged: (file: string) => void): ConnectionStatus {
  const [status, setStatus] = useState<ConnectionStatus>("connecting");
  const onDataChangedRef = useRef(onDataChanged);

  useEffect(() => {
    onDataChangedRef.current = onDataChanged;
  }, [onDataChanged]);

  useEffect(() => {
    const source = new EventSource(apiUrl("/api/stream"));

    source.onopen = () => setStatus("connected");
    source.onerror = () => setStatus("disconnected");

    source.addEventListener("data_changed", (event: MessageEvent<string>) => {
      try {
        const payload = JSON.parse(event.data) as DataChangedPayload;
        onDataChangedRef.current(payload.file);
      } catch {
        // payload không đúng định dạng — bỏ qua, không phải lỗi nghiêm trọng
      }
    });

    return () => source.close();
  }, []);

  return status;
}
