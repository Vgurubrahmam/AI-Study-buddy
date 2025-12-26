import { connectDB } from "@/lib/db"
import { ObjectId } from "mongodb"

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url)
    const userId = searchParams.get("userId")
    const limit = Number.parseInt(searchParams.get("limit") || "50")

    const db = await connectDB()

    if (userId) {
      const history = await db
        .collection("chatHistory")
        .find({ userId: new ObjectId(userId) })
        .sort({ createdAt: -1 })
        .limit(limit)
        .toArray()

      return Response.json(history)
    }

    // Get all chat history if no userId specified
    const allHistory = await db.collection("chatHistory").find({}).sort({ createdAt: -1 }).limit(limit).toArray()

    return Response.json(allHistory)
  } catch (error: any) {
    return Response.json({ error: error.message }, { status: 500 })
  }
}

// DELETE chat history
export async function DELETE(req: Request) {
  try {
    const { searchParams } = new URL(req.url)
    const chatId = searchParams.get("chatId")

    const db = await connectDB()
    await db.collection("chatHistory").deleteOne({ _id: new ObjectId(chatId as string) })

    return Response.json({ message: "Chat deleted" })
  } catch (error: any) {
    return Response.json({ error: error.message }, { status: 500 })
  }
}
