import { useCallback, useEffect, useMemo, useState } from "react";
import { api, ApiError, resolveMediaUrl } from "../api";
import { ExportPanel, ModelPicker } from "../components/ExportPanel";
import { ImageUpload } from "../components/ImageUpload";
import { JobProgress } from "../components/JobProgress";
import {
  LayerList,
  MaskList,
  ResultCanvas,
} from "../components/ResultView";
import { StatusBanner } from "../components/StatusBanner";
import { useApiHealth } from "../hooks/useApiHealth";
import { useJobPoll } from "../hooks/useJobPoll";
import type {
  ExportFormat,
  ExportResponse,
  ImageInfo,
  JobResults,
  LayerInfo,
  ModelInfo,
} from "../types/api";

type Phase =
  | "idle"
  | "uploading"
  | "starting"
  | "polling"
  | "ready"
  | "correcting"
  | "exporting";

export function WorkspacePage() {
  const health = useApiHealth();
  const [phase, setPhase] = useState<Phase>("idle");
  const [error, setError] = useState<string | null>(null);
  const [localPreview, setLocalPreview] = useState<string | null>(null);
  const [image, setImage] = useState<ImageInfo | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [results, setResults] = useState<JobResults | null>(null);
  const [editableLayers, setEditableLayers] = useState<LayerInfo[]>([]);
  const [selectedLayers, setSelectedLayers] = useState<Set<string>>(new Set());
  const [selectedMasks, setSelectedMasks] = useState<Set<string>>(new Set());
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selectedModelId, setSelectedModelId] = useState<string | null>(null);
  const [exportFormat, setExportFormat] = useState<ExportFormat>("png_layers");
  const [exportRecord, setExportRecord] = useState<ExportResponse | null>(null);
  const [statusNote, setStatusNote] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const res = await api.listModels();
        setModels(res.models ?? []);
      } catch {
        // Backend may still be warming this route
      }
    })();
  }, []);

  useEffect(() => {
    return () => {
      if (localPreview) URL.revokeObjectURL(localPreview);
    };
  }, [localPreview]);

  const applyResults = useCallback((data: JobResults) => {
    setResults(data);
    const layers = data.layers ?? [];
    setEditableLayers(layers.map((l) => ({ ...l })));
    setSelectedLayers(
      new Set(layers.filter((l) => l.visible).map((l) => l.id)),
    );
    setSelectedMasks(new Set((data.masks ?? []).map((m) => m.id)));
  }, []);

  const loadResults = useCallback(
    async (id: string) => {
      const data = await api.getJobResults(id);
      applyResults(data);
      setPhase("ready");
      setStatusNote("Results loaded.");
    },
    [applyResults],
  );

  const { job, error: pollError, polling } = useJobPoll(jobId, {
    enabled: phase === "polling" || phase === "starting",
    onComplete: (completed) => {
      void loadResults(completed.id).catch((err) => {
        setError(
          err instanceof ApiError ? err.message : "Failed to load results",
        );
        setPhase("idle");
      });
    },
    onFailed: (failed) => {
      setError(failed.error || "Job failed");
      setPhase("idle");
    },
  });

  const sourcePreview = useMemo(() => {
    return resolveMediaUrl(image?.url) ?? localPreview;
  }, [image, localPreview]);

  const busy =
    phase === "uploading" ||
    phase === "starting" ||
    phase === "polling" ||
    phase === "correcting" ||
    phase === "exporting";

  const onFile = async (file: File) => {
    setError(null);
    setStatusNote(null);
    setExportRecord(null);
    setResults(null);
    setEditableLayers([]);
    setJobId(null);
    if (localPreview) URL.revokeObjectURL(localPreview);
    setLocalPreview(URL.createObjectURL(file));
    setPhase("uploading");

    try {
      const uploaded = await api.uploadImage(file);
      setImage(uploaded);
      setPhase("starting");
      setStatusNote("Image registered — starting process job…");

      const started = await api.startProcess({
        image_id: uploaded.id,
        model_id: selectedModelId,
        options: {},
      });
      setJobId(started.id);
      setPhase("polling");
      setStatusNote("Process job running…");
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Upload / process failed",
      );
      setPhase("idle");
    }
  };

  const toggleLayer = (id: string) => {
    setSelectedLayers((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleMask = (id: string) => {
    setSelectedMasks((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const renameLayer = (id: string, name: string) => {
    setEditableLayers((prev) =>
      prev.map((l) => (l.id === id ? { ...l, name } : l)),
    );
  };

  const setLayerOpacity = (id: string, opacity: number) => {
    setEditableLayers((prev) =>
      prev.map((l) => (l.id === id ? { ...l, opacity } : l)),
    );
  };

  const sendCorrections = async () => {
    if (!jobId) return;
    setError(null);
    setPhase("correcting");
    try {
      const originalById = new Map(
        (results?.layers ?? []).map((l) => [l.id, l]),
      );
      const layerPatches = editableLayers
        .map((l) => {
          const orig = originalById.get(l.id);
          if (!orig) return null;
          const patch: {
            id: string;
            name?: string;
            opacity?: number;
            visible?: boolean;
          } = { id: l.id };
          let changed = false;
          if (l.name !== orig.name) {
            patch.name = l.name;
            changed = true;
          }
          if (l.opacity !== orig.opacity) {
            patch.opacity = l.opacity;
            changed = true;
          }
          const visible = selectedLayers.has(l.id);
          if (visible !== orig.visible) {
            patch.visible = visible;
            changed = true;
          }
          return changed ? patch : null;
        })
        .filter((p): p is NonNullable<typeof p> => p != null);

      const updated = await api.applyCorrections(jobId, {
        layers: layerPatches,
        notes: "Client UI corrections",
      });
      applyResults(updated);
      setStatusNote("Corrections applied.");
      setPhase("ready");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Corrections failed");
      setPhase("ready");
    }
  };

  const requestExport = async () => {
    if (!jobId) return;
    setError(null);
    setPhase("exporting");
    try {
      let record = await api.requestExport(jobId, {
        format: exportFormat,
        options: {},
      });

      const terminal = new Set(["ready", "failed"]);
      let attempts = 0;
      while (!terminal.has(record.status) && attempts < 30) {
        await new Promise((r) => setTimeout(r, 800));
        record = await api.getExport(record.id);
        attempts += 1;
      }

      if (record.download_url) {
        record = {
          ...record,
          download_url:
            resolveMediaUrl(record.download_url) ?? record.download_url,
        };
      }

      setExportRecord(record);
      if (record.status === "failed") {
        setError(record.error || "Export failed");
      } else {
        setStatusNote(`Export ${record.status}.`);
      }
      setPhase("ready");
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Export request failed",
      );
      setPhase("ready");
    }
  };

  const displayResults = useMemo(() => {
    if (!results) return null;
    return {
      ...results,
      layers: editableLayers.map((l) => ({
        ...l,
        visible: selectedLayers.has(l.id),
      })),
    };
  }, [results, editableLayers, selectedLayers]);

  return (
    <div className="app-shell">
      <header className="hero">
        <div className="hero__brand">
          <span className="hero__mark" aria-hidden />
          <h1>AnimAI</h1>
        </div>
        <p className="hero__tag">
          Decompose a still into editable layers — this UI is a thin client of
          the AnimAI API.
        </p>
        <StatusBanner ok={health.ok} message={health.message} />
      </header>

      <main className="workspace">
        <aside className="workspace__side">
          <section className="panel">
            <div className="panel__head">
              <h2>Source</h2>
            </div>
            <ImageUpload disabled={busy} onFile={(f) => void onFile(f)} />
            {image ? (
              <p className="mono muted tight">
                {image.filename} · {image.width}×{image.height} · {image.id}
              </p>
            ) : null}
            <ModelPicker
              models={models}
              selectedId={selectedModelId}
              onChange={setSelectedModelId}
              disabled={busy}
            />
          </section>

          <JobProgress job={job} polling={polling} />

          {(error || pollError) && (
            <div className="alert alert--error" role="alert">
              {error || pollError}
            </div>
          )}
          {statusNote && !error && !pollError ? (
            <div className="alert alert--info">{statusNote}</div>
          ) : null}

          <LayerList
            layers={editableLayers}
            selected={selectedLayers}
            onToggle={toggleLayer}
            onRename={renameLayer}
            onOpacity={setLayerOpacity}
          />

          <MaskList
            masks={results?.masks ?? []}
            selected={selectedMasks}
            onToggle={toggleMask}
          />

          <div className="actions">
            <button
              type="button"
              className="btn btn--secondary"
              disabled={!jobId || phase !== "ready"}
              onClick={() => void sendCorrections()}
            >
              {phase === "correcting" ? "Sending…" : "Send corrections"}
            </button>
          </div>

          <ExportPanel
            disabled={!jobId || phase !== "ready"}
            format={exportFormat}
            onFormatChange={setExportFormat}
            onExport={() => void requestExport()}
            busy={phase === "exporting"}
            record={exportRecord}
          />
        </aside>

        <div className="workspace__main">
          <ResultCanvas
            sourcePreviewUrl={sourcePreview}
            results={displayResults}
            selectedLayerIds={selectedLayers}
            selectedMaskIds={selectedMasks}
          />
        </div>
      </main>

      <footer className="app-footer">
        <span>Example client · no local AI</span>
        <span className="mono">{health.baseUrl}</span>
      </footer>
    </div>
  );
}
