import { forwardRef } from 'react'

export const IconButton = forwardRef(({ children, className = '', ...props }, ref) => {
  return (
    <button
      ref={ref}
      type="button"
      className={`inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200 ${className}`}
      {...props}
    >
      {children}
    </button>
  )
})

export default IconButton
