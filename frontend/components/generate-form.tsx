"use client";

import { FormEvent, useState } from "react";

import { api } from "@/lib/api";
import { GeneratedImage } from "@/types";

export function GenerateForm({ onComplete }: { onComplete: (images: GeneratedImage[]) => void }) {
  const [numImages, setNumImages] = useState(4);
  const [latentDim, setLatentDim] = useState(100);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const { data } = await api.post<{ images: GeneratedImage[] }>("/generate", {
        model_type: "dcgan",
        num_images: numImages,
        latent_dim: latentDim,
        prompt
      });
      onComplete(data.images);
    } catch {
      setError("Generation failed. Make sure the backend is running and you are logged in.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={submit} className="panel space-y-4">
      <div>
        <h2 className="text-2xl font-black">Generate images</h2>
        <p className="mt-1 text-sm text-black/60">DCGAN latent sampling with saved history and downloadable outputs.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="space-y-2">
          <span className="text-sm font-semibold">Images</span>
          <input className="input" type="number" min={1} max={16} value={numImages} onChange={(e) => setNumImages(Number(e.target.value))} />
        </label>
        <label className="space-y-2">
          <span className="text-sm font-semibold">Latent dimension</span>
          <input className="input" type="number" min={16} max={512} value={latentDim} onChange={(e) => setLatentDim(Number(e.target.value))} />
        </label>
      </div>
      <label className="space-y-2">
        <span className="text-sm font-semibold">Prompt or experiment note</span>
        <textarea className="input min-h-28" value={prompt} onChange={(e) => setPrompt(e.target.value)} />
      </label>
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      <button className="button-primary" disabled={loading}>
        {loading ? "Generating..." : "Generate with DCGAN"}
      </button>
    </form>
  );
}

