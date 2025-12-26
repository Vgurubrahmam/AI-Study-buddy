# Authentication System Documentation

## Overview
This application uses JWT (JSON Web Token) based authentication with localStorage for token storage.

## Features
- ✅ User signup with bcrypt password hashing
- ✅ User login with JWT token generation
- ✅ Token storage in localStorage
- ✅ Protected routes with authentication checks
- ✅ Auth context provider for global auth state
- ✅ Auto-redirect to login for unauthenticated users
- ✅ Logout functionality

## Flow

### 1. Signup Flow
1. User fills signup form (`/signup`)
2. Form validates password match
3. API creates user with hashed password
4. User is redirected to `/login`

### 2. Login Flow
1. User fills login form (`/login`)
2. API validates credentials
3. JWT token is generated and returned
4. Token and user data stored in localStorage
5. User is redirected to `/dashboard`

### 3. Protected Routes
Protected pages automatically redirect to `/login` if user is not authenticated.

## Usage

### Using Auth in Components

```tsx
import { useAuth } from "@/components/auth-provider"

function MyComponent() {
  const { user, token, isAuthenticated, logout } = useAuth()
  
  return (
    <div>
      <p>Welcome {user?.name}</p>
      <button onClick={logout}>Logout</button>
    </div>
  )
}
```

### Protecting a Route

```tsx
import { useProtectedRoute } from "@/hooks/use-protected-route"

export default function ProtectedPage() {
  const { isLoading } = useProtectedRoute()
  
  if (isLoading) return <div>Loading...</div>
  
  return <div>Protected content</div>
}
```

### Making Authenticated API Requests

```tsx
import { getAuthHeaders } from "@/lib/auth-utils"

const response = await fetch("/api/some-endpoint", {
  method: "POST",
  headers: getAuthHeaders(),
  body: JSON.stringify(data)
})
```

### Server-side Auth Verification

```tsx
import { requireAuth } from "@/lib/auth-middleware"

export async function GET(req: Request) {
  const auth = await requireAuth(req)
  
  if ("error" in auth) {
    return auth.error
  }
  
  const { user } = auth
  // user is authenticated, proceed with logic
}
```

## Environment Variables

Add to your `.env` file:
```
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production-min-32-chars
MONGODB_URI=mongodb://localhost:27017/AI-Study-buddy
```

## API Endpoints

- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Login and receive JWT token
- `POST /api/auth/logout` - Logout (clears client-side storage)

## Security Notes

⚠️ **Important**: 
- Change the JWT_SECRET in production
- Use HTTPS in production
- Tokens expire in 30 days by default
- Passwords are hashed using bcrypt with salt rounds of 10
