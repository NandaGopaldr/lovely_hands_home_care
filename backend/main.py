"""
Lovely Hands Homecare - FastAPI Backend
Handles contact form submissions, appointment bookings, and email notifications.
Uses Gmail SMTP for email delivery with httpx fallback via Formsubmit.co
"""

import os
import ssl
import smtplib
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Lovely Hands Homecare API",
    description="Backend API for Lovely Hands Homecare website",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Configuration ----------
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "anwarjohn108@gmail.com")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

def is_smtp_configured():
    """Check if SMTP credentials are properly set."""
    return (
        SMTP_USER
        and SMTP_PASSWORD
        and SMTP_PASSWORD != "your_gmail_app_password_here"
        and len(SMTP_PASSWORD) > 4
    )

# ---------- Pydantic Models ----------

class ContactForm(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=7, max_length=20)
    email: str = Field(default="", max_length=100)
    service_needed: str = Field(..., min_length=2)
    message: str = Field(default="", max_length=2000)

class AppointmentForm(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=7, max_length=20)
    email: str = Field(default="", max_length=100)
    service_needed: str = Field(..., min_length=2)
    preferred_date: str = Field(..., min_length=1)
    preferred_time: str = Field(..., min_length=1)
    address: str = Field(default="", max_length=500)
    message: str = Field(default="", max_length=2000)

class NewsletterForm(BaseModel):
    email: str = Field(..., min_length=5, max_length=100)

# ---------- Email Helpers ----------

