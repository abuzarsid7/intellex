import { useState, useRef } from 'react'
import { Button, Loader } from '@/components/ui'

export default function UploadBox({ onUpload, isLoading = false }) {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef(null)

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files || [])
    const pdfFiles = selectedFiles.filter((file) => {
      const fileName = (file.name || '').toLowerCase()
      return file.type === 'application/pdf' || fileName.endsWith('.pdf')
    })

    setFiles((prev) => [...prev, ...pdfFiles])
    e.target.value = ''
  }

  const handleRemoveFile = (index) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    if (files.length === 0) return

    setUploading(true)
    try {
      const formData = new FormData()
      files.forEach((file) => {
        formData.append('file', file)
      })

      await onUpload(formData)
      setFiles([])
    } catch (error) {
      console.error('Upload failed:', error)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="border-t border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900">
      {/* File Input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept="application/pdf,.pdf"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* File List */}
      {files.length > 0 && (
        <div className="mb-3 space-y-2">
          {files.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between rounded-md bg-white p-2 text-sm dark:bg-slate-800"
            >
              <span className="flex-1 truncate text-slate-700 dark:text-slate-300">
                📄 {file.name}
              </span>
              <button
                onClick={() => handleRemoveFile(index)}
                className="ml-2 text-slate-400 hover:text-red-500 dark:text-slate-500"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading || isLoading}
          className="flex-1"
        >
          {files.length > 0 ? `Add more (${files.length})` : 'Add files'}
        </Button>
        {files.length > 0 && (
          <Button
            variant="primary"
            size="sm"
            onClick={handleUpload}
            disabled={uploading || isLoading}
            className="flex-1"
          >
            {uploading ? <Loader size="sm" /> : 'Upload'}
          </Button>
        )}
      </div>
    </div>
  )
}
