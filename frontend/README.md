# AI Study Buddy - Full-Stack Real-Time AI Tutoring Platform

A production-ready Next.js application with AI-powered tutoring, real-time features, MongoDB integration, and comprehensive admin dashboard.

## Features

- **AI Chat Interface**: Powered by Google Gemini AI with dual API key support for redundancy
- **Real-Time Analytics**: Live stats dashboard with auto-refresh capabilities
- **Chat History**: Complete conversation tracking with MongoDB persistence
- **User Authentication**: Secure signup/login with bcrypt password hashing
- **Admin Dashboard**: Full CRUD operations for course management and user monitoring
- **Course Management**: Browse, enroll, and track progress across multiple courses
- **Responsive Design**: Mobile-first UI built with Tailwind CSS and shadcn/ui
- **Production-Ready**: Error handling, input validation, and security best practices

## Tech Stack

- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS v4
- **UI Components**: shadcn/ui with Recharts for analytics
- **Backend**: Next.js API routes, Server Actions
- **Database**: MongoDB with mongoose
- **Authentication**: Custom JWT with HTTP-only cookies
- **AI**: Google Generative AI SDK with Gemini 1.5 Flash
- **Deployment**: Vercel-ready

## Quick Start

### Prerequisites

- Node.js 18+
- MongoDB Atlas account (free tier available)
- Google Gemini API keys (free tier available)

### 1. Clone and Install

\`\`\`bash
git clone <your-repo>
cd ai-study-buddy
npm install
\`\`\`

### 2. Set Environment Variables

Create a `.env.local` file:

\`\`\`env
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/ai_study_buddy
GEMINI_API_KEY_1=your_first_api_key
GEMINI_API_KEY_2=your_second_api_key
NODE_ENV=development
\`\`\`

### 3. Initialize Database

\`\`\`bash
npm run dev
# Visit http://localhost:3000/api/db/init
\`\`\`

### 4. Start Development Server

\`\`\`bash
npm run dev
# Visit http://localhost:3000
\`\`\`

## Project Structure

\`\`\`
app/
├── api/
│   ├── auth/           # Authentication routes
│   ├── chat/           # Gemini chat endpoint
│   ├── admin/          # Admin dashboard APIs
│   ├── user/           # User-specific APIs
│   └── db/             # Database initialization
├── admin/              # Admin dashboard
├── chat/               # Chat interface
├── history/            # User chat history
├── settings/           # Settings page
├── login/              # Login page
├── signup/             # Signup page
└── dashboard/          # User dashboard
lib/
├── mongodb.ts          # MongoDB connection
├── db.ts               # Database utilities
├── auth.ts             # Authentication helpers
├── gemini-client.ts    # Gemini API with fallback
└── config.ts           # Configuration management
\`\`\`

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/logout` - Logout
- `GET /api/auth/session` - Get current session

### Chat
- `POST /api/chat` - Send message to Gemini with dual key fallback

### Admin
- `GET /api/admin/courses` - List all courses
- `POST /api/admin/courses` - Create course
- `PUT /api/admin/courses` - Update course
- `DELETE /api/admin/courses` - Delete course
- `GET /api/admin/chat-history` - View all chat history
- `DELETE /api/admin/chat-history` - Delete chat entry
- `GET /api/admin/stats` - Real-time dashboard stats

### User
- `GET /api/user/chat-history` - Get user's chat history
- `DELETE /api/user/chat-history` - Delete user's chat entry

## Configuration

See `ENV_SETUP.md` for detailed environment variable setup instructions.

See `DEPLOYMENT.md` for production deployment guide.

## Key Features Explained

### Dual API Key System

The application supports dual Gemini API keys with automatic fallback:

\`\`\`typescript
GEMINI_API_KEY_1=primary_key    # Primary API key
GEMINI_API_KEY_2=secondary_key  # Fallback if primary fails
\`\`\`

If the primary key fails, the system automatically tries the secondary key, ensuring uninterrupted service.

### Real-Time Admin Dashboard

- Auto-refreshing stats every 30 seconds
- Live chat history monitoring
- Course management with instant UI updates
- Manual refresh button for on-demand updates

### Chat History & Persistence

All conversations are saved to MongoDB with:
- User ID tracking
- Timestamps
- Full message content
- Token usage estimation

### Security

- Passwords hashed with bcrypt
- HTTP-only cookies for sessions
- HTTPS enforcement in production
- Input validation and sanitization
- MongoDB aggregation for performance

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import repository in Vercel
3. Add environment variables
4. Deploy

See `DEPLOYMENT.md` for detailed steps.

## Testing

### Test Credentials
- Email: `test@example.com`
- Password: `test123`

Or create a new account at `/signup`

### Test Admin Panel
- Visit `/admin` after login to manage courses and view chat history

## Troubleshooting

### MongoDB Connection Issues
- Check IP whitelist in MongoDB Atlas
- Verify connection string format
- Ensure database `ai_study_buddy` exists

### Gemini API Errors
- Verify API keys are valid and active
- Check Google Cloud Console for quota limits
- Ensure API is enabled for the project

### Chat Not Saving
- Verify MongoDB is running and accessible
- Check `/api/db/init` was called successfully
- Ensure user is authenticated before sending messages

## Performance

- MongoDB indexes on userId and createdAt for fast queries
- Connection pooling configured
- Chat history paginated (50 results default)
- Gzip compression enabled in Next.js

## Future Enhancements

- [ ] WebSocket for real-time collaborative learning
- [ ] Multi-language support
- [ ] Advanced analytics with data visualization
- [ ] Badges and gamification
- [ ] Export chat history as PDF
- [ ] Voice chat capability
- [ ] Mobile native app

## Contributing

Contributions welcome! Please follow the existing code style and add tests for new features.

## License

MIT

## Support

For issues and questions:
1. Check `ENV_SETUP.md` and `DEPLOYMENT.md`
2. Review API error messages in browser console
3. Check MongoDB and API key configurations
4. See troubleshooting section above
