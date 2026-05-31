export default function Loader({ size = 'md', className = '' }) {
  const sizeCls = size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-8 h-8' : 'w-6 h-6'

  return <span className={`inline-block animate-spin rounded-full border-2 border-slate-200 border-t-sky-500 ${sizeCls} ${className}`} />
}
