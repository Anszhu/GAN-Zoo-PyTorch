import Image from "next/image";

import { resolveAssetUrl } from "@/lib/assets";
import { GeneratedImage } from "@/types";

export function ImageGrid({ images }: { images: GeneratedImage[] }) {
  if (!images.length) {
    return <div className="panel text-sm text-black/60">No images yet. Generate or transform one to populate history.</div>;
  }

  return (
    <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
      {images.map((image) => (
        <article key={image.id} className="panel overflow-hidden p-0">
          <div className="relative aspect-square bg-black/5">
            <Image src={resolveAssetUrl(image.public_url)} alt={image.model_type} fill className="object-cover" unoptimized />
          </div>
          <div className="space-y-2 p-5">
            <div className="flex items-center justify-between">
              <span className="rounded-full bg-sand px-3 py-1 text-xs font-semibold uppercase tracking-wide">
                {image.model_type}
              </span>
              <a className="text-sm font-semibold text-ember" href={resolveAssetUrl(image.public_url)} download>
                Download
              </a>
            </div>
            <p className="text-sm text-black/70">{image.prompt || image.original_filename || "Untitled image"}</p>
            <p className="text-xs text-black/50">{new Date(image.created_at).toLocaleString()}</p>
          </div>
        </article>
      ))}
    </div>
  );
}
