import { auth } from "@/lib/auth"
import { connectDB } from "@/lib/db"
import { ObjectId } from "mongodb"

export async function GET(req: Request) {
  try {
    const session = await auth()
    if (!session?.user) {
      return Response.json({ error: "Not authenticated" }, { status: 401 })
    }

    const { searchParams } = new URL(req.url)
    const userId = searchParams.get("userId") || session.user.id
    const limit = Number.parseInt(searchParams.get("limit") || "100")

    const db = await connectDB()
    const history = await db
      .collection("chatHistory")
      .find({ userId: new ObjectId(userId) })
      .sort({ createdAt: -1 })
      .limit(limit)
      .toArray()

    return Response.json(history)
  } catch (error: any) {
    console.error("Error fetching chat history:", error)
    return Response.json({ error: error.message }, { status: 500 })
  }
}

export async function DELETE(req: Request) {
  try {
    const session = await auth()
    if (!session?.user) {
      return Response.json({ error: "Not authenticated" }, { status: 401 })
    }

    const { searchParams } = new URL(req.url)
    const chatId = searchParams.get("id")

    const db = await connectDB()

    // Verify user owns this chat
    const chat = await db.collection("chatHistory").findOne({ _id: new ObjectId(chatId as string) })

    if (!chat || chat.userId.toString() !== session.user.id) {
      return Response.json({ error: "Unauthorized" }, { status: 403 })
    }

    await db.collection("chatHistory").deleteOne({ _id: new ObjectId(chatId as string) })

    return Response.json({ message: "Chat deleted" })
  } catch (error: any) {
    console.error("Error deleting chat:", error)
    return Response.json({ error: error.message }, { status: 500 })
  }
}
