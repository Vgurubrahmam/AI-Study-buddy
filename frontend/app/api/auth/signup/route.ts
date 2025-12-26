import { connectDB } from "@/lib/db"
import bcrypt from "bcryptjs"

export async function POST(req: Request) {
  try {
    const { name, email, password } = await req.json()

    if (!name || !email || !password) {
      return Response.json({ error: "Missing required fields" }, { status: 400 })
    }

    const db = await connectDB()

    // Check if user exists
    const existingUser = await db.collection("users").findOne({ email })
    if (existingUser) {
      return Response.json({ error: "User already exists" }, { status: 400 })
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10)

    // Create user with default role
    const result = await db.collection("users").insertOne({
      name,
      email,
      password: hashedPassword,
      role: "user", // Default role
      provider: "credentials",
      createdAt: new Date(),
      updatedAt: new Date(),
    })

    // Initialize user stats
    await db.collection("userStats").insertOne({
      userId: result.insertedId,
      questionsAsked: 0,
      topicsLearned: [],
      totalAccuracy: 0,
      accuracyCount: 0,
      lastActiveDate: new Date(),
      streak: 0,
      coursesEnrolled: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    })

    const user = {
      id: result.insertedId.toString(),
      name,
      email,
    }

    return Response.json({ success: true, user, message: "Account created successfully" })
  } catch (error: any) {
    console.error("Signup error:", error)
    return Response.json({ error: error.message || "Signup failed" }, { status: 500 })
  }
}
