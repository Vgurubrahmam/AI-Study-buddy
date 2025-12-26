import { connectDB } from "@/lib/db"

export async function POST() {
  try {
    const db = await connectDB()

    // Create collections with proper indexes
    const collections = await db.listCollections().toArray()
    const collectionNames = collections.map((c) => c.name)

    // Users collection
    if (!collectionNames.includes("users")) {
      await db.createCollection("users")
    }
    await db.collection("users").createIndex({ email: 1 }, { unique: true })

    // Courses collection
    if (!collectionNames.includes("courses")) {
      await db.createCollection("courses")
    }

    // Chat History collection
    if (!collectionNames.includes("chatHistory")) {
      await db.createCollection("chatHistory")
    }
    await db.collection("chatHistory").createIndex({ userId: 1, createdAt: -1 })

    // User Progress collection
    if (!collectionNames.includes("userProgress")) {
      await db.createCollection("userProgress")
    }

    return Response.json({
      success: true,
      message: "Database initialized successfully",
    })
  } catch (error) {
    console.error("DB init error:", error)
    return Response.json({ success: false, error: String(error) }, { status: 500 })
  }
}
