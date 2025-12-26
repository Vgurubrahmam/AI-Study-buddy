export const CONFIG = {
  // API Configuration
  gemini: {
    primaryKey: process.env.GEMINI_API_KEY_1,
    secondaryKey: process.env.GEMINI_API_KEY_2,
    model: "gemini-1.5-flash",
    maxTokens: 1000,
    temperature: 0.7,
  },

  // Database Configuration
  mongodb: {
    uri: process.env.MONGODB_URI,
    database: "ai_study_buddy",
  },

  // Session Configuration
  session: {
    maxAge: 60 * 60 * 24 * 30, // 30 days
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax" as const,
  },

  // Feature Flags
  features: {
    enableChatHistory: true,
    enableAdminDashboard: true,
    enableRealTimeStats: true,
    enableAutoRefresh: true,
  },

  // Limits
  limits: {
    maxChatsPerUser: 1000,
    maxCoursesPerAdmin: 500,
    chatHistoryRetention: 90, // days
  },
}

export function validateConfig() {
  const errors: string[] = []

  if (!CONFIG.mongodb.uri) {
    errors.push("MONGODB_URI is not configured")
  }

  if (!CONFIG.gemini.primaryKey && !CONFIG.gemini.secondaryKey) {
    errors.push("At least one Gemini API key (GEMINI_API_KEY_1 or GEMINI_API_KEY_2) must be configured")
  }

  if (errors.length > 0) {
    console.error("[v0] Configuration errors:", errors)
    throw new Error(`Configuration validation failed:\n${errors.join("\n")}`)
  }
}
