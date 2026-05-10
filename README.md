# 🛍️ Etsy Seller OS

An AI-powered Etsy analytics dashboard built with Streamlit.

Upload your Etsy CSV export → get instant insights, charts, and AI recommendations.

## Features
- 📊 Dark mode dashboard with KPI cards & shop health score
- 📦 Product performance with Bestseller / Scaling / Weak / Dead badges
- 💡 AI insights panel with plain-English recommendations
- 📈 Traffic & conversion analytics
- 💰 Profit leak detector
- 🚀 Growth opportunity generator
- 📱 Mobile responsive

## Deploy on Streamlit Cloud (free)

1. Fork this repo on GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your fork
4. Set **Main file path** to `app.py`
5. Click **Deploy** — live in ~60 seconds

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Using your Etsy CSV

1. Go to **Etsy → Shop Manager → Orders**
2. Click **Download CSV**
3. Upload the file on the app's landing page

The app auto-detects Etsy's column names and handles messy exports gracefully.

## Free Deployment Options

| Platform | URL | Notes |
|---|---|---|
| Streamlit Cloud | share.streamlit.io | 100% free, GitHub connect |
| Render | render.com | Free tier available |
| Railway | railway.app | $5 free credits/month |
| Hugging Face Spaces | huggingface.co/spaces | Free, Streamlit supported |

## Folder Structure

```
etsy-seller-os/
├── app.py                 ← Main Streamlit app
├── requirements.txt       ← Python dependencies
├── README.md
└── .streamlit/
    └── config.toml        ← Dark theme config
```
