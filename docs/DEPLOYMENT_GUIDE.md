# 🚀 Helix-Zero: Complete Setup & Deployment Guide

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Local Development Setup](#2-local-development-setup)
3. [Running Locally](#3-running-locally)
4. [Free Deployment Options](#4-free-deployment-options)
5. [Deploy to Vercel (Recommended)](#5-deploy-to-vercel-recommended)
6. [Deploy to Netlify](#6-deploy-to-netlify)
7. [Deploy to GitHub Pages](#7-deploy-to-github-pages)
8. [Custom Domain Setup](#8-custom-domain-setup)
9. [Environment Variables & Security](#9-environment-variables--security)
10. [Monitoring & Analytics](#10-monitoring--analytics)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Prerequisites

### 1.1 Install Node.js (Required)

**Windows:**
1. Go to https://nodejs.org/
2. Download the **LTS version** (e.g., 20.x.x)
3. Run the installer
4. Check "Automatically install necessary tools"
5. Complete installation

**Mac:**
```bash
# Using Homebrew (recommended)
brew install node

# Or download from https://nodejs.org/
```

**Linux (Ubuntu/Debian):**
```bash
# Update package manager
sudo apt update

# Install Node.js 20.x
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Verify Installation:**
```bash
node --version    # Should show v20.x.x or higher
npm --version     # Should show 10.x.x or higher
```

### 1.2 Install Git (Required)

**Windows:**
1. Go to https://git-scm.com/download/win
2. Download and run installer
3. Use default settings
4. Select "Git from the command line and also from 3rd-party software"

**Mac:**
```bash
# Git comes with Xcode Command Line Tools
xcode-select --install

# Or using Homebrew
brew install git
```

**Linux:**
```bash
sudo apt update
sudo apt install git
```

**Verify Installation:**
```bash
git --version    # Should show git version 2.x.x
```

### 1.3 Install VS Code (Recommended)

1. Go to https://code.visualstudio.com/
2. Download for your OS
3. Install with default settings

**Recommended Extensions:**
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- Prettier - Code formatter
- TypeScript Importer

### 1.4 Create Accounts (For Deployment)

Create free accounts on these platforms:
- **GitHub**: https://github.com (Required)
- **Vercel**: https://vercel.com (Recommended for deployment)
- **Netlify**: https://netlify.com (Alternative)

---

## 2. Local Development Setup

### 2.1 Download/Clone the Project

**Option A: Download from your current project**

If you have the project files, copy them to a folder like:
```
C:\Projects\helix-zero\    (Windows)
~/Projects/helix-zero/     (Mac/Linux)
```

**Option B: Initialize a new project**

```bash
# Create project directory
mkdir helix-zero
cd helix-zero

# Initialize with Vite
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install
```

### 2.2 Project Structure

Your project should have this structure:
```
helix-zero/
├── public/
│   ├── HELIX_ZERO_WHITEPAPER.md
│   └── HELIX_ZERO_WHITEPAPER.html
├── src/
│   ├── lib/
│   │   ├── types.ts
│   │   ├── engine.ts
│   │   ├── bloomFilter.ts
│   │   └── genomeProcessor.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

### 2.3 Install Dependencies

Open terminal in project folder:

```bash
# Navigate to project folder
cd helix-zero

# Install all dependencies
npm install

# Install additional required packages
npm install recharts lucide-react
```

### 2.4 Verify package.json

Your `package.json` should include:
```json
{
  "name": "helix-zero",
  "version": "6.3.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "recharts": "^2.10.0",
    "lucide-react": "^0.300.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

---

## 3. Running Locally

### 3.1 Start Development Server

```bash
# In project directory
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
  ➜  press h + enter to show help
```

### 3.2 Open in Browser

1. Open your browser
2. Go to `http://localhost:5173/`
3. You should see the Helix-Zero application

### 3.3 Test the Application

1. Toggle "Load Demo Data" in sidebar
2. Click "INITIALIZE PROTOCOL"
3. Wait for analysis to complete
4. Verify all tabs work (Dashboard, Analytics, Ecology, Certificate)

### 3.4 Build for Production

```bash
# Create production build
npm run build
```

This creates a `dist/` folder with optimized files.

### 3.5 Preview Production Build

```bash
# Preview the production build locally
npm run preview
```

---

## 4. Free Deployment Options

| Platform | Free Tier | Best For | Custom Domain | SSL |
|----------|-----------|----------|---------------|-----|
| **Vercel** | 100GB/month | React apps | ✅ Free | ✅ Free |
| **Netlify** | 100GB/month | Static sites | ✅ Free | ✅ Free |
| **GitHub Pages** | Unlimited | Open source | ✅ Free | ✅ Free |
| **Cloudflare Pages** | Unlimited | Global CDN | ✅ Free | ✅ Free |
| **Render** | 100GB/month | Full stack | ✅ Free | ✅ Free |

**Recommendation:** Use **Vercel** for the easiest deployment experience.

---

## 5. Deploy to Vercel (Recommended)

### 5.1 Push to GitHub First

**Step 1: Create GitHub Repository**

1. Go to https://github.com/new
2. Repository name: `helix-zero`
3. Description: `Regulatory-Grade RNA Interference Design Engine`
4. Set to **Public** or **Private**
5. Click "Create repository"

**Step 2: Initialize Git & Push**

```bash
# In your project directory
cd helix-zero

# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Helix-Zero v6.3"

# Add remote origin (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/helix-zero.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 5.2 Deploy to Vercel

**Method 1: Using Vercel Dashboard (Easiest)**

1. Go to https://vercel.com/
2. Click "Sign Up" → "Continue with GitHub"
3. Authorize Vercel
4. Click "Add New..." → "Project"
5. Select "Import Git Repository"
6. Find and select `helix-zero`
7. Configure project:
   - **Framework Preset:** Vite
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
8. Click "Deploy"
9. Wait 1-2 minutes for deployment

**Method 2: Using Vercel CLI**

```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Deploy (in project directory)
vercel

# Follow prompts:
# ? Set up and deploy? Yes
# ? Which scope? Select your account
# ? Link to existing project? No
# ? Project name? helix-zero
# ? Directory? ./
# ? Override settings? No

# For production deployment
vercel --prod
```

### 5.3 Your Live URL

After deployment, you'll get URLs like:
- **Production:** `https://helix-zero.vercel.app`
- **Preview:** `https://helix-zero-xxx-username.vercel.app`

### 5.4 Auto-Deploy on Git Push

Vercel automatically deploys when you push to GitHub:
```bash
# Make changes to code
git add .
git commit -m "Update: Added new feature"
git push origin main

# Vercel automatically detects and deploys!
```

---

## 6. Deploy to Netlify

### 6.1 Using Netlify Dashboard

1. Go to https://app.netlify.com/
2. Sign up/Login with GitHub
3. Click "Add new site" → "Import an existing project"
4. Choose "GitHub"
5. Select `helix-zero` repository
6. Configure build settings:
   - **Build command:** `npm run build`
   - **Publish directory:** `dist`
7. Click "Deploy site"

### 6.2 Using Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Initialize site
netlify init

# Build and deploy
npm run build
netlify deploy --prod --dir=dist
```

### 6.3 Netlify Configuration

Create `netlify.toml` in project root:
```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

---

## 7. Deploy to GitHub Pages

### 7.1 Update vite.config.ts

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/helix-zero/', // Your repository name
})
```

### 7.2 Install gh-pages

```bash
npm install -D gh-pages
```

### 7.3 Update package.json

Add these scripts:
```json
{
  "scripts": {
    "predeploy": "npm run build",
    "deploy": "gh-pages -d dist"
  }
}
```

### 7.4 Deploy

```bash
# Build and deploy to GitHub Pages
npm run deploy
```

### 7.5 Enable GitHub Pages

1. Go to your repository on GitHub
2. Settings → Pages
3. Source: "Deploy from a branch"
4. Branch: `gh-pages` / `root`
5. Save

Your site will be at: `https://YOUR_USERNAME.github.io/helix-zero/`

---

## 8. Custom Domain Setup

### 8.1 Buy a Domain

Recommended registrars:
- **Namecheap:** https://namecheap.com (~$10/year for .com)
- **Google Domains:** https://domains.google (~$12/year)
- **Cloudflare Registrar:** https://cloudflare.com/products/registrar/
- **GoDaddy:** https://godaddy.com

Example domains:
- `helix-zero.com`
- `helix-zero.io`
- `helixzero.bio`

### 8.2 Configure DNS on Vercel

1. Go to Vercel Dashboard → Your Project
2. Settings → Domains
3. Add your domain: `helix-zero.com`
4. Vercel provides DNS records

**Add these records at your registrar:**

| Type | Name | Value |
|------|------|-------|
| A | @ | 76.76.21.21 |
| CNAME | www | cname.vercel-dns.com |

### 8.3 Configure DNS on Netlify

1. Netlify Dashboard → Site settings → Domain management
2. Add custom domain
3. Add DNS records at your registrar:

| Type | Name | Value |
|------|------|-------|
| A | @ | 104.198.14.52 |
| CNAME | www | your-site.netlify.app |

### 8.4 SSL Certificate

Both Vercel and Netlify provide **free SSL certificates** automatically!
- Your site will be accessible via `https://`
- Certificate renews automatically

---

## 9. Environment Variables & Security

### 9.1 For Future API Keys

If you add NCBI API, OpenAI, or other services:

**Local Development (.env.local):**
```bash
# Create .env.local file (never commit this!)
VITE_NCBI_API_KEY=your_api_key_here
VITE_APP_VERSION=6.3.0
```

**Access in Code:**
```typescript
const apiKey = import.meta.env.VITE_NCBI_API_KEY;
```

**Add to .gitignore:**
```
.env.local
.env.*.local
```

### 9.2 Set Environment Variables on Vercel

1. Project Settings → Environment Variables
2. Add variables:
   - Name: `VITE_NCBI_API_KEY`
   - Value: `your_api_key`
   - Environment: Production, Preview, Development
3. Redeploy for changes to take effect

### 9.3 Set Environment Variables on Netlify

1. Site settings → Build & deploy → Environment
2. Add environment variables
3. Redeploy

---

## 10. Monitoring & Analytics

### 10.1 Vercel Analytics (Free)

1. Project → Analytics tab
2. Enable Web Analytics
3. Add to your app:

```bash
npm install @vercel/analytics
```

```typescript
// In main.tsx
import { Analytics } from '@vercel/analytics/react';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
    <Analytics />
  </React.StrictMode>
);
```

### 10.2 Google Analytics (Free)

1. Go to https://analytics.google.com/
2. Create account and property
3. Get Measurement ID (G-XXXXXXXXXX)
4. Add to `index.html`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### 10.3 Uptime Monitoring (Free)

- **UptimeRobot:** https://uptimerobot.com/ (50 monitors free)
- **Freshping:** https://freshping.io/ (50 monitors free)

Setup:
1. Create account
2. Add monitor → HTTP(s)
3. URL: `https://helix-zero.vercel.app`
4. Check interval: 5 minutes
5. Get alerts via email/Slack

---

## 11. Troubleshooting

### 11.1 Build Errors

**Error: "Cannot find module"**
```bash
# Clear node_modules and reinstall
rm -rf node_modules
rm package-lock.json
npm install
```

**Error: TypeScript errors**
```bash
# Check for type errors
npx tsc --noEmit

# Fix common issues
npm install --save-dev @types/react @types/react-dom
```

**Error: "vite not found"**
```bash
npm install vite --save-dev
```

### 11.2 Deployment Errors

**Vercel: Build failed**
1. Check build logs in Vercel dashboard
2. Ensure `npm run build` works locally
3. Check for case-sensitive import paths (Linux is strict!)

**Netlify: Deploy failed**
1. Check deploy logs
2. Verify publish directory is `dist`
3. Check `netlify.toml` configuration

### 11.3 Blank Page After Deploy

**Fix for React Router / SPA:**

Create `public/_redirects` (for Netlify):
```
/*    /index.html   200
```

Or `vercel.json` (for Vercel):
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### 11.4 Large File Upload Errors

If users report errors with large files:
1. Increase chunk size in `genomeProcessor.ts`
2. Consider implementing server-side processing
3. Add file size warnings in UI

### 11.5 CORS Errors (If Adding APIs)

Add to `vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'https://api.ncbi.nlm.nih.gov',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

---

## Quick Reference Commands

```bash
# Development
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build

# Git
git add .
git commit -m "message"
git push origin main

# Vercel
vercel               # Deploy preview
vercel --prod        # Deploy production

# Netlify
netlify deploy --prod --dir=dist

# GitHub Pages
npm run deploy
```

---

## Support & Resources

- **Vite Documentation:** https://vitejs.dev/
- **React Documentation:** https://react.dev/
- **Tailwind CSS:** https://tailwindcss.com/docs
- **Vercel Docs:** https://vercel.com/docs
- **Netlify Docs:** https://docs.netlify.com/

---

## Next Steps After Deployment

1. ✅ Share your live URL
2. ✅ Set up custom domain
3. ✅ Add analytics
4. ✅ Set up uptime monitoring
5. ✅ Create social media preview image
6. ✅ Submit to search engines
7. ✅ Gather user feedback
8. ✅ Plan Phase 2 features (Deep Learning integration)

---

**Congratulations! 🎉**

Your Helix-Zero platform is now live and accessible worldwide!

For support: Contact your development team or open an issue on GitHub.

---

*Document Version: 1.0*
*Last Updated: 2025*
*Author: Helix-Zero Development Team*
