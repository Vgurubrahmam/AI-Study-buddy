"use client"

import { Card } from "@/components/ui/card"
import { BookOpen, TrendingUp, Zap, Flame, LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

interface MetricCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: LucideIcon
  trend?: {
    value: number
    isPositive: boolean
  }
  className?: string
}

export function MetricCard({ title, value, subtitle, icon: Icon, trend, className }: MetricCardProps) {
  return (
    <Card className={cn("p-6 transition-all hover:shadow-md", className)}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="text-3xl font-bold tracking-tight">{value}</p>
          {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
          {trend && (
            <div className={cn(
              "flex items-center gap-1 text-xs font-medium",
              trend.isPositive ? "text-green-500" : "text-red-500"
            )}>
              <TrendingUp className={cn("w-3 h-3", !trend.isPositive && "rotate-180")} />
              <span>{trend.isPositive ? "+" : ""}{trend.value}%</span>
            </div>
          )}
        </div>
        <div className="p-2 bg-primary/10 rounded-lg">
          <Icon className="w-6 h-6 text-primary" />
        </div>
      </div>
    </Card>
  )
}

// Specialized metric components for common use cases

interface QuestionsAskedCardProps {
  count: number
  className?: string
}

export function QuestionsAskedCard({ count, className }: QuestionsAskedCardProps) {
  return (
    <MetricCard
      title="Questions Asked"
      value={count}
      subtitle="Total queries to AI"
      icon={BookOpen}
      className={className}
    />
  )
}

interface TopicsLearnedCardProps {
  topics: string[]
  className?: string
}

export function TopicsLearnedCard({ topics, className }: TopicsLearnedCardProps) {
  return (
    <MetricCard
      title="Topics Learned"
      value={topics.length}
      subtitle={topics.length > 0 ? `Latest: ${topics[topics.length - 1]}` : "Start learning!"}
      icon={TrendingUp}
      className={className}
    />
  )
}

interface AvgAccuracyCardProps {
  accuracy: number
  trend?: number
  className?: string
}

export function AvgAccuracyCard({ accuracy, trend, className }: AvgAccuracyCardProps) {
  return (
    <MetricCard
      title="Avg Accuracy"
      value={`${accuracy}%`}
      subtitle="Response quality score"
      icon={Zap}
      trend={trend !== undefined ? { value: Math.abs(trend), isPositive: trend >= 0 } : undefined}
      className={className}
    />
  )
}

interface LearningStreakCardProps {
  days: number
  className?: string
}

export function LearningStreakCard({ days, className }: LearningStreakCardProps) {
  return (
    <MetricCard
      title="Learning Streak"
      value={`${days}d`}
      subtitle={days > 0 ? "Keep it going! 🔥" : "Start your streak today!"}
      icon={Flame}
      className={className}
    />
  )
}
