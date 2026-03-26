"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/lib/auth";

type Mode = "login" | "register";

export function AuthForm({ mode }: { mode: Mode }) {
  const router = useRouter();
  const auth = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      if (mode === "login") {
        await auth.login({ email, password });
      } else {
        await auth.register({ email, password, full_name: fullName });
      }
      router.push("/dashboard");
    } catch (err) {
      setError("Authentication failed. Check your credentials and try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={submit} className="panel mx-auto max-w-md space-y-4">
      <h1 className="text-3xl font-black">{mode === "login" ? "Welcome back" : "Create your workspace"}</h1>
      {mode === "register" ? (
        <input className="input" placeholder="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
      ) : null}
      <input className="input" placeholder="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <input
        className="input"
        placeholder="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      <button className="button-primary w-full" disabled={submitting}>
        {submitting ? "Please wait..." : mode === "login" ? "Login" : "Register"}
      </button>
    </form>
  );
}

