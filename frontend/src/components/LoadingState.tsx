export function LoadingState({ text = "加载中..." }: { text?: string }) {
  return (
    <div className="flex items-center justify-center py-20">
      <div className="text-center text-slate-400">
        <div className="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-2 border-cyan-500 border-t-transparent" />
        <p className="text-sm">{text}</p>
      </div>
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="rounded-lg border border-red-500/30 bg-red-500/5 p-6 text-center">
      <p className="text-sm text-red-400">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="mt-3 text-sm text-cyan-400 hover:underline">
          重试
        </button>
      )}
    </div>
  );
}

export function EmptyState({ text }: { text: string }) {
  return (
    <div className="rounded-lg border border-dashed border-slate-700 p-10 text-center">
      <p className="text-sm text-slate-500">{text}</p>
    </div>
  );
}
