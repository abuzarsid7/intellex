import { forwardRef } from 'react'

export const Input = forwardRef(({ label, error, className = '', ...props }, ref) => {
  return (
    <div className={className}>
      {label && <label className="mb-1 block text-sm font-medium text-[rgb(var(--app-foreground))]">{label}</label>}
      <input
        ref={ref}
        className={`block w-full rounded-md border bg-[rgb(var(--app-surface))] px-3 py-2 text-[rgb(var(--app-foreground))] shadow-sm placeholder:text-[rgb(var(--app-muted))] focus:outline-none focus:ring-2 focus:ring-sky-400 ${error ? 'border-red-500' : 'border-[rgb(var(--app-border))]'}`}
        {...props}
      />
      {error && <p className="mt-1 text-sm text-red-600 dark:text-red-300">{error}</p>}
    </div>
  )
})

export default Input
