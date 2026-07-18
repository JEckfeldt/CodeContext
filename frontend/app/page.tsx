export default function Home() {
  return (
    <main className="flex flex-1 flex-col items-center justify-center px-6 py-16">
      <div className="w-full max-w-2xl space-y-4 text-center">
        <p className="text-sm font-medium uppercase tracking-wide text-zinc-500">
          CodeContext
        </p>
        <h1 className="text-3xl font-semibold tracking-tight">
          AI-powered codebase assistant
        </h1>
        <p className="text-base leading-7 text-zinc-600">
          Frontend scaffold is ready. Application features will be added in
          upcoming milestones.
        </p>
      </div>
    </main>
  );
}
