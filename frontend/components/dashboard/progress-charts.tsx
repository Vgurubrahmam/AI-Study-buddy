"use client"

import { Card } from "@/components/ui/card"
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, AreaChart, Area } from "recharts"

interface ProgressChartProps {
  data: { day: string; accuracy: number }[]
  title?: string
  type?: "line" | "area"
}

export function ProgressChart({ data, title = "Accuracy Trend", type = "line" }: ProgressChartProps) {
  // Ensure we have at least some data points
  const chartData = data.length > 0 ? data : [
    { day: "Mon", accuracy: 0 },
    { day: "Tue", accuracy: 0 },
    { day: "Wed", accuracy: 0 },
    { day: "Thu", accuracy: 0 },
    { day: "Fri", accuracy: 0 },
    { day: "Sat", accuracy: 0 },
    { day: "Sun", accuracy: 0 },
  ]

  return (
    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      <ResponsiveContainer width="100%" height={300}>
        {type === "line" ? (
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis 
              dataKey="day" 
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
            />
            <YAxis 
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              domain={[0, 100]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "6px",
              }}
              labelStyle={{ color: "hsl(var(--foreground))" }}
            />
            <Line
              type="monotone"
              dataKey="accuracy"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={{ fill: "hsl(var(--primary))", strokeWidth: 2 }}
              activeDot={{ r: 6, fill: "hsl(var(--primary))" }}
            />
          </LineChart>
        ) : (
          <AreaChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis 
              dataKey="day" 
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
            />
            <YAxis 
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              domain={[0, 100]}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "6px",
              }}
              labelStyle={{ color: "hsl(var(--foreground))" }}
            />
            <Area
              type="monotone"
              dataKey="accuracy"
              stroke="hsl(var(--primary))"
              fill="hsl(var(--primary) / 0.2)"
              strokeWidth={2}
            />
          </AreaChart>
        )}
      </ResponsiveContainer>
    </Card>
  )
}

interface CourseProgressProps {
  courses: { name: string; progress: number; icon?: string }[]
  title?: string
}

export function CourseProgressCard({ courses, title = "Course Progress" }: CourseProgressProps) {
  return (
    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      <div className="space-y-4">
        {courses.length > 0 ? courses.map((course) => (
          <div key={course.name}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                {course.icon && <span>{course.icon}</span>}
                <span className="font-medium text-sm">{course.name}</span>
              </div>
              <span className="text-sm font-semibold">{course.progress}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div
                className="bg-primary h-2 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, Math.max(0, course.progress))}%` }}
              />
            </div>
          </div>
        )) : (
          <p className="text-muted-foreground text-center py-4">No courses enrolled yet</p>
        )}
      </div>
    </Card>
  )
}

interface TopicsListProps {
  topics: string[]
  title?: string
  maxDisplay?: number
}

export function TopicsListCard({ topics, title = "Recently Learned Topics", maxDisplay = 8 }: TopicsListProps) {
  const displayTopics = topics.slice(-maxDisplay).reverse()

  return (
    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">{title}</h2>
      {displayTopics.length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {displayTopics.map((topic, idx) => (
            <div
              key={`${topic}-${idx}`}
              className="p-3 rounded-lg bg-accent text-center font-medium text-sm truncate"
              title={topic}
            >
              {topic}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-muted-foreground text-center py-4">No topics learned yet. Start asking questions!</p>
      )}
    </Card>
  )
}
