import api from '@/services/axios'
import { API_ENDPOINTS } from '@/services/apiEndpoints'

/**
 * Create a new chat
 * @param {string} title - Chat title
 * @returns {Promise} Response from the API
 */
export const createChat = async (title = 'New Chat') => {
  const response = await api.post(API_ENDPOINTS.CHAT.CREATE || `${API_ENDPOINTS.CHAT.GET}`, {
    title,
  })
  return response.data
}

/**
 * Get all user chats
 * @param {number} page - Page number
 * @param {number} limit - Items per page
 * @returns {Promise} Response from the API
 */
export const getUserChats = async (page = 1, limit = 50) => {
  const response = await api.get(API_ENDPOINTS.CHAT.LIST || API_ENDPOINTS.CHAT.GET, {
    params: { page, limit },
  })
  return response.data
}

/**
 * Get chat details by ID
 * @param {string} chatId - Chat ID
 * @returns {Promise} Response from the API
 */
export const getChatById = async (chatId) => {
  const response = await api.get(`${API_ENDPOINTS.CHAT.GET}/${chatId}`)
  return response.data
}

/**
 * Get messages for a chat
 * @param {string} chatId - Chat ID
 * @param {number} page - Page number
 * @param {number} limit - Items per page
 * @returns {Promise} Response from the API
 */
export const getChatMessages = async (chatId, page = 1, limit = 100) => {
  const response = await api.get(`${API_ENDPOINTS.CHAT.GET}/${chatId}/messages`, {
    params: { page, limit },
  })
  return response.data
}

/**
 * Get uploaded files for a chat
 * @param {string} chatId - Chat ID
 * @returns {Promise} Response from the API
 */
export const getChatFiles = async (chatId) => {
  const response = await api.get(`${API_ENDPOINTS.CHAT.GET}/${chatId}/files`)
  return response.data
}

/**
 * Send a message to chat and get AI response - MAIN ENDPOINT
 * @param {string} chatId - Chat ID
 * @param {string} message - Message content
 * @param {boolean} useRAG - Use document context (optional)
 * @returns {Promise} Response from the API
 */
export const sendChatMessage = async (chatId, message, useRAG = false) => {
  const response = await api.post(API_ENDPOINTS.CHAT.MESSAGE || `${API_ENDPOINTS.CHAT.GET}/message`, {
    chatId,
    message,
    useRAG,
  })
  return response.data
}

/**
 * Update chat title
 * @param {string} chatId - Chat ID
 * @param {string} title - New title
 * @returns {Promise} Response from the API
 */
export const updateChatTitle = async (chatId, title) => {
  const response = await api.put(`${API_ENDPOINTS.CHAT.GET}/${chatId}/title`, {
    title,
  })
  return response.data
}

/**
 * Delete a chat
 * @param {string} chatId - Chat ID
 * @returns {Promise} Response from the API
 */
export const deleteChat = async (chatId) => {
  const response = await api.delete(`${API_ENDPOINTS.CHAT.DELETE || API_ENDPOINTS.CHAT.GET}/${chatId}`)
  return response.data
}

/**
 * Clear chat messages
 * @param {string} chatId - Chat ID
 * @returns {Promise} Response from the API
 */
export const clearChatMessages = async (chatId) => {
  const response = await api.delete(`${API_ENDPOINTS.CHAT.GET}/${chatId}/messages`)
  return response.data
}

/**
 * Upload files for chat context
 * @param {string} chatId - Chat ID
 * @param {FormData} formData - FormData containing files to upload
 * @returns {Promise} Response from the API
 */
export const uploadChatFiles = async (chatId, formData) => {
  const files = Array.from(formData?.getAll?.('file') || formData?.getAll?.('files') || [])

  if (files.length === 0) {
    throw new Error('No files provided for upload')
  }

  const uploads = []

  for (const file of files) {
    const singleFileFormData = new FormData()
    singleFileFormData.append('file', file)
    singleFileFormData.append('chatId', chatId)
    singleFileFormData.append('chat_id', chatId)

    const response = await api.post(API_ENDPOINTS.UPLOAD.FILE, singleFileFormData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    uploads.push(response.data)
  }

  return {
    success: true,
    chatId,
    uploads,
  }
}

/**
 * Clear chat history
 * @param {string} chatId - The chat session ID
 * @returns {Promise} Response from the API
 */
export const clearChatHistory = async (chatId) => {
  const response = await api.delete(`${API_ENDPOINTS.CHAT.DELETE || API_ENDPOINTS.CHAT.GET}/${chatId}`)
  return response.data
}
