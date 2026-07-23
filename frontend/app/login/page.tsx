import { AuthForm } from "@/components/auth/auth-form";

export default function LoginPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl items-center px-4 py-12 sm:px-6">
      <AuthForm mode="login" />
    </main>
  );
}
