"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ArrowLeft, Trash2, MessageSquare, ExternalLink } from "lucide-react"
import Link from "next/link"
import { useChatHistory, ChatSession } from "@/hooks/use-chat-history"

export default function HistoryPage() {
  const router = useRouter()
  const [isAuthed, setIsAuthed] = useState(false)
  
  const {
    sessions,
    isLoaded,
    deleteSession,
    clearAllSessions,
    loadSession,
  } = useChatHistory()

  useEffect(() => {
    const token = localStorage.getItem("auth_token")
    const userStr = localStorage.getItem("user")
    
    if (!token || !userStr) {
      alert("Please log in first.")
      router.push("/login")
      return
    }
    setIsAuthed(true)
  }, [router])

  const handleOpenSession = (sessionId: string) => {
    loadSession(sessionId)
    router.push("/chat")
  }

  if (!isAuthed || !isLoaded) {
    return (
      <main className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-background">
      <header className="border-b border-border bg-card p-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/chat">
              <Button variant="ghost" size="sm" className="gap-2">
                <ArrowLeft className="w-4 h-4" />
                Back to Chat
              </Button>
            </Link>
            <div>
              <h1 className="text-2xl font-bold">Chat History</h1>
              <p className="text-sm text-muted-foreground">
                {sessions.length} conversation{sessions.length !== 1 ? "s" : ""} saved locally
              </p>
            </div>
          </div>
          {sessions.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={clearAllSessions}
              className="text-destructive"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Clear All
            </Button>
          )}
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-6">
        {sessions.length > 0 ? (
          <div className="space-y-3">
            {sessions.map((session) => (
              <Card key={session.id} className="p-4 hover:shadow-md transition-shadow">
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold truncate">{session.title}</h3>
                      <p className="text-xs text-muted-foreground">
                        {new Date(session.createdAt).toLocaleDateString()} · {session.messages.length} messages
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleOpenSession(session.id)}
                        className="gap-2 h-auto p-2"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteSession(session.id)}
                        className="gap-2 text-destructive h-auto p-2"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  {/* Preview of messages */}
                  {session.messages.length > 0 && (
                    <div className="bg-accent/50 p-3 rounded text-sm space-y-2">
                      {session.messages.slice(0, 2).map((msg, idx) => (
                        <div key={idx} className="flex gap-2">
                          <span className={`text-xs font-semibold ${msg.role === "user" ? "text-primary" : "text-muted-foreground"}`}>
                            {msg.role === "user" ? "You:" : "AI:"}
                          </span>
                          <p className="text-muted-foreground line-clamp-1 flex-1">{msg.content}</p>
                        </div>
                      ))}
                      {session.messages.length > 2 && (
                        <p className="text-xs text-muted-foreground">+{session.messages.length - 2} more messages</p>
                      )}
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="p-8 text-center">
            <MessageSquare className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No chat history yet. Start asking questions in the chat!</p>
            <p className="text-xs text-muted-foreground mt-2">Your conversations are saved locally in your browser.</p>
            <Link href="/chat" className="mt-4 inline-block">
              <Button>Go to Chat</Button>
            </Link>
          </Card>
        )}
      </div>
    </main>
  )
}
