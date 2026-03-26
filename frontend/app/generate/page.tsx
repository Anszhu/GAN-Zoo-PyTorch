"use client";

import { useState } from "react";

import { GenerateForm } from "@/components/generate-form";
import { ImageGrid } from "@/components/image-grid";
import { ProtectedRoute } from "@/components/protected-route";
import { GeneratedImage } from "@/types";

export default function GeneratePage() {
  const [images, setImages] = useState<GeneratedImage[]>([]);

  return (
    <ProtectedRoute>
      <div className="space-y-6">
        <GenerateForm onComplete={(newImages) => setImages(newImages)} />
        <ImageGrid images={images} />
      </div>
    </ProtectedRoute>
  );
}

