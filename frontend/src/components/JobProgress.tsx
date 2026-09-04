import type { Job } from "../types/api";

interface JobProgressProps {
  job: Job | null;
  polling: boolean;
}

export function JobProgress({ job, polling }: JobProgressProps) {
  if (!job) return null;

  const pct = Math.max(0, Math.min(100, Math.round(job.progress * 100)));
  const label =
    job.status === "queued"
      ? "Queued"
      : job.status === "running"
        ? "Processing"
        : job.status === "completed"
          ? "Completed"
          : "Failed";

  return (
    <section className="panel job-progress" aria-live="polite">
      <div className="panel__head">
        <h2>Job</h2>
        <span className={`pill pill--${job.status}`}>
          {label}
          {polling ? " · live" : ""}
        </span>
      </div>
      <p className="muted mono">
        {job.type} · {job.id}
      </p>
      <div
        className="progress-track"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={pct}
        role="progressbar"
      >
        <div className="progress-fill" style={{ width: `${pct}%` }} />
      </div>
      <p className="progress-label">{pct}%</p>
      {job.message ? <p className="muted">{job.message}</p> : null}
      {job.error ? <p className="error-text">{job.error}</p> : null}
    </section>
  );
}
