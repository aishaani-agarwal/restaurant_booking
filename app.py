from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = "replace_this_with_a_random_secret_in_prod"

# helper validators
def valid_phone(phone: str) -> bool:
    return bool(re.fullmatch(r"\d{10}", phone))

def valid_people(ppl: str) -> bool:
    try:
        v = int(ppl)
        return 1 <= v <= 50
    except:
        return False

def valid_table(t: str) -> bool:
    try:
        v = int(t)
        return 1 <= v <= 15
    except:
        return False

def valid_rating(r: str) -> bool:
    try:
        v = float(r)
        return 0.0 <= v <= 5.0
    except:
        return False

@app.route('/')
def index():
    session.clear()
    today = datetime.now().strftime("%Y-%m-%d")
    return render_template('index.html', today=today)

@app.route('/user', methods=['POST'])
def user():
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    date = request.form.get('date', '').strip()
    people = request.form.get('people', '').strip()
    time_slot = request.form.get('time', '').strip()

    # server-side validation
    if not name:
        flash("Name is required.", "danger")
        return redirect(url_for('index'))

    if not valid_phone(phone):
        flash("Phone number must be exactly 10 digits.", "danger")
        return redirect(url_for('index'))

    # validate date (basic)
    if not date:
        flash("Reservation date is required.", "danger")
        return redirect(url_for('index'))
    try:
        # store it as YYYY-MM-DD string; you can format later
        dt = datetime.fromisoformat(date)
        # optional: don't allow past dates
        if dt.date() < datetime.now().date():
            flash("Reservation date cannot be in the past.", "danger")
            return redirect(url_for('index'))
    except Exception:
        flash("Invalid date format.", "danger")
        return redirect(url_for('index'))

    if not valid_people(people):
        flash("Number of people must be a number between 1 and 50.", "danger")
        return redirect(url_for('index'))

    # store in session
    session['name'] = name
    session['phone'] = phone
    session['date'] = date
    session['people'] = int(people)
    session['time'] = time_slot

    return redirect(url_for('location'))

@app.route('/location', methods=['GET', 'POST'])
def location():
    locations = ["Jayanagar", "Indiranagar", "Sarjapur Road"]
    if request.method == 'POST':
        loc = request.form.get('location')
        if loc not in locations:
            flash("Please choose a valid location.", "danger")
            return redirect(url_for('location'))
        session['location'] = loc
        return redirect(url_for('pricerange'))
    return render_template('location.html', locations=locations)

@app.route('/pricerange', methods=['GET', 'POST'])
def pricerange():
    ranges = ["₹50-₹500", "₹500-₹2000", "₹2000-₹5000"]
    if request.method == 'POST':
        pr = request.form.get('pricerange')
        if pr not in ranges:
            flash("Please choose a valid price range.", "danger")
            return redirect(url_for('pricerange'))
        session['pricerange'] = pr
        return redirect(url_for('cuisine'))
    return render_template('pricerange.html', ranges=ranges)

@app.route('/cuisine', methods=['GET', 'POST'])
def cuisine():
    cuisines = ["Indian", "Italian", "Chinese"]
    if request.method == 'POST':
        cu = request.form.get('cuisine')
        if cu not in cuisines:
            flash("Please choose a valid cuisine.", "danger")
            return redirect(url_for('cuisine'))
        session['cuisine'] = cu
        return redirect(url_for('ambience'))
    return render_template('cuisine.html', cuisines=cuisines)

@app.route('/ambience', methods=['GET', 'POST'])
def ambience():
    ambs = ["Fine Dining", "Buffet", "Cafe"]
    if request.method == 'POST':
        a = request.form.get('ambience')
        if a not in ambs:
            flash("Please choose a valid ambience.", "danger")
            return redirect(url_for('ambience'))
        session['ambience'] = a
        return redirect(url_for('restaurant'))
    return render_template('ambience.html', ambs=ambs)

@app.route('/restaurant', methods=['GET', 'POST'])
def restaurant():
    restaurants = ["Karavalli @ Taj", "Hard Rock Cafe", "Zoey's"]
    if request.method == 'POST':
        r = request.form.get('restaurant')
        if r not in restaurants:
            flash("Please choose a valid restaurant.", "danger")
            return redirect(url_for('restaurant'))
        session['restaurant'] = r
        return redirect(url_for('table'))
    return render_template('restaurant.html', restaurants=restaurants)

@app.route('/table', methods=['GET', 'POST'])
def table():
    if request.method == 'POST':
        table_no = request.form.get('table', '').strip()
        if not valid_table(table_no):
            flash("Table must be a number between 1 and 15.", "danger")
            return redirect(url_for('table'))
        session['table'] = int(table_no)
        return redirect(url_for('confirmation'))
    return render_template('table.html')

@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    if 'name' not in session:
        flash("Please start a booking first.", "warning")
        return redirect(url_for('index'))

    if request.method == 'POST':
        # user confirmed; go to rating
        return redirect(url_for('rating'))
    # present current booking data
    data = dict(session)
    # format date nicely
    try:
        data['date'] = datetime.fromisoformat(data['date']).strftime("%d/%m/%Y")
    except:
        pass
    return render_template('confirmation.html', data=data)

@app.route('/rating', methods=['GET', 'POST'])
def rating():
    if request.method == 'POST':
        rating_val = request.form.get('rating', '').strip()
        feedback = request.form.get('feedback', '').strip()
        if not valid_rating(rating_val):
            flash("Rating must be between 0 and 5.", "danger")
            return redirect(url_for('rating'))
        session['rating'] = float(rating_val)
        session['feedback'] = feedback
        # reward points logic (simple)
        session['reward_points'] = 10000
        return render_template('thankyou.html', data=dict(session))
    return render_template('rating.html')

if __name__ == "__main__":
    app.run(debug=True, port=5001)

