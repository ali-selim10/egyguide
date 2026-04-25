from flask import Flask, request, redirect, url_for, session, render_template_string, make_response, jsonify
from supabase import create_client
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-to-a-random-secret")

# ── Supabase client ───────────────────────────────────────────────────────────
SUPABASE_URL = "https://wfmijhnvzhndjwjpidiw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndmbWlqaG52emhuZGp3anBpZGl3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM0NDU1NTUsImV4cCI6MjA4OTAyMTU1NX0.wAWgUlP5drEYy1CmTvjI-86JeHmA8PSrWL2osFpxc1A"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Email (Flask-Mail via Gmail SMTP) ─────────────────────────────────────────
# Set these environment variables on your server / .env file:
#   MAIL_USERNAME  = your Gmail address  (e.g. EgyGuide.egypt@gmail.com)
#   MAIL_PASSWORD  = Gmail App Password  (NOT your regular password)
#
# How to get a Gmail App Password:
#   1. Enable 2-Step Verification on your Google account
#   2. Go to  myaccount.google.com/apppasswords
#   3. Create an App Password for "Mail" → copy the 16-char password
#   4. Set it as  MAIL_PASSWORD  environment variable
#
# Install Flask-Mail:  pip install Flask-Mail

from flask_mail import Mail, Message

app.config["MAIL_SERVER"]   = "smtp.gmail.com"
app.config["MAIL_PORT"]     = 587
app.config["MAIL_USE_TLS"]  = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "")   # your Gmail
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")   # Gmail App Password
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME", "noreply@EgyGuide.eg")

mail = Mail(app)


