interface StatusBannerProps {
  ok: boolean | null;
  message: string;
}

export function StatusBanner({ ok, message }: StatusBannerProps) {
  const tone = ok === null ? "pending" : ok ? "ok" : "err";
  return (
    <div className={`status-banner status-banner--${tone}`} role="status">
      <span className="status-banner__dot" aria-hidden />
      <span>{message}</span>
    </div>
  );
}
