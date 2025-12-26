import { connectDB } from "@/lib/db"
import bcrypt from "bcrypt"
import jwt from "jsonwebtoken"

const JWT_SECRET = process.env.JWT_SECRET || "your-secret-key-change-in-production"

export async function POST(req: Request) {
  try {
    const { email, password } = await req.json()

    if (!email || !password) {
      return Response.json({ error: "Email and password required" }, { status: 400 })
    }

    const db = await connectDB()
    const user = await db.collection("users").findOne({ email })

    if (!user) {
      return Response.json({ error: "Invalid email or password" }, { status: 401 })
    }

    // Verify password
    const isValidPassword = await bcrypt.compare(password, user.password)
    if (!isValidPassword) {
      return Response.json({ error: "Invalid email or password" }, { status: 401 })
    }

    const userData = {
      id: user._id.toString(),
      name: user.name,
      email: user.email,
    }

    // Generate JWT token
    const token = jwt.sign(userData, JWT_SECRET, { expiresIn: "30d" })

    return Response.json({ 
      success: true, 
      user: userData,
      token 
    })
  } catch (error: any) {
    console.error("Login error:", error)
    return Response.json({ error: error.message || "Login failed" }, { status: 500 })
  }
}
