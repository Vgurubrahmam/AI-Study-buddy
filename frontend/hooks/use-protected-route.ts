"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth-provider"

export function useProtectedRoute() {
  const router = useRouter()
  const { isAuthenticated, isLoading } = useAuth()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      alert("Please log in first.")
      router.push("/login")
    }
  }, [isAuthenticated, isLoading, router])

  return { isAuthenticated, isLoading }
}
