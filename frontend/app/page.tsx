"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ArrowRight, Sparkles, BookOpen, TrendingUp, Zap, Users, Lock, LogOut } from "lucide-react"
import { useAuth } from "@/components/auth-provider"

export default function Home() {
  const { isAuthenticated, user, logout, isLoading } = useAuth()

  return (
    <main className="min-h-screen bg-gradient-to-b from-background via-background to-accent/5">
      {/* Navigation */}
      <nav className="flex items-center justify-between px-6 py-4 border-b border-border">
        <div className="flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-primary" />
          <span className="text-xl font-bold">AI Study Buddy</span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/admin">
            <Button variant="ghost">Admin</Button>
          </Link>
          {!isLoading && (
            isAuthenticated ? (
              <>
                <span className="text-sm text-muted-foreground">Welcome, {user?.name}</span>
                <Link href="/dashboard">
                  <Button variant="ghost">Dashboard</Button>
                </Link>
                <Button variant="outline" onClick={logout} className="gap-2">
                  <LogOut className="w-4 h-4" />
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="ghost">Sign In</Button>
                </Link>
                <Link href="/signup">
                  <Button>Sign Up Free</Button>
                </Link>
              </>
            )
          )}
        </div>
      </nav>

      {/* Hero */}
      <section className="px-6 py-24 text-center">
        <h1 className="text-5xl font-bold mb-6 text-balance">Your Personal AI Tutor</h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto text-balance">
          Get instant answers, personalized learning paths, and track your progress with AI-powered tutoring powered by
          Gemini
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/chat">
            <Button size="lg" className="gap-2">
              Start Chatting <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button size="lg" variant="outline">
              View Dashboard
            </Button>
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="px-6 py-20 max-w-6xl mx-auto">
        <h2 className="text-3xl font-bold mb-12 text-center">Why Use AI Study Buddy?</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="p-8">
            <Sparkles className="w-8 h-8 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Instant Answers</h3>
            <p className="text-muted-foreground">
              Get instant, accurate answers to any question across Math, Science, DSA, ML, and more powered by Gemini AI
            </p>
          </Card>
          <Card className="p-8">
            <BookOpen className="w-8 h-8 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Personalized Learning</h3>
            <p className="text-muted-foreground">
              Adaptive recommendations based on your strengths, weaknesses, and learning pace
            </p>
          </Card>
          <Card className="p-8">
            <TrendingUp className="w-8 h-8 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Track Progress</h3>
            <p className="text-muted-foreground">
              Monitor your learning journey with detailed analytics and performance metrics
            </p>
          </Card>
          <Card className="p-8">
            <Zap className="w-8 h-8 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Real-time Features</h3>
            <p className="text-muted-foreground">
              Live stats, instant chat history sync, and real-time admin dashboard updates
            </p>
          </Card>
          <Card className="p-8">
            <Users className="w-8 h-8 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Community Courses</h3>
            <p className="text-muted-foreground">Browse and enroll in structured courses managed by admins</p>
          </Card>
          <Card className="p-8">
            <Lock className="w-8 h-8 text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Secure & Private</h3>
            <p className="text-muted-foreground">Your data is encrypted and stored securely with MongoDB Atlas</p>
          </Card>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="px-6 py-20 bg-card border-t border-border">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Built with Modern Tech</h2>
          <p className="text-muted-foreground mb-8">
            Next.js 16 • React 19 • TypeScript • Tailwind CSS • MongoDB • Gemini AI • shadcn/ui
          </p>
          <p className="text-sm text-muted-foreground max-w-2xl mx-auto">
            Production-ready full-stack application with real-time features, authentication, dual API key support, and
            comprehensive admin dashboard
          </p>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 py-20 bg-primary text-primary-foreground">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Transform Your Learning?</h2>
          <p className="mb-8 text-lg opacity-90">
            Join thousands of students already using AI Study Buddy to ace their exams
          </p>
          <Link href="/chat">
            <Button size="lg" variant="secondary" className="gap-2">
              Get Started Free <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-card px-6 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="w-5 h-5 text-primary" />
                <span className="font-semibold">AI Study Buddy</span>
              </div>
              <p className="text-sm text-muted-foreground">Empowering students with AI-powered personalized tutoring</p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="/chat" className="text-muted-foreground hover:text-foreground">
                    Chat
                  </Link>
                </li>
                <li>
                  <Link href="/dashboard" className="text-muted-foreground hover:text-foreground">
                    Dashboard
                  </Link>
                </li>
                <li>
                  <Link href="/admin" className="text-muted-foreground hover:text-foreground">
                    Admin
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Setup</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="/ENV_SETUP.md" className="text-muted-foreground hover:text-foreground">
                    Environment Variables
                  </a>
                </li>
                <li>
                  <a href="/DEPLOYMENT.md" className="text-muted-foreground hover:text-foreground">
                    Deployment Guide
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-border pt-8 text-center text-sm text-muted-foreground">
            <p>AI Study Buddy Built with Next.js, MongoDB, and Gemini AI</p>
          </div>
        </div>
      </footer>
    </main>
  )
}
