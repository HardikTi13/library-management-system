# Deployment Guide - Library Checkout System

This guide covers deploying the Library Checkout System with the backend on **Render** and the frontend on **Vercel**.

## Prerequisites

- Git repository (GitHub, GitLab, or Bitbucket)
- Render account (https://render.com)
- Vercel account (https://vercel.com)

---

## Part 1: Backend Deployment (Render)

### Step 1: Prepare Your Repository

Ensure your code is pushed to a Git repository with all deployment files:
- `requirements.txt`
- `Procfile`
- `runtime.txt`
- `.env.example`

### Step 2: Create PostgreSQL Database on Render

1. Go to Render Dashboard → **New** → **PostgreSQL**
2. Configure:
   - **Name**: `library-db` (or your preferred name)
   - **Database**: `library_checkout`
   - **User**: (auto-generated)
   - **Region**: Choose closest to your users
   - **Plan**: Free tier is fine for testing
3. Click **Create Database**
4. **Important**: Copy the **Internal Database URL** (starts with `postgresql://`)

### Step 3: Create Web Service on Render

1. Go to Render Dashboard → **New** → **Web Service**
2. Connect your Git repository
3. Configure:
   - **Name**: `library-backend` (or your preferred name)
   - **Region**: Same as your database
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (or specify if backend is in subdirectory)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn library_checkout.wsgi`

### Step 4: Set Environment Variables

In the Render web service settings, add these environment variables:

```
SECRET_KEY=<generate-a-strong-secret-key>
DEBUG=False
ALLOWED_HOSTS=<your-app-name>.onrender.com
DATABASE_URL=<paste-internal-database-url-from-step-2>
CORS_ALLOWED_ORIGINS=<your-vercel-frontend-url>
```

**To generate a SECRET_KEY**, run this in Python:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Step 5: Deploy

1. Click **Create Web Service**
2. Render will automatically build and deploy
3. Once deployed, run migrations:
   - Go to your service → **Shell** tab
   - Run: `python manage.py migrate`
   - Run: `python manage.py createsuperuser` (optional, for admin access)

### Step 6: Note Your Backend URL

Your backend will be available at: `https://<your-app-name>.onrender.com`

---

## Part 2: Frontend Deployment (Vercel)

### Step 1: Create Environment Variable File

In the `frontend` directory, create a `.env.production` file:

```
VITE_API_URL=https://<your-render-backend-url>.onrender.com
```

**Important**: Replace `<your-render-backend-url>` with your actual Render backend URL from Part 1.

### Step 2: Deploy to Vercel

#### Option A: Using Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

3. Deploy:
   ```bash
   vercel
   ```

4. Follow the prompts:
   - Set up and deploy: Yes
   - Which scope: Your account
   - Link to existing project: No
   - Project name: `library-frontend` (or your choice)
   - Directory: `./` (current directory)
   - Override settings: No

5. Set environment variable:
   ```bash
   vercel env add VITE_API_URL production
   ```
   Then paste your backend URL when prompted.

6. Deploy to production:
   ```bash
   vercel --prod
   ```

#### Option B: Using Vercel Dashboard

1. Go to Vercel Dashboard → **Add New** → **Project**
2. Import your Git repository
3. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add Environment Variable:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://<your-render-backend-url>.onrender.com`
5. Click **Deploy**

### Step 3: Update Backend CORS Settings

1. Go back to Render → Your web service → **Environment**
2. Update `CORS_ALLOWED_ORIGINS` to include your Vercel URL:
   ```
   CORS_ALLOWED_ORIGINS=https://<your-vercel-app>.vercel.app,http://localhost:5173
   ```
3. Save and redeploy

---

## Part 3: Create Initial Data

### Create a Librarian Account

1. Go to your Render service → **Shell**
2. Run the librarian creation script:
   ```bash
   python create_librarian.py
   ```
   Or manually:
   ```bash
   python manage.py shell
   ```
   Then:
   ```python
   from django.contrib.auth.models import User
   from circulation.models import Member
   
   user = User.objects.create_user(username='librarian', password='your-password')
   Member.objects.create(user=user, user_type='LIBRARIAN')
   ```

---

## Testing Your Deployment

1. Visit your Vercel frontend URL
2. Try signing up as a member
3. Log in with the librarian account
4. Test creating books, checking out, etc.

---

## Troubleshooting

### Backend Issues

**500 Error on Render:**
- Check logs: Render Dashboard → Your service → **Logs**
- Verify all environment variables are set correctly
- Ensure migrations ran successfully

**Database Connection Error:**
- Verify `DATABASE_URL` is the **Internal Database URL**
- Check database is in the same region as web service

**Static Files Not Loading:**
- Run `python manage.py collectstatic --noinput` in Shell
- Verify `STATIC_ROOT` is configured in settings.py

### Frontend Issues

**API Calls Failing:**
- Check `VITE_API_URL` environment variable in Vercel
- Verify CORS settings in backend include Vercel URL
- Check browser console for CORS errors

**Blank Page After Deployment:**
- Check Vercel build logs for errors
- Verify `vercel.json` is configured correctly
- Check that environment variables are set for production

### CORS Errors

If you see CORS errors in browser console:
1. Verify backend `CORS_ALLOWED_ORIGINS` includes your Vercel URL
2. Make sure there's no trailing slash in URLs
3. Redeploy backend after changing CORS settings

---

## Updating Your Deployment

### Backend Updates
- Push changes to Git
- Render will auto-deploy on push (if enabled)
- Or manually trigger deploy in Render Dashboard

### Frontend Updates
- Push changes to Git
- Vercel will auto-deploy on push
- Or manually trigger deploy in Vercel Dashboard

---

## Free Tier Limitations

**Render Free Tier:**
- Services spin down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- 750 hours/month (enough for one service)

**Vercel Free Tier:**
- 100 GB bandwidth/month
- Unlimited deployments
- Automatic SSL

---

## Production Checklist

- [ ] Backend deployed on Render
- [ ] PostgreSQL database created and connected
- [ ] All environment variables set on Render
- [ ] Database migrations run successfully
- [ ] Frontend deployed on Vercel
- [ ] Frontend environment variable set
- [ ] CORS configured with Vercel URL
- [ ] Librarian account created
- [ ] Tested signup, login, and core features
- [ ] SSL/HTTPS working on both frontend and backend

---

## Support

For issues:
- **Render**: https://render.com/docs
- **Vercel**: https://vercel.com/docs
- **Django**: https://docs.djangoproject.com/