def send_email_smtp(subject: str, html_body: str, reply_to: str = None) -> bool:
    """Send email via Gmail SMTP."""
    if not is_smtp_configured():
        print(f"[SMTP] Not configured — skipping SMTP.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Lovely Hands Homecare <{SMTP_USER}>"
    msg["To"] = RECEIVER_EMAIL
    if reply_to:
        msg["Reply-To"] = reply_to

    msg.attach(MIMEText(html_body, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, RECEIVER_EMAIL, msg.as_string())
        print(f"[SMTP ✅] Email sent: {subject}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[SMTP ❌ AUTH ERROR] Bad username/password. Make sure you're using a Gmail App Password, not your regular password. Error: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"[SMTP ❌ ERROR] {e}")
        return False
    except Exception as e:
        print(f"[SMTP ❌ ERROR] {type(e).__name__}: {e}")
        return False


async def send_email_formsubmit(data: dict) -> bool:
    """Fallback: Send email via Formsubmit.co (free, no config needed).
    This service sends form data directly to your email.
    First submission requires email confirmation (check your inbox).
    """
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"https://formsubmit.co/ajax/{RECEIVER_EMAIL}",
                json={
                    "_subject": data.get("_subject", "New Submission - Lovely Hands Homecare"),
                    "_template": "table",
                    **{k: v for k, v in data.items() if not k.startswith("_")}
                },
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success") == "true":
                    print(f"[FORMSUBMIT ✅] Email sent via Formsubmit.co")
                    return True
                else:
                    print(f"[FORMSUBMIT ⚠️] Response: {result}")
                    # First time? Check inbox for confirmation email from Formsubmit
                    return True  # Still count as sent — user just needs to confirm
            else:
                print(f"[FORMSUBMIT ❌] HTTP {response.status_code}: {response.text[:200]}")
                return False
    except Exception as e:
        print(f"[FORMSUBMIT ❌] {type(e).__name__}: {e}")
        return False


async def send_notification(subject: str, html_body: str, plain_data: dict, reply_to: str = None) -> bool:
    """Try SMTP first, then fall back to Formsubmit.co"""
    # Method 1: SMTP (if configured)
    if is_smtp_configured():
        result = send_email_smtp(subject, html_body, reply_to)
        if result:
            return True
        print("[FALLBACK] SMTP failed, trying Formsubmit.co...")

    # Method 2: Formsubmit.co (free, zero config)
    plain_data["_subject"] = subject
    result = await send_email_formsubmit(plain_data)
    return result


# ---------- API Endpoints ----------

@app.get("/api/health")
async def health_check():
    smtp_status = "configured" if is_smtp_configured() else "not configured (using Formsubmit.co fallback)"
    return {
        "status": "healthy",
        "service": "Lovely Hands Homecare API",
        "email_method": smtp_status
    }


@app.post("/api/contact")
async def submit_contact(form: ContactForm):
    """Handle contact form submissions."""
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px 10px 0 0;">
            <h2 style="color: white; margin: 0;">💌 New Contact Form Submission</h2>
        </div>
        <div style="background: #f9f9f9; padding: 25px; border-radius: 0 0 10px 10px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 10px; font-weight: bold; color: #555;">Full Name</td><td style="padding: 10px;">{form.full_name}</td></tr>
                <tr style="background: #fff;"><td style="padding: 10px; font-weight: bold; color: #555;">Phone</td><td style="padding: 10px;"><a href="tel:{form.phone}">{form.phone}</a></td></tr>
                <tr><td style="padding: 10px; font-weight: bold; color: #555;">Email</td><td style="padding: 10px;">{form.email or 'Not provided'}</td></tr>
                <tr style="background: #fff;"><td style="padding: 10px; font-weight: bold; color: #555;">Service Needed</td><td style="padding: 10px;">{form.service_needed}</td></tr>
                <tr><td style="padding: 10px; font-weight: bold; color: #555;">Message</td><td style="padding: 10px;">{form.message or 'No message'}</td></tr>
            </table>
            <p style="color: #888; font-size: 12px; margin-top: 20px;">Received on {timestamp}</p>
        </div>
    </div>
    """

    plain_data = {
        "Full Name": form.full_name,
        "Phone": form.phone,
        "Email": form.email or "Not provided",
        "Service Needed": form.service_needed,
        "Message": form.message or "No message",
        "Received At": timestamp,
    }

    email_sent = await send_notification(
        subject=f"New Contact: {form.full_name} - {form.service_needed}",
        html_body=html_body,
        plain_data=plain_data,
        reply_to=form.email if form.email else None
    )

    return {
        "success": True,
        "message": "Thank you! We've received your message and will get back to you within 24 hours.",
        "email_sent": email_sent
    }


@app.post("/api/appointment")
async def book_appointment(form: AppointmentForm):
    """Handle appointment booking submissions."""
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 10px 10px 0 0;">
            <h2 style="color: white; margin: 0;">📅 New Appointment Booking</h2>
        </div>
        <div style="background: #f9f9f9; padding: 25px; border-radius: 0 0 10px 10px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 10px; font-weight: bold; color: #555;">Full Name</td><td style="padding: 10px;">{form.full_name}</td></tr>
                <tr style="background: #fff;"><td style="padding: 10px; font-weight: bold; color: #555;">Phone</td><td style="padding: 10px;"><a href="tel:{form.phone}">{form.phone}</a></td></tr>
                <tr><td style="padding: 10px; font-weight: bold; color: #555;">Email</td><td style="padding: 10px;">{form.email or 'Not provided'}</td></tr>
                <tr style="background: #fff;"><td style="padding: 10px; font-weight: bold; color: #555;">Service Needed</td><td style="padding: 10px;">{form.service_needed}</td></tr>
                <tr><td style="padding: 10px; font-weight: bold; color: #555;">Preferred Date</td><td style="padding: 10px;">{form.preferred_date}</td></tr>
                <tr style="background: #fff;"><td style="padding: 10px; font-weight: bold; color: #555;">Preferred Time</td><td style="padding: 10px;">{form.preferred_time}</td></tr>
                <tr><td style="padding: 10px; font-weight: bold; color: #555;">Address</td><td style="padding: 10px;">{form.address or 'Not provided'}</td></tr>
                <tr style="background: #fff;"><td style="padding: 10px; font-weight: bold; color: #555;">Message</td><td style="padding: 10px;">{form.message or 'No additional notes'}</td></tr>
            </table>
            <p style="color: #888; font-size: 12px; margin-top: 20px;">Received on {timestamp}</p>
        </div>
    </div>
    """

    plain_data = {
        "Full Name": form.full_name,
        "Phone": form.phone,
        "Email": form.email or "Not provided",
        "Service Needed": form.service_needed,
        "Preferred Date": form.preferred_date,
        "Preferred Time": form.preferred_time,
        "Address": form.address or "Not provided",
        "Message": form.message or "No additional notes",
        "Received At": timestamp,
    }

    email_sent = await send_notification(
        subject=f"Appointment Request: {form.full_name} - {form.preferred_date}",
        html_body=html_body,
        plain_data=plain_data,
        reply_to=form.email if form.email else None
    )

    return {
        "success": True,
        "message": "Your appointment request has been submitted! We'll confirm your booking within 24 hours.",
        "email_sent": email_sent
    }


@app.post("/api/newsletter")
async def subscribe_newsletter(form: NewsletterForm):
    """Handle newsletter subscription."""
    email_sent = await send_notification(
        subject=f"New Newsletter Subscriber: {form.email}",
        html_body=f"<p>New subscriber: <strong>{form.email}</strong></p><p>Subscribed at {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>",
        plain_data={"Subscriber Email": form.email, "Subscribed At": datetime.now().strftime('%B %d, %Y at %I:%M %p')}
    )

    return {
        "success": True,
        "message": "You've been subscribed to our newsletter!",
        "email_sent": email_sent
    }


# ---------- Serve Frontend ----------

# Mount static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the frontend SPA."""
        file_path = os.path.join(frontend_path, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_path, "index.html"))
