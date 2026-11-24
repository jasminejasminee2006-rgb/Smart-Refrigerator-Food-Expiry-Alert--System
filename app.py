from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "food.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            expiry TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            location TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():

    conn = get_db()

    foods_data = conn.execute(
        "SELECT * FROM foods ORDER BY expiry ASC"
    ).fetchall()

    conn.close()

    today = datetime.now().date()

    foods = []

    fresh = 0
    near_expiry = 0
    expired = 0

    for food in foods_data:

        expiry_date = datetime.strptime(
            food["expiry"],
            "%Y-%m-%d"
        ).date()

        days_left = (expiry_date - today).days

        if days_left < 0:
            status = "Expired"
            expired += 1

        elif days_left <= 3:
            status = "Near Expiry"
            near_expiry += 1

        else:
            status = "Fresh"
            fresh += 1

        foods.append({
            "id": food["id"],
            "name": food["name"],
            "expiry": food["expiry"],
            "category": food["category"],
            "quantity": food["quantity"],
            "location": food["location"],
            "days_left": days_left,
            "status": status
        })

    return render_template(
        "index.html",
        foods=foods,
        total=len(foods),
        fresh=fresh,
        near_expiry=near_expiry,
        expired=expired
    )


@app.route("/add", methods=["POST"])
def add_food():

    name = request.form["food_name"]
    expiry = request.form["expiry_date"]
    category = request.form["category"]
    quantity = request.form["quantity"]
    location = request.form["location"]

    conn = get_db()

    conn.execute(
        """
        INSERT INTO foods
        (name, expiry, category, quantity, location)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            name,
            expiry,
            category,
            quantity,
            location
        )
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/edit/<int:food_id>", methods=["GET", "POST"])
def edit_food(food_id):

    conn = get_db()

    if request.method == "POST":

        name = request.form["food_name"]
        expiry = request.form["expiry_date"]
        category = request.form["category"]
        quantity = request.form["quantity"]
        location = request.form["location"]

        conn.execute(
            """
            UPDATE foods
            SET name = ?,
                expiry = ?,
                category = ?,
                quantity = ?,
                location = ?
            WHERE id = ?
            """,
            (
                name,
                expiry,
                category,
                quantity,
                location,
                food_id
            )
        )

        conn.commit()
        conn.close()

        return redirect("/")

    food = conn.execute(
        "SELECT * FROM foods WHERE id = ?",
        (food_id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit.html",
        food=food
    )


@app.route("/delete/<int:food_id>")
def delete_food(food_id):

    conn = get_db()

    conn.execute(
        "DELETE FROM foods WHERE id = ?",
        (food_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    create_database()
    app.run(debug=True)