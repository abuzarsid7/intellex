export default function Avatar({ src, alt, size = 8, className = '' }) {
  const sizeCls = typeof size === 'number' ? `w-${size} h-${size}` : size

  return (
    <div className={`inline-flex items-center justify-center overflow-hidden rounded-full bg-slate-100 text-slate-700 ${className}`}>
      {src ? (
        <img src={src} alt={alt} className="block h-full w-full object-cover" />
      ) : (
        <span className="text-sm font-medium">{(alt || '?').slice(0, 2).toUpperCase()}</span>
      )}
    </div>
  )
}
