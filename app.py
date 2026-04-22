from flask import Flask, request, redirect, url_for, session, render_template_string, make_response
from supabase import create_client
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-to-a-random-secret")

# ── Supabase client ───────────────────────────────────────────────────────────
SUPABASE_URL = "https://wfmijhnvzhndjwjpidiw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndmbWlqaG52emhuZGp3anBpZGl3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM0NDU1NTUsImV4cCI6MjA4OTAyMTU1NX0.wAWgUlP5drEYy1CmTvjI-86JeHmA8PSrWL2osFpxc1A"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def read_html(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


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


# ── Database connection test ──────────────────────────────────────────────────
@app.route("/test-db")
def test_db():
    try:
        result = supabase.table("User").select("user_id").limit(1).execute()
        return "✅ Supabase connected successfully!"
    except Exception as e:
        return f"❌ Supabase connection failed: {e}"


# ── Current user API ─────────────────────────────────────────────────────────
@app.route("/api/me")
def api_me():
    from flask import jsonify
    if "user_id" not in session:
        return jsonify({"error": "not logged in"}), 401
    return jsonify({
        "full_name": session.get("full_name", "Admin"),
        "role":      session.get("role", "user")
    })


# ── Attractions API ───────────────────────────────────────────────────────────
from flask import jsonify

@app.route("/api/attractions")
def api_attractions():
    try:
        result = supabase.table("Attraction").select("*").eq("is_active", True).order("created_at", desc=True).execute()
        return jsonify(result.data)
    except Exception as e:
        print(f"[ATTRACTIONS API ERROR] {e}")
        return jsonify([]), 500


@app.route("/api/attractions/add", methods=["POST"])
def api_add_attraction():
    from flask import jsonify
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    required = ["name", "region", "location", "description", "entry_fee"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        result = supabase.table("Attraction").insert({
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
        print(f"[ADD ATTRACTION ERROR] {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/attractions/edit/<int:attraction_id>", methods=["PATCH"])
def api_edit_attraction(attraction_id):
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    data = request.get_json()
    try:
        supabase.table("Attraction").update({
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
    from flask import jsonify
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    try:
        supabase.table("Attraction").update({"is_active": False}).eq("attraction_id", attraction_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
