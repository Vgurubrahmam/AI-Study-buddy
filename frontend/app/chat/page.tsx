"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Spinner } from "@/components/ui/spinner"
import { Send, MessageCircle, Lightbulb, History, LogOut, Trash2, Plus } from "lucide-react"
import Link from "next/link"
import { useLearningStats } from "@/hooks/use-learning-stats"
import { useChatHistory, ChatMessage } from "@/hooks/use-chat-history"

const SUGGESTED_QUESTIONS = [
  "Explain photosynthesis in simple terms",
  "How do I solve quadratic equations?",
  "What is the difference between REST and GraphQL?",
  "Explain the concept of recursion in programming",
]

// Topic extraction patterns
const TOPIC_PATTERNS = [
  /explain\s+(.+?)(?:\s+in|\s+to|\s*$)/i,
  /what\s+is\s+(.+?)(?:\?|$)/i,
  /how\s+(?:do|does|to)\s+(.+?)(?:\?|$)/i,
  /learn\s+(?:about\s+)?(.+?)(?:\?|$)/i,
  /teach\s+me\s+(.+?)(?:\?|$)/i,
]

function extractTopic(question: string): string | null {
  for (const pattern of TOPIC_PATTERNS) {
    const match = question.match(pattern)
    if (match && match[1]) {
      // Clean up the extracted topic
      let topic = match[1].trim()
      // Capitalize first letter
      topic = topic.charAt(0).toUpperCase() + topic.slice(1)
      // Limit length
      if (topic.length > 30) {
        topic = topic.substring(0, 30) + "..."
      }
      return topic
    }
  }
  return null
}

