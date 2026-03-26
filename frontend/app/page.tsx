import Link from "next/link";

export default function HomePage() {
  return (
    <div className="space-y-8">
      <section className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="panel space-y-6">
          <span className="inline-flex rounded-full bg-sand px-4 py-2 text-xs font-bold uppercase tracking-[0.25em] text-ink">
            Full-stack GAN Platform
          </span>
          <div className="space-y-4">
            <h1 className="max-w-3xl text-5xl font-black leading-tight md:text-6xl">
              Generate, transform, train, and manage GAN image workflows from one production-ready app.
            </h1>
            <p className="max-w-2xl text-lg text-black/65">
              DCGAN image generation, CycleGAN translation, JWT auth, async training jobs, history tracking, and Docker deployment are all included.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/generate" className="button-primary">
              Start generating
            </Link>
            <Link href="/dashboard" className="button-secondary">
              Open dashboard
            </Link>
          </div>
        </div>
        <div className="panel grid gap-4 md:grid-cols-2">
          {[
            ["DCGAN inference", "Sample latent vectors and persist outputs with downloadable artifacts."],
            ["CycleGAN transforms", "Upload source images and convert between domain styles."],
            ["Async training", "Queue PyTorch training through Celery and inspect loss curves."],
            ["History + auth", "Track user outputs and secure access with JWT-protected APIs."]
          ].map(([title, body]) => (
            <article key={title} className="rounded-3xl bg-black/[0.03] p-5">
              <h2 className="text-lg font-black">{title}</h2>
              <p className="mt-2 text-sm text-black/60">{body}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

