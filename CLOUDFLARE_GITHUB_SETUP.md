# GitHub Pages + Cloudflare Setup

## Current Setup
✅ **GitHub Actions** → Weekly scraping + JSON generation
✅ **GitHub Pages** → Hosts the static HTML site
➡️ **Cloudflare** → CDN, SSL, custom domain

## Step 1: Enable GitHub Pages
1. Go to your repository: **Settings → Pages**
2. **Source**: "Deploy from a branch"
3. **Branch**: `gh-pages` (this will be created automatically)
4. **Folder**: `/ (root)`
5. **Save**

## Step 2: Set Up Cloudflare
1. **Add your domain** to Cloudflare (if not already done)
2. Go to **DNS settings**
3. **Add CNAME record**:
   - **Name**: `www` (or your subdomain)
   - **Target**: `spergel.github.io`
   - **TTL**: Auto

4. **Page Rules** (optional for performance):
   - **URL**: `https://yourdomain.com/*`
   - **Setting**: "Cache Level" → "Cache Everything"
   - **Edge Cache TTL**: 1 hour

## Step 3: Custom Domain (Optional)
To use a custom domain instead of `spergel.github.io`:

1. In GitHub Pages settings:
   - **Custom domain**: `events.princeton.edu` (or your domain)
   - **Save**

2. In Cloudflare DNS:
   - **Add CNAME**: `events.princeton.edu` → `jsper.github.io`

## URLs After Setup

- **GitHub Pages**: `https://jsper.github.io/princeton_academic_events`
- **Custom Domain + Cloudflare**: `https://events.princeton.edu` (if you set up custom domain)

## Benefits

✅ **GitHub Pages**: Free, easy deployment, automatic SSL
✅ **Cloudflare**: Global CDN, faster loading, DDoS protection
✅ **Weekly Updates**: Automatic scraping every Sunday
✅ **No Cost**: Both services have generous free tiers

## Testing

After setup, your site will be available at:
`https://jsper.github.io/princeton_academic_events`

With Cloudflare, it will be even faster worldwide!
