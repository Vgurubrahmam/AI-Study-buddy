import { sendMessageWithFallback } from "@/lib/gemini-client"
import { connectDB } from "@/lib/db"
import { ObjectId } from "mongodb"

export async function POST(req: Request) {
  try {
    const { message, userId } = await req.json()

    if (!message) {
      return Response.json({ error: "Message is required" }, { status: 400 })
    }

    const responseText = await sendMessageWithFallback(message)

    // Save to MongoDB if user is authenticated
    if (userId) {
      try {
        const db = await connectDB()
        await db.collection("chatHistory").insertOne({
          userId: new ObjectId(userId),
          userMessage: message,
          assistantResponse: responseText,
          createdAt: new Date(),
          tokens: {
            input: Math.ceil(message.length / 4),
            output: Math.ceil(responseText.length / 4),
          },
        })
      } catch (dbError) {
        console.warn("[v0] Failed to save chat history:", dbError)
        // Don't fail the request if DB save fails
      }
    }

    return Response.json({ response: responseText })
  } catch (error: any) {
    console.error("[v0] Chat API error:", error)
    return Response.json({ error: error.message || "Failed to process chat request" }, { status: 500 })
  }
}
