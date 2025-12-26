import { GoogleGenerativeAI } from "@google/generative-ai"

let client1: GoogleGenerativeAI | null = null
let client2: GoogleGenerativeAI | null = null

function initializeClients() {
  const apiKey1 = process.env.GEMINI_API_KEY_1
  const apiKey2 = process.env.GEMINI_API_KEY_2

  if (apiKey1) {
    client1 = new GoogleGenerativeAI(apiKey1)
  }

  if (apiKey2) {
    client2 = new GoogleGenerativeAI(apiKey2)
  }

  if (!apiKey1 && !apiKey2) {
    throw new Error("No Gemini API keys configured")
  }
}

export function getGeminiClient(useSecondary = false) {
  if (!client1 && !client2) {
    initializeClients()
  }

  // Return primary by default, secondary on request or if primary not available
  if (useSecondary && client2) {
    return client2
  }

  return client1 || client2
}

export function getGeminiModel(useSecondary = false) {
  const client = getGeminiClient(useSecondary)
  if (!client) {
    throw new Error("Gemini client not initialized")
  }

  return client.getGenerativeModel({ model: "gemini-1.5-flash" })
}

export async function sendMessageWithFallback(message: string) {
  let lastError: Error | null = null

  // Try primary key first
  try {
    console.log("[v0] Attempting with primary Gemini API key")
    const model = getGeminiModel(false)
    const chat = model.startChat({
      history: [],
      generationConfig: {
        maxOutputTokens: 1000,
        temperature: 0.7,
      },
    })

    const result = await chat.sendMessage(message)
    return result.response.text()
  } catch (error) {
    console.warn("[v0] Primary API key failed, trying secondary", error)
    lastError = error as Error
  }

  // Try secondary key if primary failed
  try {
    const model = getGeminiModel(true)
    if (!model) {
      throw new Error("No secondary API key available")
    }

    console.log("[v0] Attempting with secondary Gemini API key")
    const chat = model.startChat({
      history: [],
      generationConfig: {
        maxOutputTokens: 1000,
        temperature: 0.7,
      },
    })

    const result = await chat.sendMessage(message)
    return result.response.text()
  } catch (error) {
    console.error("[v0] Both API keys failed", error)
    lastError = error as Error
  }

  throw new Error(`Failed with both Gemini API keys: ${lastError?.message}`)
}
