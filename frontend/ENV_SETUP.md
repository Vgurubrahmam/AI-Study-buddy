# Environment Variables Setup

## Required Environment Variables

Add these to your Vercel project settings under "Environment Variables":

### MongoDB Connection
\`\`\`
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/ai_study_buddy?retryWrites=true&w=majority
\`\`\`

Get this from MongoDB Atlas:
1. Go to mongodb.com/cloud/atlas
2. Create a free cluster
3. Go to Database > Connect > Drivers
4. Copy the connection string
5. Replace `<password>` and `<username>` with your credentials

### Gemini API Keys (Dual Keys for Redundancy)
\`\`\`
GEMINI_API_KEY_1=your_first_gemini_api_key
GEMINI_API_KEY_2=your_second_gemini_api_key (optional)
\`\`\`

Get from Google AI Studio:
1. Visit https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key and paste above
4. Create a second key for redundancy

### Optional: Upstash Redis (for real-time features)
\`\`\`
UPSTASH_REDIS_REST_URL=your_redis_url
UPSTASH_REDIS_REST_TOKEN=your_redis_token
\`\`\`

## Local Development (Optional)

Create a `.env.local` file in your project root:
\`\`\`
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/ai_study_buddy
GEMINI_API_KEY_1=your_key_1
GEMINI_API_KEY_2=your_key_2
NODE_ENV=development
\`\`\`

## Testing

After setup, test the connection:
1. Deploy the project to Vercel
2. Visit `/api/db/init` to initialize the database
3. Try signing up with a new account
4. Test the chat functionality

## Troubleshooting

- **MongoDB Connection Error**: Check your IP is whitelisted in MongoDB Atlas
- **Gemini API Error**: Ensure your API keys have required permissions
- **Chat not saving**: Verify MONGODB_URI is correctly set and database is accessible
