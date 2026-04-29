from flask import Flask, request, redirect, url_for, session, render_template_string, make_response, jsonify
from supabase import create_client
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-to-a-random-secret")
app.config["SESSION_PERMANENT"] = False   # sessions expire when browser closes unless "remember me" is checked

# ── Supabase client ───────────────────────────────────────────────────────────
SUPABASE_URL = "https://wfmijhnvzhndjwjpidiw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndmbWlqaG52emhuZGp3anBpZGl3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM0NDU1NTUsImV4cCI6MjA4OTAyMTU1NX0.wAWgUlP5drEYy1CmTvjI-86JeHmA8PSrWL2osFpxc1A"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Flask-Mail ────────────────────────────────────────────────────────────────
from flask_mail import Mail, Message

app.config["MAIL_SERVER"]         = "smtp.gmail.com"
app.config["MAIL_PORT"]           = 587
app.config["MAIL_USE_TLS"]        = True
app.config["MAIL_USERNAME"]       = os.environ.get("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"]       = os.environ.get("MAIL_PASSWORD", "")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME", "noreply@egyguide.eg")

mail = Mail(app)


def read_html(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# ── Email: booking confirmation ───────────────────────────────────────────────
def send_booking_email(to_email, full_name, booking):
    check_in  = booking["check_in"]
    check_out = booking["check_out"]
    nights    = booking["nights"]
    total     = booking["total"]
    room      = booking["room_name"]
    hotel     = booking["hotel_name"]
    ref       = f"EGY-{booking.get('booking_id', '—')}"

    html_body = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"/>
<style>
  body{{margin:0;padding:0;background:#f5f3ef;font-family:'Helvetica Neue',Arial,sans-serif;}}
  .wrapper{{max-width:600px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);}}
  .header{{background:linear-gradient(135deg,#00556f 0%,#1c6e8c 100%);padding:48px 40px 40px;text-align:center;}}
  .header h1{{color:#fff;font-size:28px;font-weight:800;margin:0 0 4px;}}
  .header p{{color:rgba(255,255,255,0.8);font-size:14px;margin:0;}}
  .icon{{width:56px;height:56px;background:rgba(255,255,255,0.15);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 20px;}}
  .body{{padding:40px;}}
  .greeting{{font-size:18px;font-weight:700;color:#1a1c1a;margin-bottom:8px;}}
  .subtext{{font-size:14px;color:#685d46;margin-bottom:32px;line-height:1.6;}}
  .card{{background:#f5f3ef;border-radius:12px;padding:28px;margin-bottom:28px;}}
  .card-title{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:#685d46;margin-bottom:16px;}}
  .row{{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #e4e2de;}}
  .row:last-child{{border-bottom:none;}}
  .rl{{font-size:13px;color:#685d46;}} .rv{{font-size:13px;font-weight:700;color:#1a1c1a;}}
  .total-row{{padding-top:16px;margin-top:8px;border-top:2px solid #00556f;}}
  .tl{{font-size:15px;font-weight:800;color:#1a1c1a;}} .tv{{font-size:20px;font-weight:800;color:#00556f;}}
  .badge{{text-align:center;margin-bottom:28px;}}
  .badge span{{background:#00556f;color:#fff;font-size:12px;font-weight:700;padding:6px 16px;border-radius:999px;}}
  .footer{{background:#f5f3ef;padding:28px 40px;text-align:center;border-top:1px solid #e4e2de;font-size:12px;color:#685d46;}}
  .footer a{{color:#00556f;text-decoration:none;}}
</style></head><body>
<div class="wrapper">
  <div class="header">
    <div class="icon"><svg width="28" height="28" viewBox="0 0 28 28" fill="none"><path d="M6 14 L12 20 L22 10" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
    <h1>Booking Confirmed!</h1><p>Your Egyptian adventure is officially reserved.</p>
  </div>
  <div class="body">
    <div class="badge"><span>Ref: {ref}</span></div>
    <p class="greeting">Hello, {full_name}! 👋</p>
    <p class="subtext">We're thrilled to confirm your stay at <strong>{hotel}</strong>. Pack your bags and get ready to experience the magic of Egypt.</p>
    <div class="card">
      <p class="card-title">Reservation Details</p>
      <div class="row"><span class="rl">Hotel</span><span class="rv">{hotel}</span></div>
      <div class="row"><span class="rl">Room</span><span class="rv">{room}</span></div>
      <div class="row"><span class="rl">Check-in</span><span class="rv">{check_in}</span></div>
      <div class="row"><span class="rl">Check-out</span><span class="rv">{check_out}</span></div>
      <div class="row"><span class="rl">Duration</span><span class="rv">{nights} night{"s" if nights != 1 else ""}</span></div>
    </div>
    <div class="card">
      <p class="card-title">Payment Summary</p>
      <div class="row"><span class="rl">${booking["price_per_night"]} x {nights} night{"s" if nights != 1 else ""}</span><span class="rv">${booking["room_cost"]}</span></div>
      <div class="row"><span class="rl">Heritage Conservation Fee</span><span class="rv">$45</span></div>
      <div class="row total-row"><span class="tl">Total</span><span class="tv">${total}</span></div>
    </div>
    <p style="font-size:13px;color:#685d46;line-height:1.7;">Payment collected at check-in. Bring a valid ID. For changes contact <a href="mailto:support@egyguide.eg" style="color:#00556f;">support@egyguide.eg</a> 48hrs before check-in.</p>
  </div>
  <div class="footer"><p><strong style="color:#00556f;">EgyGuide</strong> — Egypt Discovery</p><p>© 2025 EgyGuide. All rights reserved.</p></div>
</div></body></html>"""

    msg = Message(
        subject=f"Booking Confirmed — {hotel} ({check_in} to {check_out})",
        recipients=[to_email],
        html=html_body
    )
    mail.send(msg)


# ── Email: fraud report confirmation ─────────────────────────────────────────
def send_fraud_email(to_email, full_name, report):
    ref = f"FRD-{report.get('report_id', '—')}"
    html_body = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"/>
<style>
  body{{margin:0;padding:0;background:#f5f3ef;font-family:'Helvetica Neue',Arial,sans-serif;}}
  .wrapper{{max-width:600px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);}}
  .header{{background:#ba1a1a;padding:40px;text-align:center;}}
  .header h1{{color:#fff;font-size:24px;font-weight:800;margin:0;}}
  .body{{padding:40px;}}
  .card{{background:#f5f3ef;border-radius:12px;padding:28px;margin:24px 0;}}
  .card-title{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.12em;color:#685d46;margin-bottom:16px;}}
  .row{{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #e4e2de;font-size:14px;}}
  .row:last-child{{border-bottom:none;}}
  .rl{{color:#685d46;}} .rv{{font-weight:700;color:#1a1c1a;max-width:60%;text-align:right;}}
  .footer{{background:#f5f3ef;padding:20px 40px;text-align:center;font-size:12px;color:#685d46;border-top:1px solid #e4e2de;}}
</style></head><body>
<div class="wrapper">
  <div class="header"><h1>Fraud Report Received</h1></div>
  <div class="body">
    <p style="font-size:16px;font-weight:700;margin-bottom:4px;">Hello, {full_name}</p>
    <p style="font-size:14px;color:#685d46;margin-bottom:0;">Your report has been received. Our team will review it within 24-48 hours and contact you if further information is needed.</p>
    <div class="card">
      <p class="card-title">Report Summary</p>
      <div class="row"><span class="rl">Reference</span><span class="rv">{ref}</span></div>
      <div class="row"><span class="rl">Fraud Type</span><span class="rv">{report.get("fraud_type","—")}</span></div>
      <div class="row"><span class="rl">Location</span><span class="rv">{report.get("location","—")}</span></div>
      <div class="row"><span class="rl">Date of Incident</span><span class="rv">{report.get("incident_date","—")}</span></div>
      <div class="row"><span class="rl">Status</span><span class="rv" style="color:#755b00;">Pending Review</span></div>
    </div>
    <p style="font-size:13px;color:#685d46;line-height:1.7;">If you have additional evidence or information, please reply to this email with your reference number.</p>
  </div>
  <div class="footer"><p><strong style="color:#00556f;">EgyGuide</strong> — Egypt Discovery · <a href="mailto:support@egyguide.eg" style="color:#00556f;">support@egyguide.eg</a></p></div>
</div></body></html>"""

    msg = Message(
        subject=f"Fraud Report Received — Reference {ref}",
        recipients=[to_email],
        html=html_body
    )
    mail.send(msg)


# ── Static routes ─────────────────────────────────────────────────────────────
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


# ── Auth ──────────────────────────────────────────────────────────────────────
@app.route("/signup", methods=["POST"])
def signup():
    full_name = request.form.get("full_name", "").strip()
    email     = request.form.get("email", "").strip().lower()
    password  = request.form.get("password", "")
    confirm   = request.form.get("confirm_password", "")

    if not full_name or not email or not password:
        return redirect(url_for("signup_page", error="All fields are required."))
    if password != confirm:
        return redirect(url_for("signup_page", error="Passwords do not match."))
    if len(password) < 8:
        return redirect(url_for("signup_page", error="Password must be at least 8 characters."))

    password_hash = generate_password_hash(password)
    try:
        existing = supabase.table("User").select("user_id").eq("email", email).execute()
        if existing.data:
            return redirect(url_for("signup_page", error="An account with that email already exists."))

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

        session.permanent = False  # new signups always get session cookies
        response = make_response(redirect(url_for("home")))
        response.set_cookie("logged_in", "true")  # session cookie, no max_age
        return response
    except Exception as e:
        print(f"[SIGNUP ERROR] {e}")
        return redirect(url_for("signup_page", error="Something went wrong. Please try again."))


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

        remember = request.form.get("remember") == "on"
        session.permanent = remember  # only persist session if "keep me signed in" checked

        response = make_response(redirect(
            url_for("admin_overview") if user["role"] == "admin" else url_for("home")
        ))
        if remember:
            # Persist cookies for 7 days only if user opted in
            response.set_cookie("logged_in", "true", max_age=60*60*24*7)
            response.set_cookie("user_role", user["role"], max_age=60*60*24*7)
        else:
            # Session cookies — expire when browser closes, no max_age
            response.set_cookie("logged_in", "true")
            response.set_cookie("user_role", user["role"])
        return response
    except Exception as e:
        print(f"[SIGNIN ERROR] {e}")
        return redirect(url_for("signin_page", error="Something went wrong. Please try again."))


@app.route("/signout")
def signout():
    session.clear()
    response = make_response(redirect(url_for("home")))
    response.delete_cookie("logged_in")
    response.delete_cookie("user_role")
    return response


@app.route("/sign_in")
def signin_page():
    error = request.args.get("error", "")
    return render_template_string(read_html("sign_in.html"), error=error)

@app.route("/sign_up")
def signup_page():
    error = request.args.get("error", "")
    return render_template_string(read_html("Sign_up.html"), error=error)


# ── Current user ──────────────────────────────────────────────────────────────
@app.route("/api/me")
def api_me():
    if "user_id" not in session:
        return jsonify({"error": "not logged in"}), 401
    return jsonify({
        "user_id":   session.get("user_id"),
        "full_name": session.get("full_name", ""),
        "email":     session.get("email", ""),
        "role":      session.get("role", "user")
    })


# ── Update profile ────────────────────────────────────────────────────────────
@app.route("/api/profile/update", methods=["POST"])
def api_update_profile():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    data      = request.get_json(silent=True) or {}
    full_name = data.get("full_name", "").strip()
    if not full_name:
        return jsonify({"error": "Name cannot be empty."}), 400
    try:
        supabase.table("User").update({"full_name": full_name}).eq("user_id", session["user_id"]).execute()
        session["full_name"] = full_name
        return jsonify({"success": True, "full_name": full_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Booking ───────────────────────────────────────────────────────────────────
@app.route("/api/book", methods=["POST"])
def api_book():
    if "user_id" not in session:
        return jsonify({"error": "Please sign in to make a booking."}), 401

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request."}), 400

    required = ["room_name", "hotel_name", "check_in", "check_out", "price_per_night"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        check_in  = datetime.strptime(data["check_in"],  "%Y-%m-%d").date()
        check_out = datetime.strptime(data["check_out"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format."}), 400

    if check_out <= check_in:
        return jsonify({"error": "Check-out must be after check-in."}), 400

    nights          = (check_out - check_in).days
    price_per_night = int(data["price_per_night"])
    room_cost       = price_per_night * nights
    total           = room_cost + 45  # conservation fee

    user_id    = session["user_id"]
    full_name  = session.get("full_name", "Guest")
    user_email = session.get("email", "")

    booking_record = {}
    try:
        result = supabase.table("Booking").insert({
            "user_id":         user_id,
            "hotel_name":      data["hotel_name"],
            "room_name":       data["room_name"],
            "check_in":        str(check_in),
            "check_out":       str(check_out),
            "nights":          nights,
            "price_per_night": price_per_night,
            "room_cost":       room_cost,
            "total":           total,
            "status":          "confirmed",
            "created_at":      datetime.utcnow().isoformat()
        }).execute()
        booking_record = result.data[0] if result.data else {}
    except Exception as db_err:
        print(f"[BOOKING DB ERROR] {db_err}")

    booking_details = {
        "booking_id":      booking_record.get("booking_id", "—"),
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
            print(f"[EMAIL] Booking confirmation sent to {user_email}")
        except Exception as mail_err:
            print(f"[EMAIL ERROR] {mail_err}")
    else:
        print("[EMAIL] Skipped — MAIL_USERNAME not configured.")

    return jsonify({
        "success":    True,
        "booking_id": booking_record.get("booking_id"),
        "email_sent": email_sent,
        "nights":     nights,
        "total":      total
    }), 201


# ── My bookings ───────────────────────────────────────────────────────────────
@app.route("/api/my-bookings")
def api_my_bookings():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    try:
        result = supabase.table("Booking").select("*") \
            .eq("user_id", session["user_id"]) \
            .order("created_at", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        print(f"[MY BOOKINGS ERROR] {e}")
        return jsonify([]), 500


# ── Cancel booking ────────────────────────────────────────────────────────────
@app.route("/api/bookings/cancel/<int:booking_id>", methods=["PATCH"])
def api_cancel_booking(booking_id):
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    try:
        result = supabase.table("Booking").select("user_id, status") \
            .eq("booking_id", booking_id).execute()
        if not result.data:
            return jsonify({"error": "Booking not found"}), 404
        b = result.data[0]
        if b["user_id"] != session["user_id"]:
            return jsonify({"error": "Unauthorized"}), 403
        if b["status"] == "cancelled":
            return jsonify({"error": "Already cancelled"}), 400
        supabase.table("Booking").update({"status": "cancelled"}) \
            .eq("booking_id", booking_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Fraud report ──────────────────────────────────────────────────────────────
@app.route("/api/fraud-report", methods=["POST"])
def api_fraud_report():
    """
    Supabase table needed:
    CREATE TABLE IF NOT EXISTS "FraudReport" (
        report_id      BIGSERIAL    PRIMARY KEY,
        user_id        BIGINT       REFERENCES "User"(user_id) ON DELETE SET NULL,
        reporter_name  TEXT,
        reporter_email TEXT,
        fraud_type     TEXT,
        location       TEXT,
        incident_date  DATE,
        description    TEXT,
        status         TEXT         DEFAULT 'pending',
        created_at     TIMESTAMPTZ  DEFAULT now()
    );
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request."}), 400

    required = ["reporter_name", "reporter_email", "fraud_type", "description"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Missing field: {field}"}), 400

    user_id = session.get("user_id")
    report_record = {}
    try:
        result = supabase.table("FraudReport").insert({
            "user_id":        user_id,
            "reporter_name":  data.get("reporter_name"),
            "reporter_email": data.get("reporter_email"),
            "fraud_type":     data.get("fraud_type"),
            "location":       data.get("location", ""),
            "incident_date":  data.get("incident_date") or None,
            "description":    data.get("description"),
            "status":         "pending",
            "created_at":     datetime.utcnow().isoformat()
        }).execute()
        report_record = result.data[0] if result.data else {}
    except Exception as db_err:
        print(f"[FRAUD REPORT DB ERROR] {db_err}")

    to_email  = data.get("reporter_email")
    full_name = data.get("reporter_name", "User")
    if to_email and app.config.get("MAIL_USERNAME"):
        try:
            send_fraud_email(to_email, full_name, {
                **data,
                "report_id": report_record.get("report_id", "—")
            })
            print(f"[EMAIL] Fraud report confirmation sent to {to_email}")
        except Exception as mail_err:
            print(f"[EMAIL ERROR] {mail_err}")

    return jsonify({
        "success":   True,
        "report_id": report_record.get("report_id")
    }), 201


# ── Planner save / load ───────────────────────────────────────────────────────
@app.route("/api/planner/save", methods=["POST"])
def api_save_plan():
    """
    Supabase table needed:
    CREATE TABLE IF NOT EXISTS "TripPlan" (
        plan_id    BIGSERIAL    PRIMARY KEY,
        user_id    BIGINT       UNIQUE REFERENCES "User"(user_id) ON DELETE CASCADE,
        plan_data  JSONB,
        updated_at TIMESTAMPTZ  DEFAULT now()
    );
    """
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    data = request.get_json(silent=True)
    if not data or "plan_data" not in data:
        return jsonify({"error": "Missing plan_data"}), 400

    user_id = session["user_id"]
    try:
        existing = supabase.table("TripPlan").select("plan_id").eq("user_id", user_id).execute()
        if existing.data:
            supabase.table("TripPlan").update({
                "plan_data":  data["plan_data"],
                "updated_at": datetime.utcnow().isoformat()
            }).eq("user_id", user_id).execute()
        else:
            supabase.table("TripPlan").insert({
                "user_id":    user_id,
                "plan_data":  data["plan_data"],
                "updated_at": datetime.utcnow().isoformat()
            }).execute()
        return jsonify({"success": True})
    except Exception as e:
        print(f"[PLANNER SAVE ERROR] {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/planner/load")
def api_load_plan():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    try:
        result = supabase.table("TripPlan").select("plan_data, updated_at") \
            .eq("user_id", session["user_id"]).execute()
        if result.data:
            return jsonify(result.data[0])
        return jsonify({"plan_data": None})
    except Exception as e:
        return jsonify({"plan_data": None}), 500


# ── Admin APIs ────────────────────────────────────────────────────────────────
@app.route("/api/admin/bookings")
def api_admin_bookings():
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    try:
        result = supabase.table("Booking").select("*").order("created_at", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify([]), 500


@app.route("/api/admin/fraud-reports")
def api_admin_fraud_reports():
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    try:
        result = supabase.table("FraudReport").select("*").order("created_at", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        return jsonify([]), 500


@app.route("/api/admin/fraud-reports/update/<int:report_id>", methods=["PATCH"])
def api_update_fraud_status(report_id):
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    data   = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in ["pending", "investigating", "resolved", "dismissed"]:
        return jsonify({"error": "Invalid status"}), 400
    try:
        supabase.table("FraudReport").update({"status": status}).eq("report_id", report_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Attractions ───────────────────────────────────────────────────────────────
@app.route("/api/attractions")
def api_attractions():
    try:
        result = supabase.table("attraction").select("*").eq("is_active", True).order("created_at", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        print(f"[ATTRACTIONS API ERROR] {e}")
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


# ── DB test ───────────────────────────────────────────────────────────────────
@app.route("/test-db")
def test_db():
    try:
        supabase.table("User").select("user_id").limit(1).execute()
        return "Supabase connected successfully!"
    except Exception as e:
        return f"Supabase connection failed: {e}"


if __name__ == "__main__":
    app.run(debug=True)
