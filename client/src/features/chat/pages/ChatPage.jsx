import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { MainLayout } from '@/components/layout'
import ChatBox from '../components/ChatBox'
import { useChat } from '../hooks/useChat'

export default function ChatPage() {
  const navigate = useNavigate()
  const chat = useChat()

  useEffect(() => {
    document.title = 'Chat - Intellex'
  }, [])

  const handleNewChat = async () => {
    await chat.createNewChat()
  }

  const handleSelectChat = async (chatId) => {
    await chat.fetchChat(chatId)
  }

  const handleDeleteCurrentChat = async () => {
    if (!chat.currentChat?._id) return

    const shouldDelete = window.confirm('Delete this chat permanently?')
    if (!shouldDelete) return

    await chat.deleteCurrentChat(chat.currentChat._id)
  }

  return (
    <MainLayout
      sidebarProps={{
        chats: chat.chats,
        currentChat: chat.currentChat,
        onNewChat: handleNewChat,
        onSelectChat: handleSelectChat,
        onEditChat: chat.changeChatTitle,
        onDeleteChat: chat.deleteCurrentChat,
        isLoading: chat.isLoading,
        isFetchingChats: chat.isFetchingChats,
      }}
    >
      <div className="flex h-full flex-col">
        <div className="flex items-center justify-between border-b border-white/10 px-4 py-3 text-sm text-slate-300 lg:hidden">
          <span className="truncate pr-3">{chat.currentChat?.title || 'Current chat'}</span>
          <div className="flex items-center gap-2">
            {chat.currentChat?._id && (
              <button
                type="button"
                onClick={handleDeleteCurrentChat}
                className="rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs text-red-200"
              >
                Delete
              </button>
            )}
            <button
              type="button"
              onClick={() => navigate('/')}
              className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs"
            >
              Home
            </button>
          </div>
        </div>
        <ChatBox
          messages={chat.messages}
          files={chat.files}
          isLoading={chat.isLoading}
          sendMessage={chat.sendMessage}
          uploadFiles={chat.uploadFiles}
          error={chat.error}
          currentChat={chat.currentChat}
          isFetchingChat={chat.isFetchingChat}
        />
      </div>
    </MainLayout>
  )
}
