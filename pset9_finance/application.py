import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

# Store custom apology content in a variable
MORDOR = ("Send invalid requests by modifying the HTML", "One does not simply")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    portfolio = db.execute(
        "SELECT * FROM portfolios WHERE user_id = ?", session["user_id"])
    portfolio_total = 0

    # Get additional data from the API and update portfolio
    for stock in portfolio:
        api_data = lookup(stock["symbol"])
        portfolio_total += stock["shares"] * api_data["price"]
        stock["name"] = api_data["name"]
        stock["current_price"] = api_data["price"]
        stock["profit"] = (api_data["price"] -
                           stock["cost_basis"]) * stock["shares"]
        stock["profit_percent"] = (
            api_data["price"] - stock["cost_basis"]) / (stock["cost_basis"] / 100)

    # Store the user's cash balance in a variable
    cash = db.execute("SELECT cash FROM users WHERE id = ?",
                      session["user_id"])
    cash = cash[0]["cash"]
    portfolio_total += cash

    return render_template("index.html", portfolio=portfolio, cash=cash, portfolio_total=portfolio_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # Attempt to buy stock on POST
    if request.method == "POST":

        # Check for empty stock ticker fields
        if not request.form.get("symbol"):
            return apology(MORDOR[0], MORDOR[1])

        # Check share count for non-integer values, negative values and 0
        if not request.form.get("shares").isnumeric() or int(request.form.get("shares")) == 0:
            return apology(MORDOR[0], MORDOR[1])

        # Store user input and user's cash balance in variables
        api_data = lookup(request.form.get("symbol"))
        shares = int(request.form.get("shares"))
        cash = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"])
        cash = cash[0]["cash"]

        # Ensure that the stock ticker exists in IEX's database
        if not api_data:
            return apology(f"Ticker {request.form.get('symbol')} not found", 400)

        # Make sure that the user has sufficient funds for the purchase
        if api_data["price"] * shares > cash:
            max_amount = int(cash / api_data["price"])
            return apology(f"Insufficient funds. You currently have {usd(cash)}, which is " +
                           f"enough for {max_amount} shares of {api_data['symbol']}", 403)

        # "Purchase" shares if there are no errors
        db.execute("INSERT INTO transactions (user_id, symbol, price, shares) VALUES (?, ?, ?, ?)",
                   session["user_id"], api_data["symbol"], 0 - api_data["price"], shares)
        new_balance = cash - shares * api_data["price"]
        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                   new_balance, session["user_id"])

        # Update user's portfolio
        current_position = db.execute("SELECT * FROM portfolios WHERE user_id = ? AND symbol = ?",
                                      session["user_id"], api_data["symbol"])
        if not current_position:
            db.execute("INSERT INTO portfolios (user_id, symbol, shares, cost_basis) VALUES (?, ?, ?, ?)",
                       session["user_id"], api_data["symbol"], shares, api_data["price"])
        else:
            total_price = current_position[0]["shares"] * \
                current_position[0]["cost_basis"] + shares * api_data["price"]
            total_shares = current_position[0]["shares"] + shares
            cost_basis = total_price / total_shares
            db.execute("UPDATE portfolios SET shares = ?, cost_basis = ? WHERE user_id = ? AND symbol = ?",
                       total_shares, cost_basis, session["user_id"], api_data["symbol"])

        return redirect("/")

    # Render buy.html on GET
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    transactions = db.execute(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY time DESC", session["user_id"])
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology(MORDOR[0], MORDOR[1])

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology(MORDOR[0], MORDOR[1])

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # Look for matching stocks on POST
    if request.method == "POST":

        # Get the data for the stock
        api_data = lookup(request.form.get("symbol"))

        # Ensure that the stock ticker exists in IEX's database
        if not api_data:
            flash(f"Ticker {request.form.get('symbol').upper()} not found")
            return render_template("quote.html", alert_type="danger")

        # Show the stock quote below the form if a match is found
        return render_template("quote.html", api_data=api_data)

    # Show the search form on GET
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        username = request.form.get("username")

        # Ensure username was submitted
        if not username:
            return apology(MORDOR[0], MORDOR[1])

        # Query database for a matching username
        if db.execute("SELECT * FROM users WHERE username = ?", username):
            return apology("username already in use", 403)

        # Ensure password was submitted
        if not request.form.get("password") or not request.form.get("confirmation"):
            return apology(MORDOR[0], MORDOR[1])

        # Check that the password and password confirmation match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match", 400)

        starting_balance = 0

        # Determine starting balance
        if request.form.get("starting-balance"):
            starting_balance = request.form.get("starting-balance")

            # Check for non-integer values, negative values and 0
            if not starting_balance.isnumeric() or int(starting_balance) == 0:
                return apology(MORDOR[0], MORDOR[1])

            # Convert starting_balance to a float
            starting_balance = float(starting_balance)

        else:
            # Use default value of $10,000 if user didn't specify a value
            starting_balance = 10000.00

        # Register new user if no issues were found
        db.execute("INSERT INTO users (username, cash, hash) VALUES (?, ?, ?)",
                   username, starting_balance, generate_password_hash(request.form.get("password")))
        user_id = db.execute(
            "SELECT id FROM users WHERE username = ?", username)
        db.execute("INSERT INTO transactions (user_id, symbol, price) VALUES (?, ?, ?)",
                   user_id[0]["id"], "cash_deposit", starting_balance)

        return render_template("success.html")

    # Show registration page if user reached route via GET
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Get the symbols of all the stocks in the user's portfolio
    portfolio = db.execute(
        "SELECT * FROM portfolios WHERE user_id = ?", session["user_id"])
    stocks = [stock["symbol"] for stock in portfolio]

    if request.method == "POST":

        # Check for empty stock ticker fields
        if not request.form.get("symbol"):
            return apology(MORDOR[0], MORDOR[1])

        # Check for stocks not in portfolio
        if request.form.get("symbol") not in stocks:
            return apology(MORDOR[0], MORDOR[1])

        # Check for empty shares-field
        if not request.form.get("shares"):
            return apology(MORDOR[0], MORDOR[1])

        shares = int(request.form.get("shares"))

        # Check for negative numbers or 0 in share count
        if shares < 1:
            return apology(MORDOR[0], MORDOR[1])

        # Make sure that the user has enough shares to sell
        owned_shares = db.execute("SELECT shares FROM portfolios WHERE user_id = ? AND symbol = ?",
                                  session["user_id"], request.form.get("symbol"))
        if shares > owned_shares[0]["shares"]:
            return apology(f"Not enough shares to sell. You have {owned_shares[0]['shares']} shares " +
                           f"of {request.form.get('symbol')}.", 403)

        # Make transaction
        api_data = lookup(request.form.get("symbol"))
        db.execute("INSERT INTO transactions (user_id, symbol, price, shares) VALUES (?, ?, ?, ?)",
                   session["user_id"], api_data["symbol"], api_data["price"], shares)

        # Update portfolio (delete stock from portfolio when selling all remaining shares)
        new_shares = owned_shares[0]["shares"] - shares
        if new_shares == 0:
            db.execute("DELETE FROM portfolios WHERE user_id = ? AND symbol = ?",
                       session["user_id"], api_data["symbol"])
        else:
            db.execute("UPDATE portfolios SET shares = ? WHERE user_id = ? AND symbol = ?",
                       new_shares, session["user_id"], api_data["symbol"])

        # Update user's cash balance
        cash = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"])
        new_balance = cash[0]["cash"] + shares * api_data["price"]
        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                   new_balance, session["user_id"])

        return redirect("/")

    # Show sell.html on GET using the variable "stocks" for the dropdown menu
    if request.method == "GET":
        return render_template("sell.html", stocks=stocks)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():

    username = db.execute(
        "SELECT username FROM users WHERE id = ?", session["user_id"])
    username = username[0]["username"]

    # Make changes if a form was submitted
    if request.method == "POST":
        old_password_hash = db.execute(
            "SELECT hash FROM users WHERE id = ?", session["user_id"])

        # Change username
        if request.form.get("new-username"):
            new_username = request.form.get("new-username")

            # Check that a password was submitted
            if not request.form.get("password-check"):
                return apology(MORDOR[0], MORDOR[1])

            # Check that the password is correct
            if not check_password_hash(old_password_hash[0]["hash"], request.form.get("password-check")):
                flash("Incorrect password")
                return render_template("settings.html", alert_type="danger", username=username)

            # Query database for a matching username
            if db.execute("SELECT * FROM users WHERE username = ?", new_username):
                flash("Username already in use")
                return render_template("settings.html", alert_type="warning", username=username)

            # Update username if no errors found
            db.execute("UPDATE users SET username = ? WHERE id = ?",
                       new_username, session["user_id"])
            flash(f"Username successfully changed to {new_username}")
            return render_template("settings.html", alert_type="success", username=new_username)

        # Change password
        if request.form.get("new-password"):

            # Ensure old password and new password's confirmation were submitted
            if not request.form.get("password-check") or not request.form.get("confirmation"):
                return apology(MORDOR[0], MORDOR[1])

            # Check that the password is correct
            if not check_password_hash(old_password_hash[0]["hash"], request.form.get("password-check")):
                flash("Incorrect password")
                return render_template("settings.html", alert_type="danger", username=username)

            # Check that the new password and password confirmation match
            if request.form.get("new-password") != request.form.get("confirmation"):
                flash("Passwords don't match")
                return render_template("settings.html", alert_type="danger", username=username)

            # Don't accept the same password as before
            if check_password_hash(old_password_hash[0]["hash"], request.form.get("new-password")):
                flash("Use a different password than before")
                return render_template("settings.html", alert_type="warning", username=username)

            # Change password if no errors found
            new_password = generate_password_hash(
                request.form.get("new-password"))
            db.execute("UPDATE users SET hash = ? WHERE id = ?",
                       new_password, session["user_id"])
            flash("Password successfully updated!")
            return render_template("settings.html", alert_type="success", username=username)

        # Deposit cash
        if request.form.get("cash-deposit"):
            deposit = int(request.form.get("cash-deposit"))

            if deposit < 1:
                return apology(MORDOR[0], MORDOR[1])

            balance = db.execute(
                "SELECT cash FROM users WHERE id = ?", session["user_id"])
            db.execute("UPDATE users SET cash = ? WHERE id = ?",
                       deposit + balance[0]["cash"], session["user_id"])
            db.execute("INSERT INTO transactions (user_id, symbol, price) VALUES (?, ?, ?)",
                       session["user_id"], "cash_deposit", deposit)
            flash("Deposit successful")
            return render_template("settings.html", alert_type="success", username=username)

        # Delete account
        if request.form.get("password-delete"):

            # Check that the password is correct
            if not check_password_hash(old_password_hash[0]["hash"], request.form.get("password-delete")):
                flash("Incorrect password")
                return render_template("settings.html", alert_type="danger", username=username)

            # Delete account and transactions linked to the account
            db.execute("DELETE FROM transactions WHERE user_id = ?",
                       session["user_id"])
            db.execute("DELETE FROM portfolios WHERE user_id = ?",
                       session["user_id"])
            db.execute("DELETE FROM users WHERE id = ?", session["user_id"])
            session.clear()
            return redirect("/")

        # If the user has submitted a form without required information (by modifying HTML), return apology
        return apology(MORDOR[0], MORDOR[1])

    # Render settings.html on GET
    if request.method == "GET":
        return render_template("settings.html", username=username)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
