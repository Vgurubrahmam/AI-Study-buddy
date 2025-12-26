"use client"

import { useState, useEffect, useCallback } from "react"

export interface LearningStats {
  questionsAsked: number
  topicsLearned: string[]
  totalCorrect: number
  totalAttempts: number
  streakDays: number
  lastActiveDate: string
  dailyProgress: { day: string; accuracy: number; date: string }[]
}

const STORAGE_KEY_PREFIX = "learning_stats_"

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

const getDefaultStats = (): LearningStats => ({
  questionsAsked: 0,
  topicsLearned: [],
  totalCorrect: 0,
  totalAttempts: 0,
  streakDays: 0,
  lastActiveDate: "",
  dailyProgress: [],
})

export function useLearningStats() {
  const [stats, setStats] = useState<LearningStats>(getDefaultStats())
  const [isLoaded, setIsLoaded] = useState(false)

  // Load stats from localStorage on mount
  useEffect(() => {
    try {
      const storageKey = getStorageKey()
      const stored = localStorage.getItem(storageKey)
      if (stored) {
        const parsedStats = JSON.parse(stored) as LearningStats
        setStats(parsedStats)
      } else {
        setStats(getDefaultStats()) // Reset for new user
      }
      setIsLoaded(true)
    } catch (error) {
      console.error("Error loading learning stats:", error)
      setIsLoaded(true)
    }
  }, [])

  // Save stats to localStorage whenever they change
  useEffect(() => {
    if (isLoaded) {
      try {
        const storageKey = getStorageKey()
        localStorage.setItem(storageKey, JSON.stringify(stats))
      } catch (error) {
        console.error("Error saving learning stats:", error)
      }
    }
  }, [stats, isLoaded])

  // Update streak based on activity
  const updateStreak = useCallback((currentStats: LearningStats): LearningStats => {
    const today = new Date().toISOString().split("T")[0]
    const yesterday = new Date(Date.now() - 86400000).toISOString().split("T")[0]

    if (currentStats.lastActiveDate === today) {
      return currentStats // Already active today
    }

    if (currentStats.lastActiveDate === yesterday) {
      return {
        ...currentStats,
        streakDays: currentStats.streakDays + 1,
        lastActiveDate: today,
      }
    }

    // Streak broken or first activity
    return {
      ...currentStats,
      streakDays: currentStats.lastActiveDate ? 1 : 1,
      lastActiveDate: today,
    }
  }, [])

  // Increment questions asked
  const incrementQuestions = useCallback(() => {
    setStats((prev) => {
      const updated = updateStreak(prev)
      return {
        ...updated,
        questionsAsked: updated.questionsAsked + 1,
      }
    })
  }, [updateStreak])

  // Add a learned topic
  const addTopic = useCallback((topic: string) => {
    setStats((prev) => {
      if (prev.topicsLearned.includes(topic)) return prev
      const updated = updateStreak(prev)
      return {
        ...updated,
        topicsLearned: [...updated.topicsLearned, topic].slice(-20), // Keep last 20 topics
      }
    })
  }, [updateStreak])

  // Record an answer (for accuracy tracking)
  const recordAnswer = useCallback((isCorrect: boolean) => {
    setStats((prev) => {
      const updated = updateStreak(prev)
      const newTotalCorrect = updated.totalCorrect + (isCorrect ? 1 : 0)
      const newTotalAttempts = updated.totalAttempts + 1

      // Update daily progress
      const today = new Date().toISOString().split("T")[0]
      const dayName = new Date().toLocaleDateString("en-US", { weekday: "short" })
      const todayAccuracy = newTotalAttempts > 0 ? Math.round((newTotalCorrect / newTotalAttempts) * 100) : 0

      let dailyProgress = [...updated.dailyProgress]
      const todayIndex = dailyProgress.findIndex((d) => d.date === today)

      if (todayIndex >= 0) {
        dailyProgress[todayIndex] = { day: dayName, accuracy: todayAccuracy, date: today }
      } else {
        dailyProgress.push({ day: dayName, accuracy: todayAccuracy, date: today })
        // Keep last 7 days
        dailyProgress = dailyProgress.slice(-7)
      }

      return {
        ...updated,
        totalCorrect: newTotalCorrect,
        totalAttempts: newTotalAttempts,
        dailyProgress,
      }
    })
  }, [updateStreak])

  // Calculate average accuracy
  const avgAccuracy = stats.totalAttempts > 0 
    ? Math.round((stats.totalCorrect / stats.totalAttempts) * 100) 
    : 0

  // Reset stats
  const resetStats = useCallback(() => {
    setStats(getDefaultStats())
    const storageKey = getStorageKey()
    localStorage.removeItem(storageKey)
  }, [])

  return {
    stats,
    avgAccuracy,
    isLoaded,
    incrementQuestions,
    addTopic,
    recordAnswer,
    resetStats,
  }
}
