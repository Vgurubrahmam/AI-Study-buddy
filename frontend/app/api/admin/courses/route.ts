import { connectDB } from "@/lib/db"
import { ObjectId } from "mongodb"

// GET all courses
export async function GET() {
  try {
    const db = await connectDB()
    const courses = await db.collection("courses").find({}).toArray()
    return Response.json(courses)
  } catch (error: any) {
    return Response.json({ error: error.message }, { status: 500 })
  }
}

// POST create new course
export async function POST(req: Request) {
  try {
    const { name, description, difficulty, icon, category } = await req.json()

    const db = await connectDB()
    const result = await db.collection("courses").insertOne({
      name,
      description,
      difficulty,
      icon,
      category,
      enrolledCount: 0,
      rating: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
    })

    return Response.json({ id: result.insertedId, message: "Course created" }, { status: 201 })
  } catch (error: any) {
    return Response.json({ error: error.message }, { status: 500 })
  }
}

// PUT update course
export async function PUT(req: Request) {
  try {
    const { id, ...updateData } = await req.json()

    const db = await connectDB()
    await db
      .collection("courses")
      .updateOne({ _id: new ObjectId(id) }, { $set: { ...updateData, updatedAt: new Date() } })

    return Response.json({ message: "Course updated" })
  } catch (error: any) {
    return Response.json({ error: error.message }, { status: 500 })
  }
}

// DELETE course
export async function DELETE(req: Request) {
  try {
    const { searchParams } = new URL(req.url)
    const id = searchParams.get("id")

    const db = await connectDB()
    await db.collection("courses").deleteOne({ _id: new ObjectId(id as string) })

    return Response.json({ message: "Course deleted" })
  } catch (error: any) {
    return Response.json({ error: error.message }, { status: 500 })
  }
}
