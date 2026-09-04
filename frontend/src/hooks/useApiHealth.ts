import { useCallback, useEffect, useState } from "react";
import { api, ApiError, getApiBaseUrl } from "../api";

export function useApiHealth(pollMs = 15000) {
  const [ok, setOk] = useState<boolean | null>(null);
  const [message, setMessage] = useState("Checking API…");
  const [baseUrl] = useState(() => getApiBaseUrl());

  const check = useCallback(async () => {
    try {
      const health = await api.health();
      setOk(true);
      const ver = health.version ? ` v${health.version}` : "";
      setMessage(
        health.status === "ok" || health.status === "healthy"
          ? `Connected${ver} · ${baseUrl}`
          : `${health.status}${ver} · ${baseUrl}`,
      );
    } catch (err) {
      setOk(false);
      setMessage(
        err instanceof ApiError
          ? err.message
          : `API unreachable · ${baseUrl}`,
      );
    }
  }, [baseUrl]);

  useEffect(() => {
    void check();
    const id = setInterval(() => {
      void check();
    }, pollMs);
    return () => clearInterval(id);
  }, [check, pollMs]);

  return { ok, message, baseUrl, check };
}
