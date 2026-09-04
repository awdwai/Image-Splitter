import { useEffect, useMemo, useRef, useState } from "react";
import { resolveMediaUrl } from "../api";
import type { JobResults, LayerInfo, MaskInfo } from "../types/api";

interface ResultCanvasProps {
  sourcePreviewUrl: string | null;
  results: JobResults | null;
  selectedLayerIds: Set<string>;
  selectedMaskIds: Set<string>;
}

function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`Failed to load ${src}`));
    img.src = src;
  });
}

const MASK_TINTS = [
  "rgba(232, 120, 72, 0.45)",
  "rgba(62, 156, 148, 0.45)",
  "rgba(214, 176, 64, 0.45)",
  "rgba(92, 132, 196, 0.45)",
  "rgba(176, 96, 148, 0.45)",
];

export function ResultCanvas({
  sourcePreviewUrl,
  results,
  selectedLayerIds,
  selectedMaskIds,
}: ResultCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [drawError, setDrawError] = useState<string | null>(null);

  const layers = useMemo(
    () =>
      (results?.layers ?? [])
        .filter((l) => l.visible !== false && selectedLayerIds.has(l.id))
        .slice()
        .sort((a, b) => a.z_index - b.z_index),
    [results, selectedLayerIds],
  );

  const masks = useMemo(
    () => (results?.masks ?? []).filter((m) => selectedMaskIds.has(m.id)),
    [results, selectedMaskIds],
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    let cancelled = false;

    const paint = async () => {
      setDrawError(null);
      try {
        if (!sourcePreviewUrl) {
          const ctx = canvas.getContext("2d");
          if (ctx) {
            canvas.width = 640;
            canvas.height = 360;
            ctx.fillStyle = "#1a2420";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
          }
          return;
        }

        const base = await loadImage(sourcePreviewUrl);
        if (cancelled) return;

        canvas.width = base.naturalWidth || 640;
        canvas.height = base.naturalHeight || 360;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(base, 0, 0);

        for (const layer of layers) {
          const url = resolveMediaUrl(layer.image_url);
          if (!url) continue;
          try {
            const img = await loadImage(url);
            if (cancelled) return;
            ctx.globalAlpha = Math.max(0, Math.min(1, layer.opacity ?? 1));
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            ctx.globalAlpha = 1;
          } catch {
            // Skip missing layer assets during scaffold demos
          }
        }

        for (let i = 0; i < masks.length; i += 1) {
          await drawMaskOverlay(ctx, canvas, masks[i], i);
          if (cancelled) return;
        }

        for (const det of results?.detections ?? []) {
          ctx.strokeStyle = "#e8f0c8";
          ctx.lineWidth = Math.max(1, canvas.width / 400);
          ctx.strokeRect(
            det.bbox.x,
            det.bbox.y,
            det.bbox.width,
            det.bbox.height,
          );
          ctx.fillStyle = "rgba(26, 58, 50, 0.85)";
          const label = `${det.label} ${Math.round(det.confidence * 100)}%`;
          ctx.font = `${Math.max(12, canvas.width / 60)}px DM Sans, sans-serif`;
          const tw = ctx.measureText(label).width;
          ctx.fillRect(
            det.bbox.x,
            Math.max(0, det.bbox.y - 22),
            tw + 10,
            20,
          );
          ctx.fillStyle = "#e8f0c8";
          ctx.fillText(label, det.bbox.x + 5, Math.max(14, det.bbox.y - 7));
        }
      } catch (err) {
        if (!cancelled) {
          setDrawError(
            err instanceof Error ? err.message : "Canvas draw failed",
          );
        }
      }
    };

    void paint();
    return () => {
      cancelled = true;
    };
  }, [sourcePreviewUrl, results, layers, masks]);

  return (
    <section className="panel canvas-panel">
      <div className="panel__head">
        <h2>Composite</h2>
      </div>
      <div className="canvas-frame">
        <canvas ref={canvasRef} className="result-canvas" />
      </div>
      {drawError ? <p className="error-text">{drawError}</p> : null}
      {!sourcePreviewUrl && !results ? (
        <p className="muted">
          Upload and process an image to see the composite.
        </p>
      ) : null}
    </section>
  );
}

