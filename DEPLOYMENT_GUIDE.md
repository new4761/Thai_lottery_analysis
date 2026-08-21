# 🚀 Deployment Guide - Thai Lottery Generator

Complete guide to deploy the enhanced lottery generator to new4761.github.io

## 📋 What's Being Deployed

1. **Enhanced Number Generator** (3 modes)
   - Pure Random, Data-Driven, Thai-Aware
   - Web-ready (HTML + JavaScript)
   - No external dependencies

2. **Historical Data API**
   - Serves hot/cold numbers
   - Provides statistics
   - Detects Thai holidays

3. **GitHub Actions Workflow**
   - Auto-syncs new data
   - Deploys to GitHub Pages
   - Runs tests on every update

---

## 🔧 Setup Instructions

### Step 1: Clone Both Repositories

```bash
# Clone the data analysis repo
git clone https://github.com/new4761/Thai_lottery_analysis.git
cd Thai_lottery_analysis

# Clone your GitHub Pages repo
git clone https://github.com/new4761/new4761.github.io.git ../new4761.github.io
```

### Step 2: Copy Files to Your Site

```bash
# Copy generator files
cp lottery_generator_ui.html ../new4761.github.io/tools/lottery/
cp lottery_generator_web.js ../new4761.github.io/tools/lottery/

# Replace the existing index.html with the new UI
# Or integrate into existing page (see Integration section)
```

### Step 3: Deploy API Server

Choose one platform:

#### Option A: Heroku (Recommended for simplicity)

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create new app
heroku create thai-lottery-api

# Add buildpack
heroku buildpacks:add heroku/python

# Deploy
git push heroku main

# Check logs
heroku logs --tail
```

#### Option B: Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

#### Option C: Render

1. Push to GitHub
2. Go to https://render.com
3. Create new "Web Service"
4. Connect GitHub repo
5. Set Start Command: `python api_server.py`
6. Deploy

#### Option D: Self-Hosted (Your Own Server)

```bash
# Install dependencies
pip install flask flask-cors flask-caching

# Run server
python api_server.py

# Use systemd or Docker to keep it running
```

### Step 4: Update HTML with API URL

Edit `lottery_generator_ui.html`:

```javascript
// Before:
let generator = new ThaiLotteryGenerator();

// After:
const API_URL = 'https://your-api-domain.com/api/history';
let historicalData = null;

// Fetch historical data
fetch(API_URL)
  .then(res => res.json())
  .then(data => {
    historicalData = data.data;
    let generator = new ThaiLotteryGenerator(historicalData);
  });
```

### Step 5: Integrate into Existing Page

If you want to add to existing page (not replace):

```html
<!-- Add these to your page -->
<div id="lottery-generator"></div>

<script src="lottery_generator_web.js"></script>
<script>
  fetch('api/history')
    .then(r => r.json())
    .then(data => {
      const gen = new ThaiLotteryGenerator(data.data);
      // Wire up to your UI
    });
</script>
```

---

## 📁 File Structure

```
new4761.github.io/
├── tools/
│   └── lottery/
│       ├── index.html (updated with generator)
│       ├── lottery_generator_web.js (new)
│       └── lottery_generator_ui.html (alternative)
```

---

## 🌐 API Endpoints

Once deployed, these endpoints are available:

### `/api/info`
Get generator info and data overview
```bash
curl https://your-api.com/api/info
```

Response:
```json
{
  "generator": {...},
  "data": {
    "total_draws": 360,
    "start_date": "2010-03-01",
    "end_date": "2026-08-16",
    "years_covered": 16
  }
}
```

### `/api/history`
Get hot/cold numbers from 3-year analysis
```bash
curl https://your-api.com/api/history
```

Response:
```json
{
  "data": {
    "first": {
      "hot": ["100001", "200002", ...],
      "cold": ["999999", "888888", ...],
      "total_appearances": 1500
    },
    ...
  }
}
```

### `/api/stats`
Get statistical analysis
```bash
curl https://your-api.com/api/stats
```

### `/api/today`
Get today's context (holidays, luck)
```bash
curl https://your-api.com/api/today
```

### `/api/generate?mode=pure`
Generate numbers (pure, driven, or thai)
```bash
curl https://your-api.com/api/generate?mode=data_driven
```

### `/health`
Health check
```bash
curl https://your-api.com/health
```

---

## 🔄 GitHub Actions Workflow

Create `.github/workflows/deploy.yml` in Thai_lottery_analysis repo:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 8 3,17 * *'  # Every 3rd & 17th at 8am

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run tests
        run: python -m unittest discover -s tests -v

      - name: Checkout GitHub Pages repo
        uses: actions/checkout@v3
        with:
          repository: new4761/new4761.github.io
          path: site
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Copy files to site
        run: |
          cp lottery_generator_ui.html site/tools/lottery/
          cp lottery_generator_web.js site/tools/lottery/

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          deploy_key: ${{ secrets.DEPLOY_KEY }}
          external_repository: new4761/new4761.github.io
          publish_dir: ./site

      - name: Deploy API to Heroku
        run: |
          git remote add heroku https://git.heroku.com/thai-lottery-api.git
          git push heroku main
        env:
          HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
```

