"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/lib/auth";

const links = [
  { href: "/", label: "Home" },
  { href: "/generate", label: "Generate" },
  { href: "/transform", label: "Transform" },
  { href: "/dashboard", label: "Dashboard" }
];

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-50 border-b border-black/10 bg-cream/80 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-xl font-black tracking-tight">
          GAN Studio
        </Link>
        <nav className="hidden gap-2 md:flex">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                pathname === link.href ? "bg-ink text-cream" : "hover:bg-black/5"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          {user ? (
            <>
              <span className="hidden text-sm text-black/60 md:block">{user.full_name}</span>
              <button
                className="button-secondary"
                onClick={() => {
                  logout();
                  router.push("/login");
                }}
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="button-secondary">
                Login
              </Link>
              <Link href="/register" className="button-primary">
                Sign up
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

