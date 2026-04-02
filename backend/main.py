"""
Lovely Hands Homecare - FastAPI Backend
Handles contact form submissions, appointment bookings, and email notifications.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field
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

# ---------- Email Helper ----------

def send_email(subject: str, html_body: str, reply_to: str = None):
    """Send email notification via SMTP."""
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    receiver_email = os.getenv("RECEIVER_EMAIL", smtp_user)

    if not smtp_user or not smtp_password or smtp_password == "your_gmail_app_password_here":
        print(f"[EMAIL SKIPPED] SMTP not configured. Subject: {subject}")
        print(f"[EMAIL BODY]\n{html_body}")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Lovely Hands Homecare <{smtp_user}>"
    msg["To"] = receiver_email
    if reply_to:
        msg["Reply-To"] = reply_to

    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, receiver_email, msg.as_string())
        print(f"[EMAIL SENT] {subject}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


# ---------- API Endpoints ----------

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Lovely Hands Homecare API"}


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

    email_sent = send_email(
        subject=f"🏥 New Contact: {form.full_name} - {form.service_needed}",
        html_body=html_body,
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

    email_sent = send_email(
        subject=f"📅 Appointment Request: {form.full_name} - {form.preferred_date}",
        html_body=html_body,
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
    email_sent = send_email(
        subject=f"📬 New Newsletter Subscriber: {form.email}",
        html_body=f"<p>New subscriber: <strong>{form.email}</strong></p><p>Subscribed at {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>"
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
