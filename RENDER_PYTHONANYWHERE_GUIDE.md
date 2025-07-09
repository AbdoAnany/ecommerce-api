# 🚀 Render & PythonAnywhere Deployment Guide

## 🎨 **Option 1: Render (Recommended - Modern Platform)**

### ⏱️ **Deployment Time: 10-15 minutes**

#### **Step 1: Prepare Locally**

```bash
# Run the setup script
./deploy_render.sh
```

#### **Step 2: Setup Render Account**

1. 🌐 Go to [render.com](https://render.com)
2. 🔗 Sign up with your **GitHub account**
3. ✅ Verify your email

#### **Step 3: Create Web Service**

1. 📦 Click **"New"** → **"Web Service"**
2. 🔗 **Connect your GitHub repository**
3. ⚙️ Configure the service:
   ```
   Name: ecommerce-api
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn wsgi:app
   Plan: Free
   ```

#### **Step 4: Add Environment Variables**

In the **Environment** section, add:

```bash
FLASK_ENV=production
DEBUG=False
SECRET_KEY=<use-generated-key-from-script>
JWT_SECRET_KEY=<use-generated-key-from-script>
```

#### **Step 5: Create PostgreSQL Database**

1. 🗄️ In Render dashboard, click **"New"** → **"PostgreSQL"**
2. ⚙️ Configure:
   ```
   Name: ecommerce-db
   Plan: Free
   Region: Oregon (US West) - or closest to you
   PostgreSQL Version: 15 (or latest)
   ```
3. ✅ Click **"Create Database"** (takes 2-3 minutes)

4. 📋 **Copy the Internal Database URL:**
   - Once database is created, click on **"ecommerce-db"**
   - In the database dashboard, look for **"Connections"** section
   - Find **"Internal Database URL"** (NOT External Database URL)
   - Click the **copy button** 📋 next to the Internal URL
   - **Example format:** `postgresql://user:password@dpg-xxxxx-a:5432/database_name`

5. 🔗 **Add DATABASE_URL to your Web Service:**
   - Go back to your **web service** (ecommerce-api)
   - Click on **"Environment"** tab in the left sidebar
   - Click **"Add Environment Variable"**
   - **Key:** `DATABASE_URL`
   - **Value:** Paste the Internal Database URL you copied
   - Click **"Save Changes"**

#### **Step 6: Deploy & Setup**

1. 🚀 Click **"Deploy"** (takes 3-5 minutes)
2. 💻 Once deployed, go to **Shell** tab
3. 🗄️ Run database setup:
   ```bash
   python deploy.py
   python create_sample_data.py
   ```

#### **✅ Success! Your API is live at:**

`https://ecommerce-api.onrender.com`

---

## 🐍 **Option 2: PythonAnywhere (Python-Focused Platform)**

### ⏱️ **Deployment Time: 15-20 minutes**

#### **Step 1: Prepare Locally**

```bash
# Run the setup script
./deploy_pythonanywhere.sh
```

#### **Step 2: Setup PythonAnywhere Account**

1. 🌐 Go to [pythonanywhere.com](https://pythonanywhere.com)
2. 📝 Sign up for **free account**
3. ✅ Verify your email and login

#### **Step 3: Upload Your Code**

1. 💻 Open a **Bash console** from dashboard
2. 📥 Upload your code:
   ```bash
   git clone https://github.com/yourusername/ecommerce_api.git
   cd ecommerce_api
   ```

#### **Step 4: Setup Virtual Environment**

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### **Step 5: Setup MySQL Database**

1. 🗄️ Go to **"Databases"** tab in dashboard
2. ➕ Create database: `yourusername$ecommerce`
3. 📋 Note your **MySQL password** (you'll need it)

#### **Step 6: Configure Web App**

1. 🌐 Go to **"Web"** tab
2. ➕ **"Add a new web app"**
3. ⚙️ Choose **"Manual configuration"** → **Python 3.10**
4. 📁 Set source code: `/home/yourusername/ecommerce_api`
5. 🐍 Set virtualenv: `/home/yourusername/ecommerce_api/venv`

#### **Step 7: Update WSGI File**

1. 📝 Click on **WSGI configuration file**
2. 🗑️ **Delete all content**
3. 📋 **Copy content** from `pythonanywhere_wsgi.py`
4. ✏️ **Replace placeholders**:
   - `yourusername` → your actual username
   - `yourpassword` → your MySQL password
   - `your-secret-key-here` → generated SECRET_KEY
   - `your-jwt-secret-key-here` → generated JWT_SECRET_KEY

#### **Step 8: Setup Database**

```bash
# In your bash console
cd ecommerce_api
source venv/bin/activate
python deploy.py
python create_sample_data.py
```

#### **Step 9: Reload Web App**

1. 🔄 Go back to **"Web"** tab
2. 🟢 Click **"Reload yourusername.pythonanywhere.com"**

#### **✅ Success! Your API is live at:**

`https://yourusername.pythonanywhere.com`

---

## 🧪 **Testing Your Deployed API**

### **1. Health Check**

```bash
# For Render
curl https://ecommerce-api.onrender.com/ping

# For PythonAnywhere
curl https://yourusername.pythonanywhere.com/ping
```

### **2. API Info**

```bash
# For Render
curl https://ecommerce-api.onrender.com/api/v1

# For PythonAnywhere
curl https://yourusername.pythonanywhere.com/api/v1
```

### **3. Update Postman Collection**

1. 📖 Open your **Postman collection**
2. ⚙️ Go to **Variables**
3. 🔄 Update `base_url`:
   - **Render**: `https://ecommerce-api.onrender.com`
   - **PythonAnywhere**: `https://yourusername.pythonanywhere.com`

### **4. Test Authentication**

1. 🔐 **Login as admin**: `admin@example.com` / `admin123`
2. 🛒 **Test cart operations**
3. 📦 **Test product management**

---

## 🔧 **Platform Comparison**

| Feature             | Render          | PythonAnywhere     |
| ------------------- | --------------- | ------------------ |
| **Setup Time**      | 10-15 min       | 15-20 min          |
| **Database**        | PostgreSQL      | MySQL              |
| **SSL/HTTPS**       | ✅ Automatic    | ✅ Automatic       |
| **Custom Domain**   | ✅ Free         | ❌ Paid plans only |
| **Git Deploy**      | ✅ Automatic    | ❌ Manual upload   |
| **Free Tier**       | 750 hours/month | Limited but stable |
| **Python Versions** | 3.7-3.11        | 3.6-3.10           |
| **Ease of Use**     | ⭐⭐⭐⭐⭐      | ⭐⭐⭐⭐           |

---

## 🆘 **Troubleshooting**

### **Common Issues**

#### **🔥 FIXED: Gunicorn AppImportError**

**Error:** `Failed to find attribute 'app' in 'wsgi'`
**Solution:** ✅ **Already fixed in latest version!**

- Updated `wsgi.py` to include both `app` and `application` objects
- If you still get this error, make sure you've pushed the latest code to GitHub

#### **502 Bad Gateway**

- ✅ Check if `gunicorn wsgi:app` command is correct
- ✅ Verify all environment variables are set
- ✅ Check logs for Python errors
- ✅ Ensure your GitHub repository has the latest code

#### **Database Connection Error**

- ✅ Verify `DATABASE_URL` is correctly set
- ✅ Ensure database was created properly
- ✅ Check database credentials
- ✅ For Render: Use "Internal Database URL" not external URL

#### **Import Errors**

- ✅ Verify `requirements.txt` includes all dependencies
- ✅ Check Python version compatibility
- ✅ Ensure virtual environment is activated
- ✅ Make sure you've pushed all files to GitHub

#### **Environment Variables Not Set**

- ✅ Double-check all required environment variables are added:
  ```bash
  FLASK_ENV=production
  DEBUG=False
  SECRET_KEY=your-generated-secret-key
  JWT_SECRET_KEY=your-generated-jwt-key
  DATABASE_URL=your-database-url
  ```

#### **🗄️ Database Connection Issues**

**Error:** `could not connect to server`
**Solutions:**
- ✅ Make sure you used **Internal Database URL** (starts with `dpg-`)
- ✅ Verify database status is "Available" in Render dashboard
- ✅ Check that DATABASE_URL environment variable is set correctly
- ✅ Ensure web service and database are in the same region

**Error:** `database does not exist`
**Solutions:**
- ✅ Wait for database creation to complete (2-3 minutes)
- ✅ Refresh database dashboard and copy URL again
- ✅ Make sure you didn't accidentally modify the database name in URL

**Error:** `authentication failed`
**Solutions:**
- ✅ Copy the complete Internal Database URL including username and password
- ✅ Don't manually edit any part of the database URL
- ✅ Re-copy from Render dashboard if connection fails

### **Getting Help**

- **Render**: [render.com/docs](https://render.com/docs)
- **PythonAnywhere**: [help.pythonanywhere.com](https://help.pythonanywhere.com)

---

## 🎉 **Next Steps**

1. ✅ **Choose your platform** (Render is more modern, PythonAnywhere more Python-focused)
2. ✅ **Follow the step-by-step guide** above
3. ✅ **Test your deployed API** with Postman
4. ✅ **Share your API URL** for testing
5. ✅ **Build your frontend** app to consume the API

**Your e-commerce API is production-ready!** 🚀

Both platforms offer excellent free tiers perfect for development and small production deployments. Choose based on your preference for modern tooling (Render) or Python-specific features (PythonAnywhere).
