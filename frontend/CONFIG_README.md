# Frontend Configuration Guide

## Environment Variables

The frontend uses environment variables to configure the backend API URL.

### Setup Instructions

1. **Copy the example file:**
   ```bash
   cp .env.example .env.local
   ```

2. **Edit `.env.local`** for your environment:

   **For Local Development:**
   ```
   NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
   ```

   **For Production Deployment:**
   ```
   NEXT_PUBLIC_BACKEND_URL=https://veazy-backend.onrender.com
   ```

3. **Restart the development server** after changing environment variables:
   ```bash
   npm run dev
   ```

### Important Notes

- **NEXT_PUBLIC_** prefix is required for environment variables to be accessible in the browser
- `.env.local` is gitignored and should never be committed
- `.env.example` is the template - commit this to the repository
- Changes to environment variables require a server restart

### Files Modified

All API calls now use the centralized configuration from `/src/config/api.ts`:

- `src/components/ChatInterface.tsx`
- `src/components/AuthModal.tsx`
- `src/components/NewHero.tsx`
- `src/components/VisaDetails.tsx`
- `src/contexts/AuthContext.tsx`

### Usage in Code

```typescript
import { BACKEND_URL } from '@/config/api';

// Use in fetch calls
const response = await fetch(`${BACKEND_URL}/api/endpoint`);
```

### Deployment

When deploying to production (Vercel/Render/etc.), set the environment variable in your deployment platform's dashboard:

**Variable Name:** `NEXT_PUBLIC_BACKEND_URL`
**Value:** `https://veazy-backend.onrender.com`
