import os
import calendar
from flask import Flask, render_template, request, redirect, url_for, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"],
)

TABLE = "expense"

# ── Home ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    result   = supabase.table(TABLE).select("*").order("date", desc=True).execute()
    expenses = result.data
    total    = sum(e["amount"] for e in expenses)
    return render_template("index.html", expenses=expenses, total=total)

# ── Add ───────────────────────────────────────────────────────────────────────

@app.route("/add", methods=["POST"])
def add():
    date        = request.form.get("date") or datetime.now().strftime("%Y-%m-%d")
    category    = request.form.get("category", "").strip()
    amount      = float(request.form.get("amount"))
    pmtmethod   = request.form.get("pmtmethod", "").strip()
    description = request.form.get("description", "").strip()

    supabase.table(TABLE).insert({
        "date":        date,
        "category":    category,
        "amount":      amount,
        "pmtmethod":   pmtmethod,
        "description": description,
    }).execute()

    return redirect(url_for("index"))

# ── Delete ────────────────────────────────────────────────────────────────────

@app.route("/delete/<int:expense_id>")
def delete(expense_id):
    supabase.table(TABLE).delete().eq("id", expense_id).execute()
    return redirect(url_for("index"))

# ── Summary page ──────────────────────────────────────────────────────────────

@app.route("/summary")
def summary():
    result   = supabase.table(TABLE).select("category, amount").execute()
    expenses = result.data

    category_totals: dict[str, float] = {}
    for e in expenses:
        category_totals[e["category"]] = category_totals.get(e["category"], 0) + e["amount"]

    rows  = sorted(
        [{"category": k, "total": v} for k, v in category_totals.items()],
        key=lambda x: x["total"], reverse=True
    )
    total = sum(e["amount"] for e in expenses)
    return render_template("summary.html", rows=rows, total=total)

# ── Monthly summary API ───────────────────────────────────────────────────────

@app.route("/api/summary")
def api_summary():
    month = request.args.get("month", type=int)
    year  = request.args.get("year",  type=int)

    query = supabase.table(TABLE).select("category, amount")

    if month and year:
        _, last_day = calendar.monthrange(year, month)
        start = f"{year}-{month:02d}-01"
        end   = f"{year}-{month:02d}-{last_day:02d}"
        query = query.gte("date", start).lte("date", end)

    expenses = query.execute().data

    category_totals: dict[str, float] = {}
    for e in expenses:
        category_totals[e["category"]] = category_totals.get(e["category"], 0) + e["amount"]

    rows  = sorted(
        [{"category": k, "total": v} for k, v in category_totals.items()],
        key=lambda x: x["total"], reverse=True
    )
    total = sum(e["amount"] for e in expenses)

    return jsonify({"rows": rows, "total": total})

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
