"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Plus, Trash2, Edit2, MessageSquare, BookOpen, RefreshCw } from "lucide-react"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const getAuthToken = () => {
  if (typeof window !== "undefined") {
    return localStorage.getItem("auth_token")
  }
  return null
}

interface Course {
  _id: string
  name: string
  description: string
  difficulty: string
  icon: string
  category: string
  enrolledCount: number
  rating: number
}

interface ChatHistory {
  _id: string
  userId: string
  userMessage: string
  assistantResponse: string
  createdAt: string
}

interface Stats {
  totalUsers: number
  totalCourses: number
  totalChats: number
  chatsToday: number
}

export default function AdminPage() {
  const [courses, setCourses] = useState<Course[]>([])
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const [autoRefresh, setAutoRefresh] = useState(true)
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)

  // Course form
  const [newCourse, setNewCourse] = useState({
    name: "",
    description: "",
    difficulty: "Beginner",
    icon: "📚",
    category: "General",
  })

  useEffect(() => {
    fetchData()
    const interval = setInterval(() => {
      if (autoRefresh) {
        fetchData()
      }
    }, 30000)
    return () => clearInterval(interval)
  }, [autoRefresh])

  const fetchData = async () => {
    try {
      setIsLoading(true)
      await Promise.all([fetchCourses(), fetchChatHistory(), fetchStats()])
      setLastRefresh(new Date())
    } catch (error) {
      console.error("Error fetching data:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const fetchCourses = async () => {
    try {
      const token = getAuthToken()
      const res = await fetch(`${API_URL}/api/admin/courses`, {
        headers: {
          ...(token && { "Authorization": `Bearer ${token}` })
        }
      })
      if (res.ok) {
        const data = await res.json()
        setCourses(data)
      }
    } catch (error) {
      console.error("Error fetching courses:", error)
    }
  }

  const fetchChatHistory = async () => {
    try {
      const token = getAuthToken()
      const res = await fetch(`${API_URL}/api/admin/chat-history`, {
        headers: {
          ...(token && { "Authorization": `Bearer ${token}` })
        }
      })
      if (res.ok) {
        const data = await res.json()
        setChatHistory(data)
      }
    } catch (error) {
      console.error("Error fetching chat history:", error)
    }
  }

  const fetchStats = async () => {
    try {
      const token = getAuthToken()
      const res = await fetch(`${API_URL}/api/admin/stats`, {
        headers: {
          ...(token && { "Authorization": `Bearer ${token}` })
        }
      })
      if (res.ok) {
        const data = await res.json()
        setStats(data.stats)
      }
    } catch (error) {
      console.error("Error fetching stats:", error)
    }
  }

  const handleCreateCourse = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const token = getAuthToken()
      const res = await fetch(`${API_URL}/api/admin/courses`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          ...(token && { "Authorization": `Bearer ${token}` })
        },
        body: JSON.stringify(newCourse),
      })

      if (res.ok) {
        setNewCourse({
          name: "",
          description: "",
          difficulty: "Beginner",
          icon: "📚",
          category: "General",
        })
        fetchCourses()
        fetchStats()
      }
    } catch (error) {
      console.error("Error creating course:", error)
    }
  }

  const handleDeleteCourse = async (id: string) => {
    try {
      const token = getAuthToken()
      await fetch(`${API_URL}/api/admin/courses?id=${id}`, { 
        method: "DELETE",
        headers: {
          ...(token && { "Authorization": `Bearer ${token}` })
        }
      })
      fetchCourses()
      fetchStats()
    } catch (error) {
      console.error("Error deleting course:", error)
    }
  }

  const handleDeleteChat = async (id: string) => {
    try {
      const token = getAuthToken()
      await fetch(`${API_URL}/api/admin/chat-history?chatId=${id}`, { 
        method: "DELETE",
        headers: {
          ...(token && { "Authorization": `Bearer ${token}` })
        }
      })
      fetchChatHistory()
      fetchStats()
    } catch (error) {
      console.error("Error deleting chat:", error)
    }
  }

  return (
    <main className="min-h-screen bg-background">
      <header className="border-b border-border bg-card p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Admin Dashboard</h1>
            <p className="text-sm text-muted-foreground">Manage courses and view real-time analytics</p>
          </div>
          <Button variant="outline" onClick={() => fetchData()} className="gap-2 bg-transparent" disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6">
        {/* Stats Grid */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <Card className="p-4">
              <p className="text-sm text-muted-foreground">Total Users</p>
              <p className="text-3xl font-bold">{stats.totalUsers}</p>
            </Card>
            <Card className="p-4">
              <p className="text-sm text-muted-foreground">Courses</p>
              <p className="text-3xl font-bold">{stats.totalCourses}</p>
            </Card>
            <Card className="p-4">
              <p className="text-sm text-muted-foreground">Total Chats</p>
              <p className="text-3xl font-bold">{stats.totalChats}</p>
            </Card>
            <Card className="p-4">
              <p className="text-sm text-muted-foreground">Today's Chats</p>
              <p className="text-3xl font-bold">{stats.chatsToday}</p>
            </Card>
          </div>
        )}

        {lastRefresh && (
          <p className="text-xs text-muted-foreground mb-4">Last updated: {lastRefresh.toLocaleTimeString()}</p>
        )}

        <Tabs defaultValue="courses" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="courses" className="gap-2">
              <BookOpen className="w-4 h-4" />
              Courses
            </TabsTrigger>
            <TabsTrigger value="chat" className="gap-2">
              <MessageSquare className="w-4 h-4" />
              Chat History
            </TabsTrigger>
          </TabsList>

          <TabsContent value="courses" className="space-y-6">
            {/* Create Course Form */}
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4">Create New Course</h2>
              <form onSubmit={handleCreateCourse} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    placeholder="Course name"
                    value={newCourse.name}
                    onChange={(e) => setNewCourse({ ...newCourse, name: e.target.value })}
                    required
                  />
                  <select
                    className="px-3 py-2 rounded-md border border-input bg-background"
                    value={newCourse.difficulty}
                    onChange={(e) => setNewCourse({ ...newCourse, difficulty: e.target.value })}
                  >
                    <option>Beginner</option>
                    <option>Intermediate</option>
                    <option>Advanced</option>
                  </select>
                </div>
                <textarea
                  placeholder="Course description"
                  value={newCourse.description}
                  onChange={(e) => setNewCourse({ ...newCourse, description: e.target.value })}
                  className="w-full px-3 py-2 rounded-md border border-input bg-background min-h-24"
                  required
                />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    placeholder="Icon (emoji)"
                    value={newCourse.icon}
                    onChange={(e) => setNewCourse({ ...newCourse, icon: e.target.value })}
                    maxLength={2}
                  />
                  <Input
                    placeholder="Category"
                    value={newCourse.category}
                    onChange={(e) => setNewCourse({ ...newCourse, category: e.target.value })}
                  />
                </div>
                <Button type="submit" className="w-full gap-2">
                  <Plus className="w-4 h-4" />
                  Create Course
                </Button>
              </form>
            </Card>

            {/* Courses List */}
            <div className="space-y-3">
              <h2 className="text-xl font-semibold">All Courses ({courses.length})</h2>
              {courses.length > 0 ? (
                courses.map((course) => (
                  <Card key={course._id} className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-2xl">{course.icon}</span>
                          <div>
                            <h3 className="font-semibold">{course.name}</h3>
                            <p className="text-sm text-muted-foreground">{course.description}</p>
                          </div>
                        </div>
                        <div className="flex gap-4 text-sm">
                          <span className="text-muted-foreground">
                            <strong>{course.difficulty}</strong>
                          </span>
                          <span className="text-muted-foreground">Enrolled: {course.enrolledCount}</span>
                          <span className="text-muted-foreground">Rating: {course.rating.toFixed(1)}</span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" className="gap-2 bg-transparent">
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDeleteCourse(course._id)}
                          className="gap-2"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))
              ) : (
                <p className="text-muted-foreground">No courses yet. Create your first course!</p>
              )}
            </div>
          </TabsContent>

          <TabsContent value="chat" className="space-y-4">
            <h2 className="text-xl font-semibold">User Chat History ({chatHistory.length})</h2>
            {chatHistory.length > 0 ? (
              <div className="space-y-3">
                {chatHistory.map((chat) => (
                  <Card key={chat._id} className="p-4">
                    <div className="space-y-2">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="text-sm text-muted-foreground mb-2">
                            User ID: {chat.userId.substring(0, 12)}... | {new Date(chat.createdAt).toLocaleString()}
                          </p>
                          <div className="grid md:grid-cols-2 gap-4">
                            <div>
                              <p className="text-xs font-semibold text-primary mb-1">User Question:</p>
                              <p className="text-sm bg-accent p-2 rounded">{chat.userMessage}</p>
                            </div>
                            <div>
                              <p className="text-xs font-semibold text-secondary mb-1">AI Response:</p>
                              <p className="text-sm bg-accent p-2 rounded line-clamp-3">{chat.assistantResponse}</p>
                            </div>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteChat(chat._id)}
                          className="gap-2 text-destructive"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">No chat history yet</p>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </main>
  )
}
