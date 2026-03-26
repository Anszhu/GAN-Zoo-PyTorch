"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";

import { api } from "@/lib/api";
import { GeneratedImage } from "@/types";

export function UploadTransformForm({ onComplete }: { onComplete: (image: GeneratedImage) => void }) {
  const [file, setFile] = useState<File | null>(null);
  const [direction, setDirection] = useState("summer2winter");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFile(acceptedFiles[0] ?? null);
  }, []);

  const { getRootProps, getInputProps } = useDropzone({ onDrop, accept: { "image/*": [] }, maxFiles: 1 });

  const transform = async () => {
    if (!file) {
      setError("Select an image first.");
      return;
    }
    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("file", file);
    formData.append("direction", direction);
    try {
      const { data } = await api.post<GeneratedImage>("/transform", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      onComplete(data);
    } catch {
      setError("Transformation failed. Verify your model checkpoint configuration.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel space-y-4">
      <div>
        <h2 className="text-2xl font-black">Upload and transform</h2>
        <p className="mt-1 text-sm text-black/60">CycleGAN image-to-image translation for domain adaptation workflows.</p>
      </div>
      <div
        {...getRootProps()}
        className="rounded-3xl border border-dashed border-black/20 bg-black/5 p-10 text-center transition hover:bg-black/10"
      >
        <input {...getInputProps()} />
        <p className="font-semibold">{file ? file.name : "Drag and drop an image here"}</p>
        <p className="mt-2 text-sm text-black/60">or click to browse a local file</p>
      </div>
      <label className="space-y-2">
        <span className="text-sm font-semibold">Direction</span>
        <select className="input" value={direction} onChange={(e) => setDirection(e.target.value)}>
          <option value="summer2winter">summer2winter</option>
          <option value="winter2summer">winter2summer</option>
          <option value="horse2zebra">horse2zebra</option>
          <option value="zebra2horse">zebra2horse</option>
        </select>
      </label>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      <button className="button-primary" onClick={transform} disabled={loading}>
        {loading ? "Transforming..." : "Apply CycleGAN"}
      </button>
    </div>
  );
}

