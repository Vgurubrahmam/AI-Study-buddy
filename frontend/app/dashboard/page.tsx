"use client"

import { useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Zap, LogOut, RefreshCw } from "lucide-react"
import { useAuth } from "@/components/auth-provider"
import { useProtectedRoute } from "@/hooks/use-protected-route"
import { useLearningStats } from "@/hooks/use-learning-stats"
import { useFreeCourses } from "@/hooks/use-free-courses"
import {
  QuestionsAskedCard,
  TopicsLearnedCard,
  AvgAccuracyCard,
  LearningStreakCard,
} from "@/components/dashboard/metric-cards"
import {
  ProgressChart,
  CourseProgressCard,
  TopicsListCard,
} from "@/components/dashboard/progress-charts"

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const { isLoading: isAuthLoading } = useProtectedRoute()
  const { stats, avgAccuracy, isLoaded: isStatsLoaded } = useLearningStats()
  const { enrolledCourses, isLoading: isCoursesLoading, fetchCourses, lastUpdated } = useFreeCourses()

  // Update streak when visiting dashboard
  useEffect(() => {
    if (isStatsLoaded) {
      // Streak is automatically updated through the hook
    }
  }, [isStatsLoaded])

  if (isAuthLoading || !isStatsLoaded) {
    return (
      <main className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-2 text-primary" />
          <p className="text-muted-foreground">Loading your dashboard...</p>
        </div>
      </main>
    )
  }

  // Transform enrolled courses for the progress card
  const courseProgressData = enrolledCourses.map(course => ({
    name: course.title,
    progress: course.progress || 0,
    icon: getCourseIcon(course.category),
  }))

  // Transform daily progress for chart
  const chartData = stats.dailyProgress.length > 0
    ? stats.dailyProgress.map(d => ({ day: d.day, accuracy: d.accuracy }))
    : generateDefaultChartData()

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card p-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Welcome back, {user?.name || "Learner"}!</h1>
            <p className="text-sm text-muted-foreground">
              Track your progress and achievements
              {lastUpdated && (
                <span className="ml-2 text-xs">
                  · Data updated {lastUpdated.toLocaleTimeString()}
                </span>
              )}
            </p>
          </div>
          <div className="flex gap-3">
            <Link href="/chat">
              <Button className="gap-2">
                <Zap className="w-4 h-4" />
                Ask a Question
              </Button>
            </Link>
            <Link href="/courses">
              <Button variant="outline">Browse Courses</Button>
            </Link>
            <Button
              variant="outline"
              size="icon"
              onClick={() => fetchCourses()}
              disabled={isCoursesLoading}
              title="Refresh data"
            >
              <RefreshCw className={`w-4 h-4 ${isCoursesLoading ? "animate-spin" : ""}`} />
            </Button>
            <Button variant="outline" onClick={logout} className="gap-2 bg-transparent">
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="max-w-6xl mx-auto p-6">
        {/* Stats Grid - Component-based Architecture */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <QuestionsAskedCard count={stats.questionsAsked} />
          <TopicsLearnedCard topics={stats.topicsLearned} />
          <AvgAccuracyCard accuracy={avgAccuracy} />
          <LearningStreakCard days={stats.streakDays} />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ProgressChart data={chartData} title="Your Accuracy Trend" />
          <CourseProgressCard
            courses={courseProgressData.slice(0, 5)}
            title={`Course Progress (${enrolledCourses.length} enrolled)`}
          />
        </div>

        {/* Topics Learned */}
        <TopicsListCard topics={stats.topicsLearned} title="Recently Learned Topics" />

        {/* Quick Stats Summary */}
        {stats.questionsAsked > 0 && (
          <div className="mt-6 p-4 bg-accent/50 rounded-lg">
            <p className="text-sm text-center text-muted-foreground">
              🎉 You've asked <strong>{stats.questionsAsked}</strong> questions,
              learned <strong>{stats.topicsLearned.length}</strong> topics,
              and maintained a <strong>{stats.streakDays} day</strong> streak!
              {avgAccuracy >= 80 && " Keep up the excellent work! 🌟"}
            </p>
          </div>
        )}
      </div>
    </main>
  )
}

// Helper function to get emoji icon for course category
function getCourseIcon(category: string): string {
  const icons: Record<string, string> = {
    "Web Development": "🌐",
    "Programming": "💻",
    "Data Science": "📊",
    "Machine Learning": "🤖",
    "Mathematics": "📐",
    "Science": "🔬",
    "Computer Science": "🖥️",
    "Database": "🗄️",
  }
  return icons[category] || "📚"
}

// Generate default chart data for new users
function generateDefaultChartData() {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
  const today = new Date().getDay()
  return days.map((day, idx) => ({
    day,
    accuracy: idx <= today ? 0 : 0,
  }))
}
