#!/bin/bash

# 🐙 GitHub Setup Script for E-commerce API

echo "🐙 GitHub Repository Setup"
echo "=========================="
echo ""

# Check if git is configured
if ! git config user.name > /dev/null 2>&1; then
    echo "⚙️ Git not configured. Let's set it up:"
    echo ""
    read -p "Enter your GitHub username: " github_username
    read -p "Enter your email (for git): " github_email
    
    git config --global user.name "$github_username"
    git config --global user.email "$github_email"
    echo "✅ Git configured successfully!"
    echo ""
fi

echo "📋 Current git status:"
git status --short
echo ""

echo "📦 Repository Information:"
echo "------------------------"
echo "📊 Total files: $(find . -type f ! -path './.git/*' ! -path './venv/*' ! -path './__pycache__/*' | wc -l | tr -d ' ')"
echo "📝 Python files: $(find . -name '*.py' ! -path './venv/*' | wc -l | tr -d ' ')"
echo "📄 Documentation files: $(find . -name '*.md' | wc -l | tr -d ' ')"
echo "🔧 Configuration files: $(find . -name '*.json' -o -name '*.yaml' -o -name '*.yml' -o -name 'Dockerfile' -o -name 'Procfile' | wc -l | tr -d ' ')"
echo ""

echo "🚀 Instructions to create GitHub repository:"
echo "============================================"
echo ""
echo "1. 🌐 Go to https://github.com/new"
echo "2. 📝 Repository name: ecommerce-api (or your preferred name)"
echo "3. 📋 Description: Full-featured Flask e-commerce backend API with JWT auth and deployment configs"
echo "4. 🔓 Choose Public or Private"
echo "5. ❌ Don't initialize with README (we already have one)"
echo "6. ✅ Click 'Create repository'"
echo ""

echo "🔗 After creating the repository, run these commands:"
echo "===================================================="
echo ""
echo "# Replace 'yourusername' with your actual GitHub username"
echo "# Replace 'ecommerce-api' with your repository name if different"
echo ""
echo "git remote add origin https://github.com/yourusername/ecommerce-api.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""

echo "🎯 Or use the GitHub CLI (if installed):"
echo "========================================"
echo ""
echo "gh repo create ecommerce-api --public --source=. --remote=origin --push"
echo ""

echo "✨ Your repository will include:"
echo "==============================="
echo "📱 Complete Flask e-commerce API"
echo "🔐 JWT authentication system"
echo "🛒 Shopping cart and order management"
echo "👑 Admin dashboard with analytics"
echo "🚀 Multiple deployment configurations:"
echo "   - Render (render.yaml)"
echo "   - Heroku (Procfile, app.json)"
echo "   - Railway (railway.py)"
echo "   - PythonAnywhere (pythonanywhere_wsgi.py)"
echo "   - Docker (Dockerfile, docker-compose.yml)"
echo "📊 Complete Postman collection (40+ endpoints)"
echo "📚 Comprehensive documentation"
echo "🔧 Production-ready configuration"
echo ""

echo "🏃‍♂️ Quick Commands Summary:"
echo "============================"
echo ""
echo "# After creating GitHub repo, run:"
echo "git remote add origin https://github.com/YOURUSERNAME/REPONAME.git"
echo "git branch -M main"  
echo "git push -u origin main"
echo ""
echo "# Then deploy to Render by connecting your GitHub repo!"
echo ""

echo "💡 Pro Tips:"
echo "============"
echo "• Keep your GitHub repo public if you want to use free deployment tiers"
echo "• Your .env file is already in .gitignore (secure!)"
echo "• All deployment platforms can connect directly to your GitHub repo"
echo "• Update the repository URLs in deployment guides after creating repo"
echo ""

echo "🎉 Ready to push to GitHub! Create your repository and run the commands above."
