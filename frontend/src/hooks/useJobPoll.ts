import { useCallback, useEffect, useRef, useState } from "react";
import { api, ApiError } from "../api";
import type { Job, JobStatus } from "../types/api";

const TERMINAL: JobStatus[] = ["completed", "failed"];

export interface UseJobPollOptions {
  intervalMs?: number;
  enabled?: boolean;
  onComplete?: (job: Job) => void;
  onFailed?: (job: Job) => void;
}

export function useJobPoll(jobId: string | null, options: UseJobPollOptions = {}) {
  const { intervalMs = 1000, enabled = true, onComplete, onFailed } = options;
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [polling, setPolling] = useState(false);
  const onCompleteRef = useRef(onComplete);
  const onFailedRef = useRef(onFailed);
  onCompleteRef.current = onComplete;
  onFailedRef.current = onFailed;

  const refresh = useCallback(async () => {
    if (!jobId) return null;
    try {
      const next = await api.getJob(jobId);
      setJob(next);
      setError(null);
      return next;
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Failed to fetch job";
      setError(msg);
      return null;
    }
  }, [jobId]);

  useEffect(() => {
    if (!jobId || !enabled) {
      setPolling(false);
      return;
    }

    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | undefined;

    const tick = async () => {
      setPolling(true);
      const next = await refresh();
      if (cancelled) return;

      if (next && TERMINAL.includes(next.status)) {
        setPolling(false);
        if (next.status === "completed") onCompleteRef.current?.(next);
        if (next.status === "failed") onFailedRef.current?.(next);
        return;
      }

      timer = setTimeout(() => {
        void tick();
      }, intervalMs);
    };

    void tick();

    return () => {
      cancelled = true;
      setPolling(false);
      if (timer) clearTimeout(timer);
    };
  }, [jobId, enabled, intervalMs, refresh]);

  return { job, error, polling, refresh };
}
