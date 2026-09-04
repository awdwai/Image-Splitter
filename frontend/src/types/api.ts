/** Types mirroring AnimAI backend OpenAPI schemas (`backend/app/schemas`). */

export type JobStatus = "queued" | "running" | "completed" | "failed";

export type JobType = "analyze" | "segment" | "process";

export type ExportFormat = "png_layers" | "psd" | "json";

export type ExportStatus = "ready" | "pending" | "failed";

export interface HealthResponse {
  status: string;
  service?: string;
  version?: string;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface ImageInfo {
  id: string;
  filename: string;
  content_type: string;
  width: number;
  height: number;
  created_at: string;
  url: string;
}

export interface ModelInfo {
  id: string;
  name: string;
  kind: string;
  description: string;
  available: boolean;
  is_stub: boolean;
}

export interface ModelsResponse {
  models: ModelInfo[];
}

export interface ProcessJobRequest {
  image_id: string;
  model_id?: string | null;
  options?: Record<string, unknown>;
}

export interface AnalyzeJobRequest {
  image_id: string;
  model_id?: string | null;
  options?: Record<string, unknown>;
}

export interface SegmentJobRequest {
  image_id: string;
  model_id?: string | null;
  detection_ids?: string[] | null;
  options?: Record<string, unknown>;
}

export interface Job {
  id: string;
  type: JobType;
  status: JobStatus;
  /** 0.0–1.0 progress fraction */
  progress: number;
  image_id: string;
  message?: string | null;
  error?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Detection {
  id: string;
  label: string;
  confidence: number;
  bbox: BoundingBox;
}

export interface Keypoint {
  name: string;
  x: number;
  y: number;
  confidence: number;
}

export interface PoseResult {
  keypoints: Keypoint[];
  skeleton: string[][];
}

export interface MaskInfo {
  id: string;
  label: string;
  score: number;
  bbox?: BoundingBox | null;
  mask_url?: string | null;
}

export interface LayerInfo {
  id: string;
  name: string;
  kind: string;
  z_index: number;
  opacity: number;
  visible: boolean;
  mask_url?: string | null;
  image_url?: string | null;
}

export interface JobResults {
  job_id: string;
  image_id: string;
  detections: Detection[];
  pose?: PoseResult | null;
  masks: MaskInfo[];
  layers: LayerInfo[];
  meta: Record<string, unknown>;
}

export interface MaskCorrection {
  id: string;
  label?: string | null;
  mask_url?: string | null;
  bbox?: BoundingBox | null;
  deleted?: boolean;
}

export interface LayerCorrection {
  id: string;
  name?: string | null;
  visible?: boolean | null;
  opacity?: number | null;
  z_index?: number | null;
  deleted?: boolean;
}

export interface CorrectionRequest {
  masks?: MaskCorrection[] | null;
  layers?: LayerCorrection[] | null;
  notes?: string | null;
}

export interface ExportRequest {
  format: ExportFormat;
  options?: Record<string, unknown>;
}

export interface ExportResponse {
  id: string;
  job_id: string;
  format: ExportFormat;
  status: ExportStatus | string;
  download_url?: string | null;
  created_at: string;
  error?: string | null;
}

export interface ApiErrorBody {
  detail?: string | { msg: string }[] | Record<string, unknown>;
  message?: string;
  error?: string;
}
