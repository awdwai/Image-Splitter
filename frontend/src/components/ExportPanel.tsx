import type { ExportFormat, ExportResponse, ModelInfo } from "../types/api";

interface ExportPanelProps {
  disabled: boolean;
  format: ExportFormat;
  onFormatChange: (format: ExportFormat) => void;
  onExport: () => void;
  busy: boolean;
  record: ExportResponse | null;
}

export function ExportPanel({
  disabled,
  format,
  onFormatChange,
  onExport,
  busy,
  record,
}: ExportPanelProps) {
  return (
    <section className="panel">
      <div className="panel__head">
        <h2>Export</h2>
      </div>
      <div className="export-row">
        <label className="field">
          <span>Format</span>
          <select
            value={format}
            disabled={disabled || busy}
            onChange={(e) => onFormatChange(e.target.value as ExportFormat)}
          >
            <option value="png_layers">PNG layers</option>
            <option value="psd">PSD</option>
            <option value="json">JSON</option>
          </select>
        </label>
        <button
          type="button"
          className="btn btn--primary"
          disabled={disabled || busy}
          onClick={onExport}
        >
          {busy ? "Requesting…" : "Request export"}
        </button>
      </div>
      {record ? (
        <div className="export-result">
          <p className="mono muted">
            {record.id} · {record.status} · {record.format}
          </p>
          {record.error ? <p className="error-text">{record.error}</p> : null}
          {record.download_url ? (
            <a
              className="btn btn--ghost"
              href={record.download_url}
              target="_blank"
              rel="noreferrer"
            >
              Download
            </a>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}

interface ModelPickerProps {
  models: ModelInfo[];
  selectedId: string | null;
  onChange: (id: string | null) => void;
  disabled?: boolean;
}

export function ModelPicker({
  models,
  selectedId,
  onChange,
  disabled,
}: ModelPickerProps) {
  if (!models.length) {
    return (
      <p className="muted">
        No models listed by the API yet — process will use server defaults.
      </p>
    );
  }

  return (
    <fieldset className="model-picker" disabled={disabled}>
      <legend>Pipeline model</legend>
      <div className="model-picker__grid">
        <label className={`model-chip${!selectedId ? " is-on" : ""}`}>
          <input
            type="radio"
            name="model"
            checked={!selectedId}
            onChange={() => onChange(null)}
          />
          <span>
            <strong>Server default</strong>
            <em>use backend config</em>
          </span>
        </label>
        {models.map((m) => {
          const checked = selectedId === m.id;
          return (
            <label
              key={m.id}
              className={`model-chip${checked ? " is-on" : ""}`}
            >
              <input
                type="radio"
                name="model"
                checked={checked}
                disabled={!m.available}
                onChange={() => onChange(m.id)}
              />
              <span>
                <strong>
                  {m.name}
                  {m.is_stub ? " (stub)" : ""}
                </strong>
                <em>
                  {m.kind} — {m.description}
                </em>
              </span>
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}
