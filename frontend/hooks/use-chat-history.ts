"use client"

import { useState, useEffect, useCallback } from "react"

export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: string
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: string
  updatedAt: string
}

const STORAGE_KEY_PREFIX = "chat_history_"
const MAX_SESSIONS = 50

function getUserId(): string | null {
  try {
    const userStr = localStorage.getItem("user")
    if (userStr) {
      const user = JSON.parse(userStr)
      return user._id || user.id || null
    }
  } catch {
    return null
  }
  return null
}

function getStorageKey(): string {
  const userId = getUserId()
  return userId ? `${STORAGE_KEY_PREFIX}${userId}` : `${STORAGE_KEY_PREFIX}guest`
}

export function useChatHistory() {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [isLoaded, setIsLoaded] = useState(false)

  // Load chat history from localStorage on mount
  useEffect(() => {
    try {
      const storageKey = getStorageKey()
      const stored = localStorage.getItem(storageKey)
      if (stored) {
        const parsedSessions = JSON.parse(stored) as ChatSession[]
        setSessions(parsedSessions)
      } else {
        setSessions([]) // Reset for new user
      }
      setIsLoaded(true)
    } catch (error) {
      console.error("Error loading chat history:", error)
      setIsLoaded(true)
    }
  }, [])

  // Save sessions to localStorage whenever they change (only sessions with messages)
  useEffect(() => {
    if (isLoaded) {
      try {
        const storageKey = getStorageKey()
        // Only save sessions that have at least one message
        const sessionsWithMessages = sessions.filter(s => s.messages.length > 0)
        localStorage.setItem(storageKey, JSON.stringify(sessionsWithMessages))
      } catch (error) {
        console.error("Error saving chat history:", error)
      }
    }
  }, [sessions, isLoaded])

  // Create a new chat session
  const createSession = useCallback((): string => {
    const newSession: ChatSession = {
      id: Date.now().toString(),
      title: "New Chat",
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }

    setSessions((prev) => {
      const updated = [newSession, ...prev].slice(0, MAX_SESSIONS)
      return updated
    })

    setCurrentSessionId(newSession.id)
    return newSession.id
  }, [])

  // Add a message to a session
  const addMessage = useCallback((sessionId: string, message: Omit<ChatMessage, "id" | "timestamp">) => {
    const newMessage: ChatMessage = {
      ...message,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
    }

    setSessions((prev) => {
      return prev.map((session) => {
        if (session.id === sessionId) {
          const updatedMessages = [...session.messages, newMessage]
          // Update title from first user message
          const title = session.messages.length === 0 && message.role === "user"
            ? message.content.slice(0, 50) + (message.content.length > 50 ? "..." : "")
            : session.title
          
          return {
            ...session,
            title,
            messages: updatedMessages,
            updatedAt: new Date().toISOString(),
          }
        }
        return session
      })
    })

    return newMessage
  }, [])

  // Get current session
  const getCurrentSession = useCallback((): ChatSession | null => {
    if (!currentSessionId) return null
    return sessions.find((s) => s.id === currentSessionId) || null
  }, [currentSessionId, sessions])

  // Get session by ID
  const getSession = useCallback((sessionId: string): ChatSession | null => {
    return sessions.find((s) => s.id === sessionId) || null
  }, [sessions])

  // Delete a session
  const deleteSession = useCallback((sessionId: string) => {
    setSessions((prev) => prev.filter((s) => s.id !== sessionId))
    if (currentSessionId === sessionId) {
      setCurrentSessionId(null)
    }
  }, [currentSessionId])

  // Clear all sessions
  const clearAllSessions = useCallback(() => {
    setSessions([])
    setCurrentSessionId(null)
    const storageKey = getStorageKey()
    localStorage.removeItem(storageKey)
  }, [])

  // Load a session
  const loadSession = useCallback((sessionId: string) => {
    setCurrentSessionId(sessionId)
  }, [])

  // Only return sessions that have messages (for display in history)
  const sessionsWithMessages = sessions.filter(s => s.messages.length > 0)

  return {
    sessions: sessionsWithMessages,
    currentSessionId,
    isLoaded,
    createSession,
    addMessage,
    getCurrentSession,
    getSession,
    deleteSession,
    clearAllSessions,
    loadSession,
    setCurrentSessionId,
  }
}
