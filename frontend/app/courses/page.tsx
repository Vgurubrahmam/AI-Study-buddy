"use client"

import { useState, useMemo } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { BookOpen, Users, Star, ArrowRight, ExternalLink, RefreshCw, Search, Filter } from "lucide-react"
import { useFreeCourses, Course } from "@/hooks/use-free-courses"

export default function CoursesPage() {
  const {
    courses,
    enrolledCourseIds,
    isLoading,
    error,
    lastUpdated,
    fetchCourses,
    enrollCourse,
    unenrollCourse,
    isEnrolled,
  } = useFreeCourses()

  const [levelFilter, setLevelFilter] = useState<"All" | "Beginner" | "Intermediate" | "Advanced">("All")
  const [categoryFilter, setCategoryFilter] = useState<string>("All")
  const [providerFilter, setProviderFilter] = useState<string>("All")
  const [searchQuery, setSearchQuery] = useState("")

  // Get unique categories and providers
  const categories = useMemo(() => ["All", ...new Set(courses.map(c => c.category))], [courses])
  const providers = useMemo(() => ["All", ...new Set(courses.map(c => c.provider))], [courses])

  // Filter courses
  const filteredCourses = useMemo(() => {
    return courses.filter(course => {
      const matchesLevel = levelFilter === "All" || course.level === levelFilter
      const matchesCategory = categoryFilter === "All" || course.category === categoryFilter
      const matchesProvider = providerFilter === "All" || course.provider === providerFilter
      const matchesSearch = searchQuery === "" || 
        course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        course.description.toLowerCase().includes(searchQuery.toLowerCase())
      
      return matchesLevel && matchesCategory && matchesProvider && matchesSearch
    })
  }, [courses, levelFilter, categoryFilter, providerFilter, searchQuery])

  const handleEnroll = (course: Course) => {
    if (isEnrolled(course.id)) {
      unenrollCourse(course.id)
    } else {
      enrollCourse(course.id)
      // Open course URL in new tab
      window.open(course.url, "_blank", "noopener,noreferrer")
    }
  }

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card p-4 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Browse Free Courses</h1>
            <p className="text-sm text-muted-foreground">
              {enrolledCourseIds.length} course{enrolledCourseIds.length !== 1 ? "s" : ""} enrolled
              {lastUpdated && (
                <span className="ml-2">
                  · Updated {lastUpdated.toLocaleTimeString()}
                </span>
              )}
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={() => fetchCourses()}
              disabled={isLoading}
              title="Refresh courses"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
            </Button>
            <Link href="/dashboard">
              <Button variant="outline">Go to Dashboard</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Search and Filters */}
      <div className="border-b border-border bg-card">
        <div className="max-w-6xl mx-auto p-4 space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search courses..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-4">
            {/* Level Filter */}
            <div className="flex gap-2 items-center">
              <Filter className="w-4 h-4 text-muted-foreground" />
              <div className="flex gap-1">
                {(["All", "Beginner", "Intermediate", "Advanced"] as const).map((level) => (
                  <Button
                    key={level}
                    variant={levelFilter === level ? "default" : "outline"}
                    size="sm"
                    onClick={() => setLevelFilter(level)}
                  >
                    {level}
                  </Button>
                ))}
              </div>
            </div>

            {/* Category Filter */}
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-3 py-1 rounded-md border border-input bg-background text-sm"
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>

            {/* Provider Filter */}
            <select
              value={providerFilter}
              onChange={(e) => setProviderFilter(e.target.value)}
              className="px-3 py-1 rounded-md border border-input bg-background text-sm"
            >
              {providers.map(provider => (
                <option key={provider} value={provider}>{provider}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && (
        <div className="max-w-6xl mx-auto p-4">
          <div className="bg-destructive/10 text-destructive p-4 rounded-lg text-center">
            {error}
            <Button variant="link" onClick={() => fetchCourses()} className="ml-2">
              Try again
            </Button>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && courses.length === 0 && (
        <div className="max-w-6xl mx-auto p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Card key={i} className="p-6 animate-pulse">
                <div className="h-12 w-12 bg-muted rounded-lg mb-4" />
                <div className="h-6 bg-muted rounded mb-2 w-3/4" />
                <div className="h-4 bg-muted rounded mb-4 w-full" />
                <div className="h-4 bg-muted rounded w-1/2" />
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Courses Grid */}
      <div className="max-w-6xl mx-auto p-6">
        <div className="mb-4 text-sm text-muted-foreground">
          Showing {filteredCourses.length} of {courses.length} courses
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((course) => (
            <Card key={course.id} className="p-6 hover:shadow-lg transition-shadow flex flex-col">
              <div className="flex items-start justify-between mb-4">
                <span className="text-4xl">{getCourseIcon(course.category)}</span>
                <div className="flex flex-col items-end gap-1">
                  <span className="text-xs font-semibold px-2 py-1 rounded-full bg-accent text-accent-foreground">
                    {course.level}
                  </span>
                  <span className="text-xs text-muted-foreground">{course.provider}</span>
                </div>
              </div>

              <h3 className="text-xl font-bold mb-2">{course.title}</h3>
              <p className="text-muted-foreground text-sm mb-4 flex-1">{course.description}</p>

              <div className="space-y-2 mb-4">
                {course.duration && (
                  <div className="flex items-center gap-2 text-sm">
                    <BookOpen className="w-4 h-4" />
                    <span>{course.duration}</span>
                  </div>
                )}
                {course.students && (
                  <div className="flex items-center gap-2 text-sm">
                    <Users className="w-4 h-4" />
                    <span>{course.students.toLocaleString()} students</span>
                  </div>
                )}
                {course.rating && (
                  <div className="flex items-center gap-2 text-sm">
                    <Star className="w-4 h-4 fill-primary text-primary" />
                    <span>{course.rating}/5.0</span>
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                <Button
                  onClick={() => handleEnroll(course)}
                  variant={isEnrolled(course.id) ? "default" : "outline"}
                  className="flex-1 gap-2"
                >
                  {isEnrolled(course.id) ? "Enrolled ✓" : "Enroll Now"}
                  <ArrowRight className="w-4 h-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => window.open(course.url, "_blank", "noopener,noreferrer")}
                  title="Open course"
                >
                  <ExternalLink className="w-4 h-4" />
                </Button>
              </div>
            </Card>
          ))}
        </div>

        {filteredCourses.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <p className="text-muted-foreground mb-4">No courses found matching your filters.</p>
            <Button variant="outline" onClick={() => {
              setLevelFilter("All")
              setCategoryFilter("All")
              setProviderFilter("All")
              setSearchQuery("")
            }}>
              Clear Filters
            </Button>
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
