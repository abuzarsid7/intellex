import { Avatar, Loader } from '@/components/ui'
import { formatDate } from '@/utils/formatDate'

export default function MessageBox({ message, isLoading = false, isUser = false }) {
  const { content, timestamp, type } = message

  return (
    <div className={`flex gap-3 mb-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div className="mt-1 flex-shrink-0">
        <Avatar alt={isUser ? 'You' : 'Bot'} size="w-8 h-8" />
      </div>

      {/* Message Content */}
      <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-xs lg:max-w-md`}>
        {/* Message Bubble */}
        <div
          className={`rounded-lg px-4 py-2 ${
            isUser
              ? 'bg-sky-600 text-white rounded-br-none'
              : 'bg-slate-100 text-slate-900 rounded-bl-none dark:bg-slate-800 dark:text-slate-100'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center gap-2">
              <Loader size="sm" />
              <span className="text-sm">Thinking...</span>
            </div>
          ) : type === 'code' ? (
            <pre className="whitespace-pre-wrap break-words overflow-x-auto text-xs">
              <code>{content}</code>
            </pre>
          ) : (
            <p className="text-sm whitespace-pre-wrap break-words">{content}</p>
          )}
        </div>

        {/* Timestamp */}
        {timestamp && (
          <span className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            {formatDate(timestamp)}
          </span>
        )}
      </div>
    </div>
  )
}
