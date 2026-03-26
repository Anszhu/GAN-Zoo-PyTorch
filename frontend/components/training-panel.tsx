"use client";

import { FormEvent, useMemo, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { api } from "@/lib/api";
import { TrainingJob } from "@/types";

export function TrainingPanel({ jobs, onRefresh }: { jobs: TrainingJob[]; onRefresh: () => Promise<void> }) {
  const [epochs, setEpochs] = useState(5);
  const [batchSize, setBatchSize] = useState(64);
  const [latentDim, setLatentDim] = useState(100);
  const [datasetName, setDatasetName] = useState("mnist");
  const [loading, setLoading] = useState(false);

  const latestMetrics = useMemo(() => {
    const completed = jobs.find((job) => job.metrics_json);
    if (!completed?.metrics_json) return [];
    try {
      return JSON.parse(completed.metrics_json);
    } catch {
      return [];
    }
  }, [jobs]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    try {
      await api.post("/train", {
        model_type: "dcgan",
        dataset_name: datasetName,
        epochs,
        batch_size: batchSize,
        latent_dim: latentDim
      });
      await onRefresh();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <form onSubmit={submit} className="panel space-y-4">
        <div>
          <h2 className="text-2xl font-black">Train a model</h2>
          <p className="mt-1 text-sm text-black/60">Background Celery jobs feed a training dashboard for experiment tracking.</p>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          <label className="space-y-2">
            <span className="text-sm font-semibold">Dataset</span>
            <select className="input" value={datasetName} onChange={(e) => setDatasetName(e.target.value)}>
              <option value="mnist">MNIST</option>
              <option value="celeba">CelebA</option>
              <option value="custom">Custom</option>
            </select>
          </label>
          <label className="space-y-2">
            <span className="text-sm font-semibold">Epochs</span>
            <input className="input" type="number" value={epochs} onChange={(e) => setEpochs(Number(e.target.value))} />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-semibold">Batch size</span>
            <input className="input" type="number" value={batchSize} onChange={(e) => setBatchSize(Number(e.target.value))} />
          </label>
          <label className="space-y-2">
            <span className="text-sm font-semibold">Latent dimension</span>
            <input className="input" type="number" value={latentDim} onChange={(e) => setLatentDim(Number(e.target.value))} />
          </label>
        </div>
        <button className="button-primary" disabled={loading}>
          {loading ? "Queueing..." : "Queue training job"}
        </button>
      </form>
      <div className="panel">
        <h3 className="text-xl font-black">Latest loss curves</h3>
        <div className="mt-4 h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={latestMetrics}>
              <XAxis dataKey="epoch" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="g_loss" stroke="#d55d3f" strokeWidth={3} />
              <Line type="monotone" dataKey="d_loss" stroke="#6d8b74" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

