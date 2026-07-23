"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { loginUser, registerUser } from "@/lib/api";
import { setAccessToken } from "@/lib/auth-token";

type AuthFormProps = {
  mode: "login" | "register";
};

export function AuthForm({ mode }: AuthFormProps) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (loading) return;

    setError(null);
    setLoading(true);

    try {
      const result =
        mode === "login"
          ? await loginUser(email.trim(), password)
          : await registerUser(email.trim(), password);
      setAccessToken(result.access_token);
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel mx-auto w-full max-w-md p-6 sm:p-8">
      <p className="section-label">{mode === "login" ? "Sign in" : "Create account"}</p>
      <h1 className="section-title mt-1">
        {mode === "login" ? "Log in to CodeContext" : "Register for CodeContext"}
      </h1>
      <p className="mt-2 text-sm text-muted">
        {mode === "login"
          ? "Access your projects and indexed content."
          : "Create an account to own projects and import sources."}
      </p>

      <form onSubmit={(event) => void handleSubmit(event)} className="mt-6 space-y-4">
        <div>
          <label htmlFor="auth-email" className="text-sm font-medium text-foreground">
            Email
          </label>
          <input
            id="auth-email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="mt-2 w-full rounded-md border border-border bg-surface px-3 py-2.5 text-sm"
          />
        </div>
        <div>
          <label htmlFor="auth-password" className="text-sm font-medium text-foreground">
            Password
          </label>
          <input
            id="auth-password"
            type="password"
            autoComplete={mode === "login" ? "current-password" : "new-password"}
            required
            minLength={8}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-2 w-full rounded-md border border-border bg-surface px-3 py-2.5 text-sm"
          />
        </div>
        <Button type="submit" variant="primary" className="h-10 w-full" disabled={loading}>
          {loading ? "Please wait…" : mode === "login" ? "Log in" : "Create account"}
        </Button>
      </form>

      {error ? (
        <p className="status-banner-error mt-4 text-sm" role="alert">
          {error}
        </p>
      ) : null}

      <p className="mt-6 text-sm text-muted">
        {mode === "login" ? (
          <>
            Need an account?{" "}
            <Link href="/register" className="text-primary hover:underline">
              Register
            </Link>
          </>
        ) : (
          <>
            Already have an account?{" "}
            <Link href="/login" className="text-primary hover:underline">
              Log in
            </Link>
          </>
        )}
      </p>
    </div>
  );
}
