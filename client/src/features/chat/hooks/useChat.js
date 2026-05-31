import { useCallback, useEffect, useState } from 'react'
import { useAuth } from '@/context/AuthContext'
import {
  clearChatMessages,
  createChat,
  deleteChat,
  getChatFiles,
  getChatById,
  getChatMessages,
  getUserChats,
  sendChatMessage,
  updateChatTitle,
  uploadChatFiles,
} from '../services/chatApi'

export function useChat() {
  const { isAuthenticated } = useAuth()
  const [chats, setChats] = useState([])
  const [currentChat, setCurrentChat] = useState(null)
  const [messages, setMessages] = useState([])
  const [files, setFiles] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [isFetchingChats, setIsFetchingChats] = useState(false)
  const [isFetchingChat, setIsFetchingChat] = useState(false)
  const [error, setError] = useState(null)

  const loadChats = useCallback(async () => {
    if (!isAuthenticated) return

    setIsFetchingChats(true)
    try {
      const data = await getUserChats()
      setChats(data.chats || [])
      setError(null)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch chats')
    } finally {
      setIsFetchingChats(false)
    }
  }, [isAuthenticated])

  const fetchChats = loadChats

  const fetchChat = useCallback(
    async (chatId) => {
      if (!isAuthenticated) return

      setIsFetchingChat(true)
      try {
        const chatData = await getChatById(chatId)
        const messagesData = await getChatMessages(chatId)
        const filesData = await getChatFiles(chatId)

        setCurrentChat(chatData.chat)
        setMessages(messagesData.messages || [])
        setFiles(filesData.files || [])
        setError(null)
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to fetch chat')
      } finally {
        setIsFetchingChat(false)
      }
    },
    [isAuthenticated]
  )

  const createNewChat = useCallback(
    async (title = 'New Chat') => {
      if (!isAuthenticated) return null

      setIsLoading(true)
      try {
        const data = await createChat(title)
        const newChat = data.chat

        setChats((previousChats) => [newChat, ...previousChats])
        setCurrentChat(newChat)
        setMessages([])
        setFiles([])
        setError(null)

        return newChat
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to create chat')
        return null
      } finally {
        setIsLoading(false)
      }
    },
    [isAuthenticated]
  )

  const ensureCurrentChat = useCallback(
    async (fallbackTitle = 'New Chat') => {
      if (currentChat) {
        return currentChat
      }

      return createNewChat(fallbackTitle)
    },
    [currentChat, createNewChat]
  )

  const sendMessage = useCallback(
    async (message, useRAG = true) => {
      if (!isAuthenticated) return null

      setIsLoading(true)
      setError(null)

      try {
        const chat = await ensureCurrentChat(message.slice(0, 40) || 'New Chat')

        if (!chat?._id) {
          throw new Error('Unable to create or select a chat')
        }

        const data = await sendChatMessage(chat._id, message, useRAG)
        const messageCountIncrement = data.userMessage && data.assistantMessage ? 2 : 0
        const activeChat = {
          ...chat,
          messageCount: Number(chat.messageCount || 0) + messageCountIncrement,
        }

        setMessages((previousMessages) => [
          ...previousMessages,
          data.userMessage,
          data.assistantMessage,
        ])

        setChats((previousChats) =>
          previousChats.map((existingChat) => {
            if (existingChat._id !== chat._id) {
              return existingChat
            }

            const currentCount = Number(existingChat.messageCount || 0)
            return {
              ...existingChat,
              messageCount: currentCount + messageCountIncrement,
            }
          })
        )

        setCurrentChat((previousChat) => {
          if (!previousChat || previousChat._id !== chat._id) {
            return previousChat || activeChat
          }

          const currentCount = Number(previousChat.messageCount || 0)
          return {
            ...previousChat,
            messageCount: currentCount + messageCountIncrement,
          }
        })

        return data
      } catch (err) {
        const messageText = err.response?.data?.message || err.message || 'Failed to send message'
        setError(messageText)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [ensureCurrentChat, isAuthenticated]
  )

  const uploadFiles = useCallback(
    async (formData) => {
      if (!isAuthenticated) return null

      setIsLoading(true)
      setError(null)

      try {
        const chat = await ensureCurrentChat('Uploaded Documents')

        if (!chat?._id) {
          throw new Error('Unable to create or select a chat')
        }

        const data = await uploadChatFiles(chat._id, formData)
        const filesData = await getChatFiles(chat._id)
        const uploadedFiles = data.uploads?.map((upload) => upload.storedFile).filter(Boolean) ?? []
        setFiles(filesData.files || uploadedFiles)
        return data
      } catch (err) {
        const messageText = err.response?.data?.message || err.message || 'Failed to upload files'
        setError(messageText)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [ensureCurrentChat, isAuthenticated]
  )

  const changeChatTitle = useCallback(
    async (chatId, newTitle) => {
      if (!isAuthenticated) return null

      try {
        const data = await updateChatTitle(chatId, newTitle)
        const updatedChat = data.chat

        setChats((previousChats) =>
          previousChats.map((chat) => (chat._id === chatId ? updatedChat : chat))
        )

        setCurrentChat((previousChat) =>
          previousChat?._id === chatId ? updatedChat : previousChat
        )

        setError(null)
        return updatedChat
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to update chat title')
        return null
      }
    },
    [isAuthenticated]
  )

  const deleteCurrentChat = useCallback(
    async (chatId) => {
      if (!isAuthenticated) return null

      try {
        await deleteChat(chatId)
        setChats((previousChats) => previousChats.filter((chat) => chat._id !== chatId))

        if (currentChat?._id === chatId) {
          setCurrentChat(null)
          setMessages([])
          setFiles([])
        }

        setError(null)
        return true
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to delete chat')
        return null
      }
    },
    [currentChat, isAuthenticated]
  )

  const clearMessages = useCallback(
    async (chatId) => {
      if (!isAuthenticated) return null

      try {
        await clearChatMessages(chatId)
        if (currentChat?._id === chatId) {
          setMessages([])
          setFiles([])
        }
        setError(null)
        return true
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to clear messages')
        return null
      }
    },
    [currentChat, isAuthenticated]
  )

  useEffect(() => {
    /* eslint-disable react-hooks/set-state-in-effect */
    if (isAuthenticated) {
      void loadChats()
    } else {
      setChats([])
      setCurrentChat(null)
      setMessages([])
      setFiles([])
    }
    /* eslint-enable react-hooks/set-state-in-effect */
  }, [isAuthenticated, loadChats])

  return {
    chats,
    currentChat,
    messages,
    files,
    isLoading,
    isFetchingChats,
    isFetchingChat,
    error,
    fetchChats,
    fetchChat,
    createNewChat,
    sendMessage,
    uploadFiles,
    changeChatTitle,
    deleteCurrentChat,
    clearMessages,
    setError,
  }
}
