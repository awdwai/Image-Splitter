import { useRef, useState, type DragEvent, type ChangeEvent } from "react";

interface ImageUploadProps {
  disabled?: boolean;
  onFile: (file: File) => void;
}

const ACCEPT = "image/png,image/jpeg,image/webp,image/gif";

export function ImageUpload({ disabled, onFile }: ImageUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const takeFile = (file: File | undefined) => {
    if (!file || disabled) return;
    if (!file.type.startsWith("image/")) return;
    onFile(file);
  };

  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragging(false);
    takeFile(e.dataTransfer.files[0]);
  };

  const onChange = (e: ChangeEvent<HTMLInputElement>) => {
    takeFile(e.target.files?.[0]);
    e.target.value = "";
  };

  return (
    <div
      className={`upload-zone${dragging ? " upload-zone--active" : ""}${disabled ? " upload-zone--disabled" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={onDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      role="button"
      tabIndex={disabled ? -1 : 0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          if (!disabled) inputRef.current?.click();
        }
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        hidden
        disabled={disabled}
        onChange={onChange}
      />
      <p className="upload-zone__title">Drop a still frame</p>
      <p className="upload-zone__hint">PNG, JPEG, or WebP — click to browse</p>
    </div>
  );
}
