"use client";

import { useEffect, useState } from "react";

import { ImageGrid } from "@/components/image-grid";
import { ProtectedRoute } from "@/components/protected-route";
import { TrainingPanel } from "@/components/training-panel";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { GeneratedImage, TrainingJob } from "@/types";

export default function DashboardPage() {
  const { user } = useAuth();
  const [images, setImages] = useState<GeneratedImage[]>([]);
  const [jobs, setJobs] = useState<TrainingJob[]>([]);

  const loadData = async () => {
    const [imagesResponse, jobsResponse] = await Promise.all([api.get<GeneratedImage[]>("/images"), api.get<TrainingJob[]>("/training-jobs")]);
    setImages(imagesResponse.data);
    setJobs(jobsResponse.data);
  };

  useEffect(() => {
    void loadData();
  }, []);

  useEffect(() => {
    const interval = window.setInterval(() => {
      void loadData();
    }, 5000);
    return () => window.clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!user) return;
    const socketBase = (process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000").replace(/\/$/, "");
    const ws = new WebSocket(`${socketBase}/ws/${user.id}`);
    ws.onmessage = () => {
      void loadData();
    };
    return () => ws.close();
  }, [user]);

  return (
    <ProtectedRoute>
      <div className="space-y-6">
        <section className="grid gap-4 md:grid-cols-3">
          <div className="panel">
            <p className="text-sm uppercase tracking-[0.2em] text-black/45">Generated images</p>
            <p className="mt-3 text-4xl font-black">{images.length}</p>
          </div>
          <div className="panel">
            <p className="text-sm uppercase tracking-[0.2em] text-black/45">Training jobs</p>
            <p className="mt-3 text-4xl font-black">{jobs.length}</p>
          </div>
          <div className="panel">
            <p className="text-sm uppercase tracking-[0.2em] text-black/45">Running jobs</p>
            <p className="mt-3 text-4xl font-black">{jobs.filter((job) => job.status === "running").length}</p>
          </div>
        </section>
        <TrainingPanel jobs={jobs} onRefresh={loadData} />
        <ImageGrid images={images} />
      </div>
    </ProtectedRoute>
  );
}
