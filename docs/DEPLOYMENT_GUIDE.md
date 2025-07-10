# 🚀 E-commerce API Deployment Guide

This guide covers multiple deployment options for your Flask e-commerce API with database hosting.

## 📋 Deployment Options Overview

| Platform           | Database         | Difficulty | Cost                | Best For           |
| ------------------ | ---------------- | ---------- | ------------------- | ------------------ |
| **Railway**        | PostgreSQL/MySQL | Easy       | Free tier available | Modern platform    |
| **Heroku**         | PostgreSQL       | Easy       | Free tier available | Quick deployment   |
| **PythonAnywhere** | MySQL            | Easy       | Free tier available | Python-focused     |
| **Render**         | PostgreSQL       | Easy       | Free tier available | Modern alternative |
| **DigitalOcean**   | Managed Database | Medium     | $5+/month           | Production apps    |
| **AWS**            | RDS              | Hard       | Pay-as-you-go       | Enterprise         |

---

## 🔥 Option 1: Railway (Recommended - Easiest)

Railway is modern, has great Python support, and provides both app hosting and database.

### Step 1: Setup Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Install Railway CLI: `npm install -g @railway/cli`

### Step 2: Prepare Your Project

Already done! Your project includes:

- ✅ `requirements.txt`
- ✅ `Dockerfile`
- ✅ `railway.py` (entry point)
- ✅ Environment configuration

### Step 3: Deploy to Railway

```bash
# 1. Login to Railway
railway login

# 2. Initialize project
railway init

# 3. Add PostgreSQL database
railway add postgresql

# 4. Set environment variables
railway env set FLASK_ENV=production
railway env set SECRET_KEY="your-super-secret-key-here"
railway env set JWT_SECRET_KEY="your-jwt-secret-key-here"

# 5. Deploy
railway up
```

### Step 4: Setup Database

```bash
# Connect to your Railway database and run migrations
railway shell
python deploy.py
python create_sample_data.py
```

**Railway automatically provides:**

- Free PostgreSQL database
- Environment variables for database connection
- HTTPS SSL certificates
- Custom domain options

---

## 🌟 Option 2: Heroku (Classic Choice)

### Step 1: Setup Heroku

1. Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Create account at [heroku.com](https://heroku.com)

### Step 2: Create Heroku App

```bash
# Login to Heroku
heroku login

# Create app (replace 'your-app-name' with unique name)
heroku create your-ecommerce-api

# Add PostgreSQL database
heroku addons:create heroku-postgresql:essential-0

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY="your-super-secret-key-here"
heroku config:set JWT_SECRET_KEY="your-jwt-secret-key-here"
```

### Step 3: Create Procfile

```bash
echo "web: gunicorn wsgi:app" > Procfile
echo "release: python deploy.py" >> Procfile
```

### Step 4: Deploy

```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"

# Deploy to Heroku
git remote add heroku https://git.heroku.com/your-ecommerce-api.git
git push heroku main

# Setup database
heroku run python create_sample_data.py
```

---

## 💻 Option 3: PythonAnywhere (Python-Focused)

### Step 1: Setup Account

1. Go to [pythonanywhere.com](https://pythonanywhere.com)
2. Sign up for free account
3. Open a Bash console

### Step 2: Upload Your Code

```bash
# Clone your repository or upload files
git clone https://github.com/yourusername/ecommerce_api.git
cd ecommerce_api

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Setup Database

```bash
# PythonAnywhere provides MySQL
# Update your config.py to use MySQL instead of SQLite
mysql -u yourusername -p
CREATE DATABASE ecommerce_db;
```

### Step 4: Configure Web App

1. Go to Web tab in PythonAnywhere dashboard
2. Create new web app
3. Choose Flask framework
4. Set source code path: `/home/yourusername/ecommerce_api`
5. Set virtualenv path: `/home/yourusername/ecommerce_api/venv`

---

## 🚀 Option 4: Render (Modern Alternative)

### Step 1: Setup Render

1. Go to [render.com](https://render.com)
2. Connect your GitHub account
3. Create new Web Service

### Step 2: Configure Service

- **Repository**: Connect your GitHub repo
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn wsgi:app`
- **Environment**: Python 3.11

### Step 3: Add Database

1. Create PostgreSQL database on Render
2. Copy connection string to environment variables

### Step 4: Set Environment Variables

```
FLASK_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=postgresql://... (from Render database)
```

---

## ☁️ Option 5: DigitalOcean App Platform

### Step 1: Setup DigitalOcean

1. Create account at [digitalocean.com](https://digitalocean.com)
2. Go to App Platform
3. Create new app from GitHub repository

### Step 2: Configure App

- **Source**: GitHub repository
- **Plan**: Basic ($5/month)
- **Build Command**: `pip install -r requirements.txt`
- **Run Command**: `gunicorn wsgi:app`

### Step 3: Add Managed Database

1. Create PostgreSQL managed database
2. Add connection string to app environment

---

## 🛠️ Required Environment Variables for All Platforms

```bash
# Required for all deployments
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-too

# Database (auto-provided by most platforms)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Optional
DEBUG=False
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

---

## 📦 Pre-Deployment Checklist

### ✅ Code Preparation

- [x] `requirements.txt` with all dependencies
- [x] `Dockerfile` for containerization
- [x] `wsgi.py` entry point
- [x] `deploy.py` for database setup
- [x] Environment configuration in `config.py`
- [x] `.gitignore` to exclude sensitive files

### ✅ Security

- [ ] Change default `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Set `DEBUG=False` in production
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS (most platforms provide this automatically)

### ✅ Database

- [ ] Choose between SQLite (dev) and PostgreSQL/MySQL (production)
- [ ] Run database migrations
- [ ] Create sample data if needed

### ✅ Testing

- [ ] Test API endpoints locally
- [ ] Import Postman collection for testing
- [ ] Verify authentication flows

---

## 🔧 Quick Start Commands

### For Railway (Recommended):

```bash
npm install -g @railway/cli
railway login
railway init
railway add postgresql
railway env set FLASK_ENV=production
railway env set SECRET_KEY="your-secret-key"
railway env set JWT_SECRET_KEY="your-jwt-key"
railway up
```

### For Heroku:

```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:essential-0
heroku config:set FLASK_ENV=production SECRET_KEY="your-key"
git push heroku main
```

---

## 🌐 After Deployment

1. **Update Postman Collection**: Change `base_url` to your deployed URL
2. **Test All Endpoints**: Use the provided Postman collection
3. **Monitor Logs**: Check platform-specific logs for any issues
4. **Setup Custom Domain**: Most platforms offer free custom domains
5. **Enable SSL**: Usually automatic on modern platforms

---

## 📞 Support & Troubleshooting

### Common Issues:

1. **502 Bad Gateway**: Check if app is binding to correct PORT
2. **Database Connection**: Verify DATABASE_URL environment variable
3. **Static Files**: Ensure `static/uploads` directory exists
4. **Memory Limits**: Free tiers have memory restrictions

### Platform-Specific Help:

- **Railway**: [docs.railway.app](https://docs.railway.app)
- **Heroku**: [devcenter.heroku.com](https://devcenter.heroku.com)
- **Render**: [render.com/docs](https://render.com/docs)
- **PythonAnywhere**: [help.pythonanywhere.com](https://help.pythonanywhere.com)

### Next Steps:

1. Choose a platform (Railway recommended for beginners)
2. Follow the specific deployment steps
3. Test your deployed API
4. Share your API URL for testing!

Your e-commerce API is ready for production! 🎉
