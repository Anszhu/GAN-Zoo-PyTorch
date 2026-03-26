"use client";

import { useState } from "react";

import { ImageGrid } from "@/components/image-grid";
import { ProtectedRoute } from "@/components/protected-route";
import { UploadTransformForm } from "@/components/upload-transform-form";
import { GeneratedImage } from "@/types";

export default function TransformPage() {
  const [images, setImages] = useState<GeneratedImage[]>([]);

  return (
    <ProtectedRoute>
      <div className="space-y-6">
        <UploadTransformForm onComplete={(image) => setImages((current) => [image, ...current])} />
        <ImageGrid images={images} />
      </div>
    </ProtectedRoute>
  );
}

