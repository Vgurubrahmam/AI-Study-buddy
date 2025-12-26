import { auth } from "@/lib/auth"

export async function GET() {
  const session = await auth()
  if (!session?.user) {
    return Response.json({ error: "Not authenticated" }, { status: 401 })
  }
  return Response.json({ session, userId: session.user.id })
}
