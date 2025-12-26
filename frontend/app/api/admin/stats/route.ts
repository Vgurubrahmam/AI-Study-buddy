import { connectDB } from "@/lib/db"

export async function GET() {
  try {
    const db = await connectDB()

    const totalUsers = await db.collection("users").countDocuments()
    const totalCourses = await db.collection("courses").countDocuments()
    const totalChats = await db.collection("chatHistory").countDocuments()

    // Get today's chats
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const chatsToday = await db.collection("chatHistory").countDocuments({
      createdAt: { $gte: today },
    })

    // Get most active users
    const topUsers = await db
      .collection("chatHistory")
      .aggregate([{ $group: { _id: "$userId", count: { $sum: 1 } } }, { $sort: { count: -1 } }, { $limit: 5 }])
      .toArray()

    return Response.json({
      stats: {
        totalUsers,
        totalCourses,
        totalChats,
        chatsToday,
        topUsers,
      },
    })
  } catch (error: any) {
    return Response.json({ error: error.message }, { status: 500 })
  }
}