def read_html(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# ── Email helper ──────────────────────────────────────────────────────────────
def send_booking_email(to_email, full_name, booking):
    """Send a beautiful HTML booking confirmation email."""
    check_in  = booking["check_in"]
    check_out = booking["check_out"]
    nights    = booking["nights"]
    total     = booking["total"]
    room      = booking["room_name"]
    hotel     = booking["hotel_name"]
    ref       = booking.get("booking_id", "SKK-" + str(booking.get("id", ""))[:6].upper())

    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <style>
    body {{ margin:0; padding:0; background:#f5f3ef; font-family:'Helvetica Neue',Arial,sans-serif; }}
    .wrapper {{ max-width:600px; margin:40px auto; background:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 4px 24px rgba(0,0,0,0.08); }}
    .header {{ background:linear-gradient(135deg,#00556f 0%,#1c6e8c 100%); padding:48px 40px 40px; text-align:center; }}
    .header h1 {{ color:#ffffff; font-size:28px; font-weight:800; margin:0 0 4px; letter-spacing:-0.5px; }}
    .header p {{ color:rgba(255,255,255,0.8); font-size:14px; margin:0; }}
    .check-icon {{ width:56px; height:56px; background:rgba(255,255,255,0.15); border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 20px; }}
    .body {{ padding:40px; }}
    .greeting {{ font-size:18px; font-weight:700; color:#1a1c1a; margin-bottom:8px; }}
    .subtext {{ font-size:14px; color:#685d46; margin-bottom:32px; line-height:1.6; }}
    .card {{ background:#f5f3ef; border-radius:12px; padding:28px; margin-bottom:28px; }}
    .card-title {{ font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:#685d46; margin-bottom:16px; }}
    .row {{ display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid #e4e2de; }}
    .row:last-child {{ border-bottom:none; }}
    .row-label {{ font-size:13px; color:#685d46; }}
    .row-value {{ font-size:13px; font-weight:700; color:#1a1c1a; }}
    .total-row {{ padding-top:16px; margin-top:8px; border-top:2px solid #00556f; }}
    .total-label {{ font-size:15px; font-weight:800; color:#1a1c1a; }}
    .total-value {{ font-size:20px; font-weight:800; color:#00556f; }}
    .ref-badge {{ text-align:center; margin-bottom:28px; }}
    .ref-badge span {{ background:#00556f; color:#ffffff; font-size:12px; font-weight:700; padding:6px 16px; border-radius:999px; letter-spacing:0.06em; }}
    .footer {{ background:#f5f3ef; padding:28px 40px; text-align:center; border-top:1px solid #e4e2de; }}
    .footer p {{ font-size:12px; color:#685d46; margin:0 0 4px; }}
    .footer a {{ color:#00556f; text-decoration:none; }}
    .divider {{ height:1px; background:#e4e2de; margin:0; }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <div class="check-icon">
        <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
          <path d="M6 14 L12 20 L22 10" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h1>Booking Confirmed!</h1>
      <p>Your Egyptian adventure is officially reserved.</p>
    </div>
    <div class="body">
      <div class="ref-badge">
        <span>Ref: {ref}</span>
      </div>
      <p class="greeting">Hello, {full_name}! 👋</p>
      <p class="subtext">
        We're thrilled to confirm your stay at <strong>{hotel}</strong>.
        Everything is set — all you need to do is pack your bags and get ready
        to experience the magic of Egypt.
      </p>
      <div class="card">
        <p class="card-title">Reservation Details</p>
        <div class="row">
          <span class="row-label">Hotel</span>
          <span class="row-value">{hotel}</span>
        </div>
        <div class="row">
          <span class="row-label">Room</span>
          <span class="row-value">{room}</span>
        </div>
        <div class="row">
          <span class="row-label">Check-in</span>
          <span class="row-value">{check_in}</span>
        </div>
        <div class="row">
          <span class="row-label">Check-out</span>
          <span class="row-value">{check_out}</span>
        </div>
        <div class="row">
          <span class="row-label">Duration</span>
          <span class="row-value">{nights} night{"s" if nights != 1 else ""}</span>
        </div>
      </div>
      <div class="card">
        <p class="card-title">Payment Summary</p>
        <div class="row">
          <span class="row-label">${booking["price_per_night"]} × {nights} night{"s" if nights != 1 else ""}</span>
          <span class="row-value">${booking["room_cost"]}</span>
        </div>
        <div class="row">
          <span class="row-label">Heritage Conservation Fee</span>
          <span class="row-value">$45</span>
        </div>
        <div class="row total-row">
          <span class="total-label">Total</span>
          <span class="total-value">${total}</span>
        </div>
      </div>
      <p style="font-size:13px;color:#685d46;line-height:1.7;margin:0;">
        Payment is collected at check-in. Please bring a valid ID and this
        confirmation email. For changes or cancellations, contact us at
        <a href="mailto:support@EgyGuide.eg" style="color:#00556f;">support@EgyGuide.eg</a>
        at least 48 hours before check-in.
      </p>
    </div>
    <div class="footer">
      <p><strong style="color:#00556f;">EgyGuide</strong> — Egypt Discovery</p>
      <p>© 2024 Egypt Discovery. All rights reserved.</p>
      <p style="margin-top:8px;"><a href="#">Unsubscribe</a> · <a href="#">Privacy Policy</a></p>
    </div>
  </div>
</body>
</html>
"""

    msg = Message(
        subject=f"✅ Booking Confirmed — {hotel} ({check_in} → {check_out})",
        recipients=[to_email],
        html=html_body
    )
    mail.send(msg)


# ── Static page routes ────────────────────────────────────────────────────────
@app.route("/")
@app.route("/index")
def home():
    return read_html("index.html")

@app.route("/attractions")
def attractions():
    return read_html("attractions.html")

@app.route("/explore")
def explore():
    return read_html("explore.html")

@app.route("/booking")
def booking():
    return read_html("booking.html")

@app.route("/planner")
def planner():
    return read_html("planner.html")

@app.route("/room_booking")
def room_booking():
    return read_html("room_booking.html")

@app.route("/room_details")
def room_details():
    return read_html("room_details.html")

@app.route("/user_dashboard")
def user_dashboard():
    return read_html("user_dashboard.html")

@app.route("/report-fraud")
def report_fraud():
    return read_html("fraud_report.html")


@app.route("/admin_dashboard")
def admin_overview():
    if session.get("role") != "admin":
        return redirect(url_for("signin_page", error="Admin access only."))
    return read_html("admin_dashboard.html")

@app.route("/admin_attractions")
def manage_attractions():
    if session.get("role") != "admin":
        return redirect(url_for("signin_page", error="Admin access only."))
    return read_html("admin_attractions.html")

@app.route("/admin_fraud_report")
def fraud_reports_monitor():
    if session.get("role") != "admin":
        return redirect(url_for("signin_page", error="Admin access only."))
    return read_html("admin_fraud_report.html")

@app.route("/admin_user_plans")
def user_plans_insights():
    if session.get("role") != "admin":
        return redirect(url_for("signin_page", error="Admin access only."))
    return read_html("admin_user_plans.html")


# ── Sign Up ───────────────────────────────────────────────────────────────────
@app.route("/signup", methods=["POST"])
def signup():
    full_name = request.form.get("full_name", "").strip()
    email     = request.form.get("email", "").strip().lower()
    password  = request.form.get("password", "")
    confirm   = request.form.get("confirm_password", "")

    if not full_name or not email or not password:
        return redirect(url_for("sign_up", error="All fields are required."))
    if password != confirm:
        return redirect(url_for("sign_up", error="Passwords do not match."))
    if len(password) < 8:
        return redirect(url_for("sign_up", error="Password must be at least 8 characters."))

    password_hash = generate_password_hash(password)

    try:
        existing = supabase.table("User").select("user_id").eq("email", email).execute()
        if existing.data:
            return redirect(url_for("sign_up", error="An account with that email already exists."))

        result = supabase.table("User").insert({
            "full_name":     full_name,
            "email":         email,
            "password_hash": password_hash,
            "role":          "user",
            "created_at":    datetime.utcnow().isoformat()
        }).execute()

        user = result.data[0]
        session["user_id"]   = user["user_id"]
        session["full_name"] = full_name
        session["email"]     = email
        session["role"]      = "user"

        response = make_response(redirect(url_for("home")))
        response.set_cookie("logged_in", "true", max_age=60*60*24*7)
        return response

    except Exception as e:
        print(f"[SIGNUP ERROR] {e}")
        return redirect(url_for("sign_up", error="Something went wrong. Please try again."))


# ── Sign In ───────────────────────────────────────────────────────────────────
@app.route("/sign_in", methods=["POST"])
def signin():
    email    = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        return redirect(url_for("signin_page", error="Email and password are required."))

    try:
        result = supabase.table("User").select("user_id, full_name, password_hash, role").eq("email", email).execute()

        if not result.data:
            return redirect(url_for("signin_page", error="Invalid email or password."))

        user = result.data[0]

        if not check_password_hash(user["password_hash"], password):
            return redirect(url_for("signin_page", error="Invalid email or password."))

        session["user_id"]   = user["user_id"]
        session["full_name"] = user["full_name"]
        session["email"]     = email
        session["role"]      = user["role"]

        response = make_response(redirect(
            url_for("admin_overview") if user["role"] == "admin" else url_for("home")
        ))
        response.set_cookie("logged_in", "true", max_age=60*60*24*7)
        response.set_cookie("user_role", user["role"], max_age=60*60*24*7)
        return response

    except Exception as e:
        print(f"[SIGNIN ERROR] {e}")
        return redirect(url_for("signin_page", error="Something went wrong. Please try again."))


# ── Sign Out ──────────────────────────────────────────────────────────────────
@app.route("/signout")
def signout():
    session.clear()
    response = make_response(redirect(url_for("home")))
    response.delete_cookie("logged_in")
    response.delete_cookie("user_role")
    return response


# ── Sign In / Sign Up pages ───────────────────────────────────────────────────
@app.route("/sign_in")
def signin_page():
    error = request.args.get("error", "")
    return render_template_string(read_html("sign_in.html"), error=error)

@app.route("/sign_up")
def signup_page():
    error = request.args.get("error", "")
    return render_template_string(read_html("sign_up.html"), error=error)


# ── Current user API ──────────────────────────────────────────────────────────
@app.route("/api/me")
def api_me():
    if "user_id" not in session:
        return jsonify({"error": "not logged in"}), 401
    return jsonify({
        "full_name": session.get("full_name", ""),
        "email":     session.get("email", ""),
        "role":      session.get("role", "user")
    })


# ── Booking API ───────────────────────────────────────────────────────────────
@app.route("/api/book", methods=["POST"])
def api_book():
    """
    Create a booking, save it to Supabase, and email the user a confirmation.

    Expected JSON body:
    {
        "room_name":       "Deluxe Nile View Room",
        "hotel_name":      "Luxor Heritage Escapes",
        "check_in":        "2025-11-01",
        "check_out":       "2025-11-06",
        "price_per_night": 120
    }

    Supabase table needed (create if not exists):
    CREATE TABLE "Booking" (
        booking_id    BIGSERIAL PRIMARY KEY,
        user_id       BIGINT       REFERENCES "User"(user_id),
        hotel_name    TEXT,
        room_name     TEXT,
        check_in      DATE,
        check_out     DATE,
        nights        INTEGER,
        price_per_night INTEGER,
        room_cost     INTEGER,
        total         INTEGER,
        status        TEXT         DEFAULT 'confirmed',
        created_at    TIMESTAMPTZ  DEFAULT now()
    );
    """
    if "user_id" not in session:
        return jsonify({"error": "Please sign in to make a booking."}), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request."}), 400

    # ── Validate fields ────────────────────────────────────────────────────
    required = ["room_name", "hotel_name", "check_in", "check_out", "price_per_night"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        check_in  = datetime.strptime(data["check_in"],  "%Y-%m-%d").date()
        check_out = datetime.strptime(data["check_out"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    if check_out <= check_in:
        return jsonify({"error": "Check-out must be after check-in."}), 400

    nights          = (check_out - check_in).days
    price_per_night = int(data["price_per_night"])
    room_cost       = price_per_night * nights
    conservation    = 45
    total           = room_cost + conservation

    user_id    = session["user_id"]
    full_name  = session.get("full_name", "Guest")
    user_email = session.get("email", "")

    # ── Save to Supabase ──────────────────────────────────────────────────
    booking_record = None
    try:
        result = supabase.table("Booking").insert({
            "user_id":        user_id,
            "hotel_name":     data["hotel_name"],
            "room_name":      data["room_name"],
            "check_in":       str(check_in),
            "check_out":      str(check_out),
            "nights":         nights,
            "price_per_night": price_per_night,
            "room_cost":      room_cost,
            "total":          total,
            "status":         "confirmed",
            "created_at":     datetime.utcnow().isoformat()
        }).execute()
        booking_record = result.data[0] if result.data else {}
    except Exception as db_err:
        print(f"[BOOKING DB ERROR] {db_err}")
        # Don't crash — still try to send email and return success
        booking_record = {}

    # ── Send confirmation email ───────────────────────────────────────────
    booking_details = {
        "booking_id":      booking_record.get("booking_id", "—"),
        "id":              booking_record.get("booking_id", 0),
        "hotel_name":      data["hotel_name"],
        "room_name":       data["room_name"],
        "check_in":        check_in.strftime("%B %d, %Y"),
        "check_out":       check_out.strftime("%B %d, %Y"),
        "nights":          nights,
        "price_per_night": price_per_night,
        "room_cost":       room_cost,
        "total":           total,
    }

    email_sent = False
    if user_email and app.config.get("MAIL_USERNAME"):
        try:
            send_booking_email(user_email, full_name, booking_details)
            email_sent = True
            print(f"[EMAIL] Confirmation sent to {user_email}")
        except Exception as mail_err:
            print(f"[EMAIL ERROR] {mail_err}")
            # Don't fail the booking just because email failed
    else:
        print("[EMAIL] Skipped — MAIL_USERNAME not configured.")

    return jsonify({
        "success":    True,
        "booking_id": booking_record.get("booking_id"),
        "email_sent": email_sent,
        "nights":     nights,
        "total":      total
    }), 201


# ── Database connection test ──────────────────────────────────────────────────
@app.route("/test-db")
def test_db():
    try:
        result = supabase.table("User").select("user_id").limit(1).execute()
        return "✅ Supabase connected successfully!"
    except Exception as e:
        return f"❌ Supabase connection failed: {e}"


# ── attractions API ───────────────────────────────────────────────────────────
@app.route("/api/attractions")
def api_attractions():
    try:
        result = supabase.table("attraction").select("*").eq("is_active", True).order("created_at", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        print(f"[attractionS API ERROR] {e}")
        return jsonify([]), 500


@app.route("/api/attractions/add", methods=["POST"])
def api_add_attraction():
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    required = ["name", "region", "location", "description", "entry_fee"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        result = supabase.table("attraction").insert({
            "name":          data.get("name"),
            "region":        data.get("region"),
            "category":      data.get("category", ""),
            "location":      data.get("location"),
            "description":   data.get("description"),
            "history":       data.get("history", ""),
            "best_time":     data.get("best_time", ""),
            "activities":    data.get("activities", ""),
            "what_to_bring": data.get("what_to_bring", ""),
            "entry_fee":     data.get("entry_fee"),
            "image_url":     data.get("image_url", ""),
            "is_active":     True,
            "created_at":    datetime.utcnow().isoformat()
        }).execute()
        return jsonify({"success": True, "attraction": result.data[0]}), 201
    except Exception as e:
        print(f"[ADD attraction ERROR] {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/attractions/edit/<int:attraction_id>", methods=["PATCH"])
def api_edit_attraction(attraction_id):
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    try:
        supabase.table("attraction").update({
            "name":          data.get("name"),
            "region":        data.get("region"),
            "category":      data.get("category", ""),
            "location":      data.get("location"),
            "description":   data.get("description"),
            "history":       data.get("history", ""),
            "best_time":     data.get("best_time", ""),
            "activities":    data.get("activities", ""),
            "what_to_bring": data.get("what_to_bring", ""),
            "entry_fee":     data.get("entry_fee"),
            "image_url":     data.get("image_url", ""),
        }).eq("attraction_id", attraction_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/attractions/delete/<int:attraction_id>", methods=["DELETE"])
def api_delete_attraction(attraction_id):
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    try:
        supabase.table("attraction").update({"is_active": False}).eq("attraction_id", attraction_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
