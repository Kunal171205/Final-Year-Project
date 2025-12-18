# Deploy to Render - Step by Step Guide

## ✅ Your code is now on GitHub!

Your repository: `https://github.com/Kunal171205/Final-Year-Project`

## 🚀 Deploy to Render (FREE - No CLI Required!)

### Step 1: Sign Up
1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with your **GitHub account** (recommended) or email

### Step 2: Create New Web Service
1. Once logged in, click the **"New +"** button (top right)
2. Select **"Web Service"**

### Step 3: Connect GitHub Repository
1. Click **"Connect account"** if you haven't connected GitHub yet
2. Authorize Render to access your repositories
3. Search for: `Final-Year-Project`
4. Click **"Connect"** next to your repository

### Step 4: Configure Your App
Fill in these settings:

- **Name**: `industry-explorer` (or any name you like)
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main`
- **Root Directory**: Leave empty (or `.` if needed)
- **Environment**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  gunicorn app:app
  ```

### Step 5: Add Environment Variables
Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

1. **Key**: `FLASK_SECRET_KEY`
   **Value**: Generate a random key (you can use: `python -c "import secrets; print(secrets.token_hex(32))"` in terminal, or use any random string)

2. **Key**: `DATABASE_URL` (Optional - leave empty for SQLite, or add PostgreSQL URL later)

### Step 6: Deploy!
1. Scroll down and click **"Create Web Service"**
2. Wait 2-3 minutes while Render builds and deploys your app
3. You'll see build logs in real-time
4. When it says "Live", your app is ready! 🎉

### Step 7: Get Your Live URL
- Your app will be live at: `https://your-app-name.onrender.com`
- Copy this URL and add it to your GitHub README!

## ✅ That's It!

Your Flask app is now live on the internet, and it will automatically redeploy whenever you push to GitHub!

## Troubleshooting

### If build fails:
- Check the build logs in Render dashboard
- Make sure `requirements.txt` has all dependencies
- Verify Python version compatibility

### If app crashes:
- Check the logs tab in Render
- Verify environment variables are set correctly
- Make sure `gunicorn` is in `requirements.txt` (it is!)

### Database issues:
- SQLite files don't persist on free tier
- Consider using Render's free PostgreSQL database (add it as a separate service)

## Next Steps

1. ✅ Your code is on GitHub
2. ✅ Your app is deployed on Render
3. 📝 Update your GitHub README with the live link!

---

**Need help?** Check the logs in Render dashboard - they show exactly what's happening!

