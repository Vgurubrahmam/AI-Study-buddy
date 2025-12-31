# Deploying AI Study Buddy Backend to Google Cloud

This guide covers deploying the FastAPI backend to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud CLI** installed ([Install Guide](https://cloud.google.com/sdk/docs/install))
3. **Docker** installed locally (optional, for local testing)
4. **MongoDB Atlas** account (or Cloud MongoDB)

## Quick Start Deployment

### Step 1: Setup Google Cloud Project

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create ai-study-buddy --name="AI Study Buddy"

# Set the project
gcloud config set project ai-study-buddy

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### Step 2: Configure Secrets

Store sensitive data in Secret Manager:

```bash
# Create secrets
echo -n "your-mongodb-uri" | gcloud secrets create MONGODB_URI --data-file=-
echo -n "your-jwt-secret" | gcloud secrets create JWT_SECRET --data-file=-
echo -n "your-gemini-api-key" | gcloud secrets create GEMINI_API_KEY_1 --data-file=-
```

### Step 3: Deploy with Cloud Build

```bash
# Navigate to backend directory
cd backend

# Deploy using Cloud Build
gcloud builds submit --config=cloudbuild.yaml
```

### Step 4: Manual Deployment (Alternative)

If you prefer manual deployment:

```bash
# Build the image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ai-study-buddy-backend -f Dockerfile.cloudrun

# Deploy to Cloud Run
gcloud run deploy ai-study-buddy-backend \
  --image gcr.io/YOUR_PROJECT_ID/ai-study-buddy-backend \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "ENVIRONMENT=production" \
  --set-secrets "MONGODB_URI=MONGODB_URI:latest,JWT_SECRET=JWT_SECRET:latest,GEMINI_API_KEY_1=GEMINI_API_KEY_1:latest"
```

## Environment Variables

Set these in Cloud Run or as secrets:

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGODB_URI` | MongoDB connection string | Yes |
| `JWT_SECRET` | Secret for JWT signing | Yes |
| `GEMINI_API_KEY_1` | Google Gemini API key | Yes |
| `ENVIRONMENT` | `production` | Yes |
| `CORS_ORIGINS` | Frontend URLs (comma-separated) | Yes |
| `DATABASE_NAME` | MongoDB database name | No (default: ai_study_buddy) |

## Configuring Secrets in Cloud Run

### Option A: Environment Variables (Not Recommended for Secrets)

```bash
gcloud run services update ai-study-buddy-backend \
  --set-env-vars "MONGODB_URI=your-uri,JWT_SECRET=your-secret"
```

### Option B: Secret Manager (Recommended)

```bash
# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding MONGODB_URI \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Deploy with secrets
gcloud run deploy ai-study-buddy-backend \
  --set-secrets "MONGODB_URI=MONGODB_URI:latest"
```

## Setting Up MongoDB Atlas

1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a free cluster
3. Create a database user
4. Whitelist Cloud Run IPs (or use `0.0.0.0/0` for all IPs)
5. Get the connection string

## Connecting Frontend

After deployment, update your frontend's `.env`:

```env
NEXT_PUBLIC_API_URL=https://ai-study-buddy-backend-xxxxx-uc.a.run.app
```

## Monitoring & Logs

```bash
# View logs
gcloud run services logs read ai-study-buddy-backend --region us-central1

# Stream logs
gcloud run services logs tail ai-study-buddy-backend --region us-central1

# View in Cloud Console
# https://console.cloud.google.com/run
```

## Custom Domain (Optional)

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service ai-study-buddy-backend \
  --domain api.yourdomain.com \
  --region us-central1
```

## Cost Optimization

1. **Set min-instances to 0** for cold starts (saves money)
2. **Use appropriate memory/CPU** - start with 2Gi/2CPU
3. **Set concurrency** to maximize instance usage
4. **Use Gemini API** instead of local models (no GPU needed)

## Troubleshooting

### Build Fails
```bash
# Check build logs
gcloud builds log BUILD_ID
```

### Memory Issues
```bash
# Increase memory
gcloud run services update ai-study-buddy-backend --memory 4Gi
```

### Cold Start Too Slow
```bash
# Set minimum instances
gcloud run services update ai-study-buddy-backend --min-instances 1
```

### CORS Issues
Ensure `CORS_ORIGINS` includes your frontend URL:
```bash
gcloud run services update ai-study-buddy-backend \
  --set-env-vars "CORS_ORIGINS=https://your-frontend.vercel.app"
```

## CI/CD with GitHub Actions

Create `.github/workflows/deploy.yml` in your repo:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]
    paths: ['backend/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - uses: google-github-actions/setup-gcloud@v2
      
      - name: Deploy
        working-directory: backend
        run: |
          gcloud builds submit --config=cloudbuild.yaml
```

## Architecture Notes

- **Cloud Run** automatically scales based on traffic
- **Gemini API** is recommended over local models for serverless
- **MongoDB Atlas** provides managed database with auto-scaling
- **Secret Manager** keeps credentials secure

For GPU workloads (local Phi-3 model), consider:
- **Compute Engine** with GPU
- **Vertex AI** for managed ML
- **GKE** with GPU node pools