export default function ChatPage() {
  const router = useRouter()
  const [isAuthed, setIsAuthed] = useState(false)
  const [userId, setUserId] = useState("")
  const [userName, setUserName] = useState("")
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Learning stats hook - persists to localStorage
  const { incrementQuestions, addTopic, recordAnswer } = useLearningStats()
  
  // Chat history hook - persists to localStorage
  const {
    sessions,
    currentSessionId,
    isLoaded: isChatHistoryLoaded,
    createSession,
    addMessage,
    getCurrentSession,
    loadSession,
    deleteSession,
    clearAllSessions,
  } = useChatHistory()

  const getAuthToken = () => localStorage.getItem("auth_token")
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem("auth_token")
      const userStr = localStorage.getItem("user")
      
      if (!token || !userStr) {
        alert("Please log in first.")
        router.push("/login")
        return
      }
      
      try {
        const user = JSON.parse(userStr)
        setUserId(user._id || user.id || "")
        setUserName(user.name || "")
        setIsAuthed(true)
      } catch {
        alert("Please log in first.")
        router.push("/login")
      }
    }
    checkAuth()
  }, [router])

  // Load messages from current session
  useEffect(() => {
    if (isChatHistoryLoaded && currentSessionId) {
      const session = getCurrentSession()
      if (session) {
        setMessages(session.messages)
      }
    }
  }, [isChatHistoryLoaded, currentSessionId, getCurrentSession])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Create new session on first load if none exists
  useEffect(() => {
    if (isChatHistoryLoaded && isAuthed && !currentSessionId && sessions.length === 0) {
      createSession()
    }
  }, [isChatHistoryLoaded, isAuthed, currentSessionId, sessions.length, createSession])

  const handleNewChat = useCallback(() => {
    const newSessionId = createSession()
    setMessages([])
  }, [createSession])

  const handleLoadSession = useCallback((sessionId: string) => {
    loadSession(sessionId)
    const session = sessions.find(s => s.id === sessionId)
    if (session) {
      setMessages(session.messages)
    }
  }, [loadSession, sessions])

  if (!isAuthed) return null

  const handleSendMessage = async (question: string = input) => {
    if (!question.trim()) return

    // Ensure we have a session
    let sessionId = currentSessionId
    if (!sessionId) {
      sessionId = createSession()
    }

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: question,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])
    addMessage(sessionId, { role: "user", content: question })
    setInput("")
    setIsLoading(true)

    // Update learning stats - increment questions asked
    incrementQuestions()

    // Extract and add topic from question
    const topic = extractTopic(question)
    if (topic) {
      addTopic(topic)
    }

    try {
      const token = getAuthToken()
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          ...(token && { "Authorization": `Bearer ${token}` })
        },
        body: JSON.stringify({ message: question, userId }),
      })

      if (!response.ok) throw new Error("Failed to get response")

      const data = await response.json()

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response,
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, assistantMessage])
      addMessage(sessionId, { role: "assistant", content: data.response })

      // Record successful interaction for accuracy tracking
      recordAnswer(true)
    } catch (error) {
      console.error("Chat error:", error)
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error. Please check if the backend server is running.",
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMessage])
      
      // Record failed interaction
      recordAnswer(false)
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("auth_token")
    localStorage.removeItem("user")
    router.push("/")
  }

  return (
    <main className="min-h-screen bg-background flex">
      {/* Sidebar - Chat History */}
      <aside className="w-64 border-r border-border bg-card hidden md:flex flex-col">
        <div className="p-4 border-b border-border">
          <Button onClick={handleNewChat} className="w-full gap-2">
            <Plus className="w-4 h-4" />
            New Chat
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          <div className="space-y-1">
            {sessions.map((session) => (
              <div
                key={session.id}
                onClick={() => handleLoadSession(session.id)}
                className={`w-full text-left p-2 rounded-lg text-sm truncate transition-colors cursor-pointer group ${
                  currentSessionId === session.id
                    ? "bg-accent text-accent-foreground"
                    : "hover:bg-accent/50"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="truncate flex-1">{session.title}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      deleteSession(session.id)
                      if (currentSessionId === session.id) {
                        setMessages([])
                      }
                    }}
                    className="p-1 hover:bg-destructive/20 rounded opacity-0 group-hover:opacity-100"
                  >
                    <Trash2 className="w-3 h-3 text-muted-foreground hover:text-destructive" />
                  </button>
                </div>
                <span className="text-xs text-muted-foreground">
                  {new Date(session.updatedAt).toLocaleDateString()}
                </span>
              </div>
            ))}
          </div>
          {sessions.length === 0 && (
            <p className="text-sm text-muted-foreground text-center py-4">No chat history yet</p>
          )}
        </div>
        {sessions.length > 0 && (
          <div className="p-2 border-t border-border">
            <Button
              variant="ghost"
              size="sm"
              onClick={clearAllSessions}
              className="w-full text-destructive hover:text-destructive"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Clear All History
            </Button>
          </div>
        )}
      </aside>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="border-b border-border bg-card p-4">
          <div className="max-w-4xl mx-auto flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <MessageCircle className="w-6 h-6 text-primary" />
              <div>
                <h1 className="text-2xl font-bold">AI Tutor</h1>
                <p className="text-sm text-muted-foreground">Powered by Qwen AI</p>
              </div>
            </div>
            <div className="flex gap-2">
              <a href="https://ai-study-buddy-chatbot.vercel.app/" target="_blank" rel="noopener noreferrer">
                <Button variant="outline" size="sm" className="gap-2 bg-transparent">
                  API Based
                </Button>
              </a>
              <Link href="/dashboard">
                <Button variant="outline" size="sm" className="gap-2 bg-transparent">
                  Dashboard
                </Button>
              </Link>
              <Link href="/admin">
                <Button variant="outline" size="sm" className="gap-2 bg-transparent">
                  Admin
                </Button>
              </Link>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                className="gap-2 bg-transparent text-destructive"
              >
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 max-w-4xl mx-auto w-full px-4 py-8 flex flex-col">
          {messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center gap-8">
              <div className="text-center">
                <h2 className="text-3xl font-bold mb-2">Welcome to AI Study Buddy</h2>
                <p className="text-muted-foreground mb-8">Ask any question and get instant, detailed answers</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
                {SUGGESTED_QUESTIONS.map((question, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(question)}
                    className="p-4 text-left rounded-lg border border-border hover:bg-accent transition-colors flex items-start gap-3"
                  >
                    <Lightbulb className="w-4 h-4 text-primary mt-1 flex-shrink-0" />
                    <span className="text-sm">{question}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6 flex-1 overflow-y-auto">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`max-w-2xl rounded-lg px-4 py-3 ${
                      msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-card border border-border"
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    <span className="text-xs opacity-50 mt-1 block">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-card border border-border rounded-lg px-4 py-3">
                    <Spinner className="w-4 h-4" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-border bg-card">
          <div className="max-w-4xl mx-auto p-4">
            <div className="flex gap-3">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && !isLoading && handleSendMessage()}
                placeholder="Ask your question..."
                disabled={isLoading}
                className="text-base"
              />
              <Button onClick={() => handleSendMessage()} disabled={isLoading || !input.trim()} className="gap-2">
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