async function drawMaskOverlay(
  ctx: CanvasRenderingContext2D,
  canvas: HTMLCanvasElement,
  mask: MaskInfo,
  _index: number,
) {
  const url = resolveMediaUrl(mask.mask_url);
  if (!url) return;
  try {
    const img = await loadImage(url);
    ctx.save();
    ctx.globalAlpha = 0.55;
    if (mask.bbox) {
      ctx.drawImage(
        img,
        mask.bbox.x,
        mask.bbox.y,
        mask.bbox.width,
        mask.bbox.height,
      );
    } else {
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    }
    ctx.restore();
  } catch {
    // ignore
  }
}

interface LayerListProps {
  layers: LayerInfo[];
  selected: Set<string>;
  onToggle: (id: string) => void;
  onRename: (id: string, name: string) => void;
  onOpacity: (id: string, opacity: number) => void;
}

export function LayerList({
  layers,
  selected,
  onToggle,
  onRename,
  onOpacity,
}: LayerListProps) {
  const sorted = useMemo(
    () => layers.slice().sort((a, b) => a.z_index - b.z_index),
    [layers],
  );

  if (!sorted.length) {
    return (
      <section className="panel">
        <div className="panel__head">
          <h2>Layers</h2>
        </div>
        <p className="muted">No layers yet.</p>
      </section>
    );
  }

  return (
    <section className="panel">
      <div className="panel__head">
        <h2>Layers</h2>
        <span className="muted">{sorted.length}</span>
      </div>
      <ul className="layer-list">
        {sorted.map((layer) => (
          <li key={layer.id} className="layer-row">
            <label className="layer-row__check">
              <input
                type="checkbox"
                checked={selected.has(layer.id)}
                onChange={() => onToggle(layer.id)}
              />
              <span className="sr-only">Show {layer.name}</span>
            </label>
            <div className="layer-row__meta">
              <input
                className="layer-row__name"
                value={layer.name}
                onChange={(e) => onRename(layer.id, e.target.value)}
                aria-label={`Rename layer ${layer.id}`}
              />
              <span className="muted layer-row__kind">{layer.kind}</span>
            </div>
            <input
              className="layer-row__opacity"
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={layer.opacity}
              onChange={(e) => onOpacity(layer.id, Number(e.target.value))}
              aria-label={`Opacity ${layer.name}`}
            />
          </li>
        ))}
      </ul>
    </section>
  );
}

interface MaskListProps {
  masks: MaskInfo[];
  selected: Set<string>;
  onToggle: (id: string) => void;
}

export function MaskList({ masks, selected, onToggle }: MaskListProps) {
  if (!masks.length) {
    return (
      <section className="panel">
        <div className="panel__head">
          <h2>Masks</h2>
        </div>
        <p className="muted">No masks yet.</p>
      </section>
    );
  }

  return (
    <section className="panel">
      <div className="panel__head">
        <h2>Masks</h2>
        <span className="muted">{masks.length}</span>
      </div>
      <ul className="mask-list">
        {masks.map((mask, i) => (
          <li key={mask.id} className="mask-row">
            <label>
              <input
                type="checkbox"
                checked={selected.has(mask.id)}
                onChange={() => onToggle(mask.id)}
              />
              <span
                className="mask-swatch"
                style={{ background: MASK_TINTS[i % MASK_TINTS.length] }}
                aria-hidden
              />
              {mask.label}
              <span className="muted">
                {" "}
                · {Math.round(mask.score * 100)}%
              </span>
            </label>
          </li>
        ))}
      </ul>
    </section>
  );
}
