# Deployment Guide for Flask Application

## Important Note
**GitHub Pages does NOT support Flask applications** - GitHub Pages only hosts static websites. Flask requires a server to run Python code.

## Deployment Options

### Option 1: Render (Recommended - Free Tier Available)
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `Kunal171205/Final-Year-Project`
4. Configure:
   - **Name**: your-app-name
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add environment variables:
   - `FLASK_SECRET_KEY`: Generate a secure random key
   - `DATABASE_URL`: (Optional) If using external database
6. Click "Create Web Service"

**Update requirements.txt** to include gunicorn:
```bash
pip install gunicorn
echo gunicorn >> requirements.txt
```

### Option 2: Railway
1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway auto-detects Flask apps
5. Add environment variables in the dashboard
6. Your app will be live automatically

### Option 3: Heroku
1. Install Heroku CLI: [heroku.com](https://devcenter.heroku.com/articles/heroku-cli)
2. Create `Procfile`:
   ```
   web: gunicorn app:app
   ```
3. Run:
   ```bash
   heroku create your-app-name
   heroku config:set FLASK_SECRET_KEY=your-secret-key
   git push heroku main
   ```

### Option 4: PythonAnywhere (Free Tier Available)
1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Go to "Web" tab → "Add a new web app"
3. Choose Flask and Python version
4. Upload your files or clone from GitHub
5. Configure WSGI file to point to `app.py`
6. Reload web app

## Pre-Deployment Checklist

- [ ] Update `requirements.txt` with all dependencies
- [ ] Ensure `.gitignore` excludes sensitive files (instance/, __pycache__, etc.)
- [ ] Set `FLASK_SECRET_KEY` as environment variable (never commit secrets!)
- [ ] Change `debug=True` to `debug=False` in production
- [ ] Use production database (not SQLite for production)
- [ ] Test locally before deploying

## Required Changes for Production

### 1. Update `app.py` for Production
```python
if __name__ == "__main__":
    # Only run in debug mode locally
    app.run(debug=False, host='0.0.0.0', port=5000)
```

### 2. Add `Procfile` (for Heroku/Railway)
```
web: gunicorn app:app
```

### 3. Update `requirements.txt`
Make sure it includes:
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
pymongo==4.6.0
gunicorn
```

## Environment Variables
Set these in your hosting platform:
- `FLASK_SECRET_KEY`: Random secret key for sessions
- `DATABASE_URL`: Database connection string (if using external DB)

## Troubleshooting

### Issue: App crashes on startup
- Check logs in your hosting platform
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

### Issue: Database errors
- SQLite files don't persist on most free hosting platforms
- Use external database (PostgreSQL, MySQL) for production
- Update `DATABASE_URL` environment variable

### Issue: Static files not loading
- Ensure `static/` folder is in the repository
- Check file paths in templates (use `url_for('static', filename='...')`)

## Making Repository Public
If you want to make your GitHub repository public:
1. Go to repository settings on GitHub
2. Scroll to "Danger Zone"
3. Click "Change visibility" → "Make public"

## GitHub Actions (CI/CD)
See `.github/workflows/deploy.yml` for automated deployment setup.

