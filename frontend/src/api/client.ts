import type {
  AnalyzeJobRequest,
  ApiErrorBody,
  CorrectionRequest,
  ExportResponse,
  ExportRequest,
  HealthResponse,
  ImageInfo,
  Job,
  JobResults,
  ModelsResponse,
  ProcessJobRequest,
  SegmentJobRequest,
} from "../types/api";

const DEFAULT_BASE = "http://localhost:8000";

export function getApiBaseUrl(): string {
  const raw = import.meta.env.VITE_API_BASE_URL as string | undefined;
  const base = (raw?.trim() || DEFAULT_BASE).replace(/\/+$/, "");
  return base;
}

export class ApiError extends Error {
  readonly status: number;
  readonly body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

function messageFromBody(body: unknown, fallback: string): string {
  if (!body || typeof body !== "object") return fallback;
  const b = body as ApiErrorBody;
  if (typeof b.detail === "string") return b.detail;
  if (Array.isArray(b.detail)) {
    return b.detail.map((d) => d.msg).filter(Boolean).join("; ") || fallback;
  }
  if (typeof b.message === "string") return b.message;
  if (typeof b.error === "string") return b.error;
  return fallback;
}

async function parseJsonSafe(res: Response): Promise<unknown> {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const url = `${getApiBaseUrl()}${path}`;
  const headers = new Headers(init.headers);
  if (
    init.body &&
    !(init.body instanceof FormData) &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }

  let res: Response;
  try {
    res = await fetch(url, { ...init, headers });
  } catch (err) {
    const reason = err instanceof Error ? err.message : "Network error";
    throw new ApiError(
      `Cannot reach API at ${getApiBaseUrl()} (${reason}). Is the backend running?`,
      0,
      null,
    );
  }

  const body = await parseJsonSafe(res);
  if (!res.ok) {
    throw new ApiError(
      messageFromBody(body, `Request failed (${res.status})`),
      res.status,
      body,
    );
  }
  return body as T;
}

/** Resolve a media URL that may be absolute, data:, or API-relative. */
export function resolveMediaUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  if (
    url.startsWith("http://") ||
    url.startsWith("https://") ||
    url.startsWith("data:") ||
    url.startsWith("blob:")
  ) {
    return url;
  }
  if (url.startsWith("/")) {
    return `${getApiBaseUrl()}${url}`;
  }
  return `${getApiBaseUrl()}/${url}`;
}

export const api = {
  health(): Promise<HealthResponse> {
    return request<HealthResponse>("/health");
  },

  listModels(): Promise<ModelsResponse> {
    return request<ModelsResponse>("/api/v1/models");
  },

  async uploadImage(file: File): Promise<ImageInfo> {
    const form = new FormData();
    form.append("file", file);
    return request<ImageInfo>("/api/v1/images", {
      method: "POST",
      body: form,
    });
  },

  startProcess(body: ProcessJobRequest): Promise<Job> {
    return request<Job>("/api/v1/jobs/process", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  startAnalyze(body: AnalyzeJobRequest): Promise<Job> {
    return request<Job>("/api/v1/jobs/analyze", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  startSegment(body: SegmentJobRequest): Promise<Job> {
    return request<Job>("/api/v1/jobs/segment", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  getJob(jobId: string): Promise<Job> {
    return request<Job>(`/api/v1/jobs/${encodeURIComponent(jobId)}`);
  },

  getJobResults(jobId: string): Promise<JobResults> {
    return request<JobResults>(
      `/api/v1/jobs/${encodeURIComponent(jobId)}/results`,
    );
  },

  applyCorrections(
    jobId: string,
    body: CorrectionRequest,
  ): Promise<JobResults> {
    return request<JobResults>(
      `/api/v1/jobs/${encodeURIComponent(jobId)}/corrections`,
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    );
  },

  requestExport(jobId: string, body: ExportRequest): Promise<ExportResponse> {
    return request<ExportResponse>(
      `/api/v1/jobs/${encodeURIComponent(jobId)}/export`,
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    );
  },

  getExport(exportId: string): Promise<ExportResponse> {
    return request<ExportResponse>(
      `/api/v1/exports/${encodeURIComponent(exportId)}`,
    );
  },
};
