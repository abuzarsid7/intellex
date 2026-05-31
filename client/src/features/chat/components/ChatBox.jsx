import { useEffect, useMemo, useRef, useState } from 'react'
import { Button, Input, Loader, ChatMessagesSkeleton } from '@/components/ui'
import MessageBox from './MessageBox'
import UploadBox from './UploadBox'

export default function ChatBox({
  messages: sharedMessages,
  files: sharedFiles,
  isLoading: sharedIsLoading,
  sendMessage: sharedSendMessage,
  uploadFiles: sharedUploadFiles,
  error: sharedError,
  currentChat,
  isFetchingChat = false,
}) {
  const messagesEndRef = useRef(null)
  const [inputValue, setInputValue] = useState('')
  const messages = useMemo(
    () => (Array.isArray(sharedMessages) ? sharedMessages : []),
    [sharedMessages]
  )
  const files = useMemo(() => (Array.isArray(sharedFiles) ? sharedFiles : []), [sharedFiles])
  const isLoading = sharedIsLoading ?? false
  const sendMessage = sharedSendMessage ?? (async () => {})
  const uploadFiles = sharedUploadFiles ?? (async () => {})
  const error = sharedError ?? null

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!inputValue.trim() || isLoading) return

    const message = inputValue.trim()
    setInputValue('')
    await sendMessage(message, true)
  }

  const handleUpload = async (formData) => {
    await uploadFiles(formData)
  }

  return (
    <div className="flex h-full flex-col bg-white dark:bg-slate-950">
      {/* Chat Header */}
      <div className="border-b border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-900">
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
          {currentChat?.title || 'Chat with AI'}
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Ask questions and upload documents
        </p>
        {files.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {files.map((file) => (
              <span
                key={file._id}
                className="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 dark:border-blue-900 dark:bg-blue-950 dark:text-blue-200"
              >
                📎 {file.filename}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {isFetchingChat ? (
          <ChatMessagesSkeleton />
        ) : messages.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <div className="mb-4 text-6xl">🚀</div>
              <h3 className="text-xl font-semibold text-slate-900 dark:text-white">Start a conversation</h3>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                Ask me anything or upload a document to get started
              </p>
            </div>
          </div>
        ) : (
          <div>
            {messages.map((msg, index) => (
              <MessageBox key={index} message={msg} isUser={msg.role === 'user'} />
            ))}
            {isLoading && (
              <MessageBox
                message={{ content: '', timestamp: new Date() }}
                isLoading={true}
                isUser={false}
              />
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="border-t border-red-200 bg-red-50 px-4 py-3 dark:border-red-900 dark:bg-red-950">
          <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
        </div>
      )}

      {/* Upload Box */}
      <UploadBox onUpload={handleUpload} isLoading={isLoading} />

      {/* Input Area */}
      <div className="border-t border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <Input
            placeholder="Type your message..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isLoading}
            className="flex-1"
          />
          <Button
            type="submit"
            variant="primary"
            disabled={!inputValue.trim() || isLoading}
            className="flex-shrink-0"
          >
            {isLoading ? <Loader size="sm" /> : 'Send'}
          </Button>
        </form>
      </div>
    </div>
  )
}
