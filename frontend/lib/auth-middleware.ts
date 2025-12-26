import jwt from "jsonwebtoken"

const JWT_SECRET = process.env.JWT_SECRET || "your-secret-key-change-in-production"

export interface AuthUser {
  id: string
  name: string
  email: string
}

export async function verifyToken(token: string): Promise<AuthUser | null> {
  try {
    const decoded = jwt.verify(token, JWT_SECRET) as AuthUser
    return decoded
  } catch (error) {
    return null
  }
}

export function getTokenFromRequest(req: Request): string | null {
  const authHeader = req.headers.get("authorization")
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return null
  }
  return authHeader.substring(7)
}

export async function requireAuth(req: Request): Promise<{ user: AuthUser } | { error: Response }> {
  const token = getTokenFromRequest(req)
  
  if (!token) {
    return { error: Response.json({ error: "Unauthorized" }, { status: 401 }) }
  }

  const user = await verifyToken(token)
  
  if (!user) {
    return { error: Response.json({ error: "Invalid token" }, { status: 401 }) }
  }

  return { user }
}
