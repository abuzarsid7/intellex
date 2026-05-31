export default function Skeleton({ className = '' }) {
  return (
    <div
      className={`animate-pulse rounded-lg bg-gradient-to-r from-slate-700 via-slate-600 to-slate-700 ${className}`}
    />
  )
}

export function ChatListSkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0 flex-1 space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/2" />
            </div>
            <Skeleton className="h-6 w-12 rounded-full" />
          </div>
        </div>
      ))}
    </div>
  )
}

export function ChatMessagesSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className={i % 2 === 0 ? 'flex justify-end' : 'flex justify-start'}>
          <div className="max-w-xs space-y-2">
            <Skeleton className={`h-12 ${i % 2 === 0 ? 'rounded-3xl rounded-tr-lg' : 'rounded-3xl rounded-tl-lg'}`} />
            <Skeleton className="h-3 w-24 text-xs" />
          </div>
        </div>
      ))}
    </div>
  )
}
