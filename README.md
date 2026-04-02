# Lovely Hands Homecare 💖

> **Caring With Love, Healing With Gentle Hands**

A professional healthcare website with a FastAPI backend for contact forms, appointment bookings, and email notifications.

## 📁 Project Structure

```
lovely_hands_home_care/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables (SMTP config)
│   └── .env.example         # Example environment config
├── frontend/
│   ├── index.html           # Main HTML page
│   └── assets/
│       ├── style.css         # Stylesheet
│       ├── app.js            # Frontend JavaScript
│       └── images/           # Website images
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Email (Optional)
Edit `backend/.env` with your Gmail App Password:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=anwarjohn108@gmail.com
SMTP_PASSWORD=your_gmail_app_password
RECEIVER_EMAIL=anwarjohn108@gmail.com
```

> **How to get a Gmail App Password:**
> 1. Go to [Google Account Settings](https://myaccount.google.com/)
> 2. Enable 2-Step Verification
> 3. Go to Security → App Passwords
> 4. Generate a new app password for "Mail"
> 5. Paste the 16-character password in `.env`

### 3. Run the Server
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Visit the Website
Open [http://localhost:8000](http://localhost:8000) in your browser.

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/contact` | POST | Submit contact form |
| `/api/appointment` | POST | Book an appointment |
| `/api/newsletter` | POST | Subscribe to newsletter |

## 🌐 Deployment

### Free Hosting Options
- **Render.com** — Free tier with Python support
- **Railway.app** — Free starter plan
- **Vercel** — Free for frontend (use separate API)

### Deploy to Render
1. Push code to GitHub
2. Create a new Web Service on [render.com](https://render.com)
3. Connect your GitHub repo
4. Set build command: `pip install -r backend/requirements.txt`
5. Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables from `.env`

## 📞 Contact
- **Phone:** +1 (720) 505-9559
- **Email:** anwarjohn108@gmail.com
- **Location:** 1169 South Alton Court, Denver, CO 80247

---

© 2026 Lovely Hands Homecare. All rights reserved.
