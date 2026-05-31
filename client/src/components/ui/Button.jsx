import { forwardRef } from 'react'

const VARIANTS = {
  primary: 'bg-sky-600 text-white hover:bg-sky-500',
  secondary: 'bg-white border text-slate-900 hover:bg-slate-50',
  ghost: 'bg-transparent text-slate-900 hover:bg-slate-100 dark:text-slate-100',
}

const SIZES = {
  sm: 'px-2 py-1 text-sm',
  md: 'px-3 py-2 text-sm',
  lg: 'px-4 py-2 text-base',
}

export const Button = forwardRef(
  (
    { children, variant = 'primary', size = 'md', className = '', as: Component = 'button', ...props },
    ref,
  ) => {
    const variantCls = VARIANTS[variant] ?? VARIANTS.primary
    const sizeCls = SIZES[size] ?? SIZES.md

    return (
      <Component
        ref={ref}
        className={`inline-flex items-center justify-center rounded-md font-medium transition ${variantCls} ${sizeCls} ${className}`}
        {...props}
      >
        {children}
      </Component>
    )
  },
)

export default Button
