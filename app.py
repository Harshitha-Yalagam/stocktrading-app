from flask import Flask, render_template, request, session, redirect, url_for
from cs50 import SQL
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from flask_session import Session

app = Flask(__name__)

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database connection
db = SQL("sqlite:///database.db")

# Alpha Vantage API key (replace with your key)
API_KEY = "YOUR_API_KEY"
def lookup(symbol):
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()
        print("API Response:", data)  # Debug: See what Alpha Vantage sends
        quote = data["Global Quote"]
        return {
            "name": symbol,
            "price": float(quote["05. price"]),
            "symbol": quote["01. symbol"]
        }
    except Exception as e:
        print("Lookup Error:", e)  # Debug: Catch any issues
        return None

@app.template_filter("usd")
def usd(value):
    return f"${value:,.2f}"

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    stocks = db.execute("SELECT symbol, SUM(shares) as shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id)
    portfolio = []
    total_value = cash
    for stock in stocks:
        quote = lookup(stock["symbol"])
        if quote:
            value = stock["shares"] * quote["price"]
            portfolio.append({"symbol": stock["symbol"], "shares": stock["shares"], "price": quote["price"], "value": value})
            total_value += value
    return render_template("index.html", portfolio=portfolio, cash=cash, total=total_value)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return "Invalid username or password", 400
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return "Missing username or password", 400
        hash = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
            return redirect("/login")
        except:
            return "Username already taken", 400
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/buy", methods=["GET", "POST"])
def buy():
    if "user_id" not in session:
        return redirect("/login")
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = int(request.form.get("shares"))
        quote = lookup(symbol)
        if not quote or shares < 1:
            return "Invalid symbol or shares", 400
        user_id = session["user_id"]
        cost = quote["price"] * shares
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        if cash < cost:
            return "Not enough cash", 400
        db.execute("UPDATE users SET cash = cash - ? WHERE id = ?", cost, user_id)
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                   user_id, symbol, shares, quote["price"])
        return redirect("/")
    return render_template("buy.html")

@app.route("/sell", methods=["GET", "POST"])
def sell():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]
    stocks = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id)
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = int(request.form.get("shares"))
        quote = lookup(symbol)
        owned_shares = db.execute("SELECT SUM(shares) as total FROM transactions WHERE user_id = ? AND symbol = ?",
                                  user_id, symbol)[0]["total"]
        if not quote or shares < 1 or shares > owned_shares:
            return "Invalid sale", 400
        revenue = quote["price"] * shares
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", revenue, user_id)
        db.execute("INSERT INTO transactions (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
                   user_id, symbol, -shares, quote["price"])
        return redirect("/")
    return render_template("sell.html", stocks=stocks)

@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]
    transactions = db.execute("SELECT symbol, shares, price, timestamp FROM transactions WHERE user_id = ? ORDER BY timestamp DESC", user_id)
    return render_template("history.html", transactions=transactions)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)