---

## 🧪 Testing Locally

Before deploying:

```bash
# Test API server
python api_server.py
# Visit http://localhost:5000/api/info

# Test generator
python lottery_generator.py

# Test UI locally
# Open lottery_generator_ui.html in browser
# Or start local server:
python -m http.server 8000
# Visit http://localhost:8000/lottery_generator_ui.html
```

---

## 📊 Environment Variables

Set these for deployed API:

```bash
# Heroku
heroku config:set FLASK_ENV=production

# Railway / Render (set in dashboard)
FLASK_ENV=production
PORT=5000  # or whatever port they assign
```

---

## 🔐 Security Considerations

1. **API Rate Limiting**
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=lambda: request.remote_addr)
   
   @app.route('/api/generate')
   @limiter.limit("10 per minute")
   def api_generate():
       ...
   ```

2. **CORS Headers** (already enabled)
   - `Access-Control-Allow-Origin: *`

3. **Cache Control**
   - Historical data cached for 1 hour
   - Update frequency: Every 3rd & 17th month

---

## 📈 Monitoring

Once deployed, monitor:

1. **API Uptime**
   - Health check: `GET /health`
   - Add to uptime monitor (UptimeRobot, etc.)

2. **Performance**
   - API response time should be <500ms
   - Cache hit ratio should be >80%

3. **Errors**
   - Monitor logs via Heroku/Railway dashboard
   - Set up error alerts (Sentry, etc.)

---

## 🎯 Verification Checklist

- [ ] Files copied to GitHub Pages repo
- [ ] API server deployed and running
- [ ] `/api/health` returns 200 OK
- [ ] `/api/history` returns valid data
- [ ] Generator UI loads without errors
- [ ] All 3 modes (Pure, Data-Driven, Thai) work
- [ ] CI workflow running successfully
- [ ] CORS working (test from different domain)
- [ ] Historical data updating automatically

---

## 🚨 Troubleshooting

### API not responding
```bash
# Check if API is running
curl https://your-api.com/health

# Check logs
heroku logs --tail  # if using Heroku
```

### Generator not loading
1. Check browser console for errors
2. Verify `lottery_generator_web.js` is accessible
3. Check if API URL is correct

### Data not updating
1. Check if GitHub Actions workflow is running
2. Verify data pipeline is working
3. Check API cache (wait 1 hour or clear cache)

### CORS errors
1. Ensure API has CORS headers enabled
2. Check domain whitelist in Flask app
3. Browser may cache CORS preflight, try private mode

---

## 📞 Support

For issues:
1. Check GitHub Actions logs
2. Check API server logs
3. Review error messages in browser console
4. Check data_analysis.py for data issues

---

## 🎉 Success!

Once deployed, your site will have:
- ✅ 3 different lottery number generation modes
- ✅ Data-driven numbers based on 360+ real draws
- ✅ Thai cultural awareness (holidays, lucky numbers)
- ✅ Auto-updating data pipeline
- ✅ Historical analytics API
- ✅ Beautiful, responsive UI

Enjoy! 🎰
