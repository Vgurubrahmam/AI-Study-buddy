# Deployment Guide

## Vercel Deployment

### Prerequisites
- GitHub repository with your project
- MongoDB Atlas account
- Google Gemini API keys

### Step 1: Set Up MongoDB Atlas

1. Go to [mongodb.com/cloud/atlas](https://mongodb.com/cloud/atlas)
2. Create a free cluster
3. Create a database user
4. Get connection string: Database > Connect > Drivers
5. Copy the connection string (replace `<password>` with your user password)

### Step 2: Get Gemini API Keys

1. Visit [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Create 2 keys for redundancy
4. Copy both keys

### Step 3: Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository
4. In "Environment Variables", add:

\`\`\`
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/ai_study_buddy?retryWrites=true&w=majority
GEMINI_API_KEY_1=your_first_api_key
GEMINI_API_KEY_2=your_second_api_key
NODE_ENV=production
\`\`\`

5. Click "Deploy"

### Step 4: Initialize Database

After deployment:

1. Visit `https://your-domain.vercel.app/api/db/init`
2. You should see: `{"success":true,"message":"Database initialized successfully"}`
3. Sign up at `/signup` with test account
4. Test chat at `/chat`

## Environment Variables Checklist

- [ ] `MONGODB_URI` - MongoDB Atlas connection string
- [ ] `GEMINI_API_KEY_1` - Primary Gemini API key
- [ ] `GEMINI_API_KEY_2` - Secondary Gemini API key (optional for backup)
- [ ] `NODE_ENV` - Set to `production`

## Troubleshooting

### MongoDB Connection Failed
- Check IP whitelist in MongoDB Atlas: Network Access > Add Current IP
- Verify username and password in connection string
- Ensure database name is `ai_study_buddy`

### Gemini API Error
- Verify API keys are valid at aistudio.google.com
- Check API quotas and billing in Google Cloud Console
- Try both primary and secondary keys work independently

### Chat History Not Saving
- Check MongoDB connection is working
- Verify collection indexes are created (visit `/api/db/init`)
- Check user is authenticated before sending messages

## Scaling Considerations

For production use:
- Enable MongoDB backup in Atlas settings
- Monitor API usage in Google Cloud Console
- Set up alerts for quota limits
- Consider connection pooling for high traffic
- Use CDN for static assets

## Security Best Practices

- Never commit API keys to GitHub
- Use Vercel's environment variables for sensitive data
- Enable MongoDB IP whitelist
- Use HTTPS only (enabled by default on Vercel)
- Implement rate limiting for API routes
- Validate and sanitize all user inputs
