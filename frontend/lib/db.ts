import clientPromise from "./mongodb"

export async function connectDB() {
  const client = await clientPromise
  const db = client.db("ai_study_buddy")
  return db
}

export async function getCollections() {
  const db = await connectDB()
  return {
    users: db.collection("users"),
    courses: db.collection("courses"),
    chatHistory: db.collection("chatHistory"),
    userProgress: db.collection("userProgress"),
  }
}
