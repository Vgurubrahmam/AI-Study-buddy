import type { NextAuthConfig } from "next-auth"
import Google from "next-auth/providers/google"
import Credentials from "next-auth/providers/credentials"
import bcrypt from "bcryptjs"
import { connectDB } from "./db"

export const authConfig = {
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    }),
    Credentials({
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        const db = await connectDB()
        const user = await db.collection("users").findOne({
          email: credentials.email as string,
        })

        if (!user) {
          return null
        }

        const isValid = await bcrypt.compare(
          credentials.password as string,
          user.password
        )

        if (!isValid) {
          return null
        }

        return {
          id: user._id.toString(),
          email: user.email,
          name: user.name,
          role: user.role || "user",
          image: user.image,
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user, trigger, session }) {
      if (user) {
        token.id = user.id
        token.role = user.role || "user"
      }

      // Handle session updates
      if (trigger === "update" && session) {
        token = { ...token, ...session }
      }

      return token
    },
    async session({ session, token }) {
      if (token && session.user) {
        session.user.id = token.id as string
        session.user.role = token.role as string
      }
      return session
    },
    async signIn({ user, account, profile }) {
      if (account?.provider === "google") {
        const db = await connectDB()
        
        // Check if user exists
        const existingUser = await db.collection("users").findOne({
          email: user.email,
        })

        if (!existingUser) {
          // Create new user from Google account
          await db.collection("users").insertOne({
            name: user.name,
            email: user.email,
            image: user.image,
            role: "user",
            provider: "google",
            createdAt: new Date(),
            updatedAt: new Date(),
          })
        } else {
          // Update existing user
          await db.collection("users").updateOne(
            { email: user.email },
            {
              $set: {
                name: user.name,
                image: user.image,
                updatedAt: new Date(),
              },
            }
          )
        }
      }
      return true
    },
  },
  pages: {
    signIn: "/login",
  },
  session: {
    strategy: "jwt",
  },
} satisfies NextAuthConfig
