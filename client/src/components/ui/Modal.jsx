import { useEffect } from 'react'
import { createPortal } from 'react-dom'

function ModalContent({ children, onClose }) {
  useEffect(() => {
    function onKey(e) {
      if (e.key === 'Escape') onClose()
    }

    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />

      <div className="relative z-10 w-full max-w-lg rounded-lg bg-white p-6 shadow-lg dark:bg-slate-900">
        {children}
      </div>
    </div>
  )
}

export default function Modal({ isOpen, onClose, children }) {
  if (typeof document === 'undefined') return null

  return isOpen ? createPortal(<ModalContent onClose={onClose}>{children}</ModalContent>, document.body) : null
}
