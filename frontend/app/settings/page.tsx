"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function SettingsPage() {
  const router = useRouter()
  const [isAuthed, setIsAuthed] = useState(false)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch("/api/auth/session")
        if (!res.ok) {
          router.push("/login")
        } else {
          setIsAuthed(true)
        }
      } catch {
        router.push("/login")
      }
    }
    checkAuth()
  }, [router])

  if (!isAuthed) return null

  return (
    <main className="min-h-screen bg-background">
      <header className="border-b border-border bg-card p-4">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <Link href="/dashboard">
            <Button variant="ghost" size="sm" className="gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">Settings</h1>
            <p className="text-sm text-muted-foreground">Manage your preferences</p>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto p-6">
        <div className="space-y-6">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">API Configuration</h2>
            <div className="space-y-4">
              <div className="p-4 bg-accent rounded-lg">
                <p className="text-sm font-semibold mb-2">Primary Gemini API Key</p>
                <p className="text-xs text-muted-foreground">
                  {process.env.GEMINI_API_KEY_1 ? "Configured" : "Not configured"}
                </p>
              </div>
              <div className="p-4 bg-accent rounded-lg">
                <p className="text-sm font-semibold mb-2">Secondary Gemini API Key (Fallback)</p>
                <p className="text-xs text-muted-foreground">
                  {process.env.GEMINI_API_KEY_2 ? "Configured" : "Not configured (optional)"}
                </p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Database</h2>
            <div className="p-4 bg-accent rounded-lg">
              <p className="text-sm font-semibold mb-2">MongoDB Connection</p>
              <p className="text-xs text-muted-foreground">
                {process.env.MONGODB_URI ? "Connected" : "Not configured"}
              </p>
            </div>
          </Card>

          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">Help</h2>
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                For setup instructions and troubleshooting, see the ENV_SETUP.md file in the project root.
              </p>
              <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
                <li>Set up MongoDB at mongodb.com/cloud/atlas</li>
                <li>Get Gemini API keys from aistudio.google.com/app/apikey</li>
                <li>Add environment variables in Vercel project settings</li>
              </ul>
            </div>
          </Card>
        </div>
      </div>
    </main>
  )
}
