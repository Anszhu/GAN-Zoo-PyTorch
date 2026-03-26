import "./globals.css";

import type { Metadata } from "next";

import { Navbar } from "@/components/navbar";
import { AuthProvider } from "@/lib/auth";

export const metadata: Metadata = {
  title: "GAN Studio",
  description: "Full-stack GAN platform built with Next.js, FastAPI, PyTorch, Celery, and PostgreSQL-ready data models."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <Navbar />
          <main className="mx-auto min-h-screen max-w-7xl px-6 py-10">{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}

