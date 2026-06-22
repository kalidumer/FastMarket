export default function Header() {
  return (
    <header className="bg-slate-900 text-white shadow-md py-4 px-6 mb-8">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          🤖 AI Support Hub <span className="text-xs bg-cyan-500 py-1 px-2 rounded-full text-white">React 19 + TypeScript</span>
        </h1>
        <p className="text-sm text-slate-400">FastAPI Async Loop Pipeline</p>
      </div>
    </header>
  );
}