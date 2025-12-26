export async function POST() {
  try {
    // Client-side will handle localStorage clearing
    return Response.json({ success: true, message: "Logged out successfully" })
  } catch (error: any) {
    return Response.json({ error: error.message || "Logout failed" }, { status: 500 })
  }
}
