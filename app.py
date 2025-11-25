from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from functools import wraps
from flask import jsonify


app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="gauri@sql",  # <-- change to your MySQL password
        database="NutriGym"          # <-- change to your database name
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def calculate_nutrition(age, weight, gender, goal, gym_hours):
    # 1. Set a realistic, low calorie base
    if gender == 'female':
        base_calories = 1600
    else:
        base_calories = 1800

    # 2. Add a small bonus for gym hours (50 kcal per hour)
    calories = base_calories + gym_hours * 50

    # 3. Adjust for goal
    if goal == 'lose':
        calories -= 150
    elif goal == 'gain':
        calories += 150

    # 4. Set macro upper limits
    max_protein = round(weight * 0.8)  # in grams
    max_protein_cal = max_protein * 4

    max_carb_cal = calories * 0.55
    max_carbs = round(max_carb_cal / 4)

    max_fat_cal = calories * 0.3
    max_fats = round(max_fat_cal / 9)

    return {
        'calories': int(calories),
        'protein': max_protein,
        'carbs': max_carbs,
        'fats': max_fats
    }

def suggest_meal_plan(recipes, requirements):
    plan = []
    total = {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0}

    # Sort recipes by calories (or any macro you want to prioritize)
    sorted_recipes = sorted(
        recipes,
        key=lambda r: r['calories'],
        reverse=True
    )

    for recipe in sorted_recipes:
        if not all(recipe.get(k, 0) > 0 for k in ['calories', 'protein', 'carbs', 'fats']):
            continue

        max_possible = 0
        # Try up to 5 portions, but never exceed any macro
        for qty in range(1, 6):
            next_totals = {
                'calories': total['calories'] + recipe['calories'] * qty,
                'protein': total['protein'] + recipe['protein'] * qty,
                'carbs': total['carbs'] + recipe['carbs'] * qty,
                'fats': total['fats'] + recipe['fats'] * qty,
            }
            # Check if any macro would be exceeded
            if (next_totals['calories'] > requirements['calories'] or
                next_totals['protein'] > requirements['protein'] or
                next_totals['carbs'] > requirements['carbs'] or
                next_totals['fats'] > requirements['fats']):
                break
            max_possible = qty

        if max_possible > 0:
            plan.append({
                'id': recipe['id'],
                'name': recipe['name'],
                'quantity': max_possible,
                'calories': recipe['calories'] * max_possible,
                'protein': recipe['protein'] * max_possible,
                'carbs': recipe['carbs'] * max_possible,
                'fats': recipe['fats'] * max_possible,
            })
            # Update totals
            total['calories'] += recipe['calories'] * max_possible
            total['protein'] += recipe['protein'] * max_possible
            total['carbs'] += recipe['carbs'] * max_possible
            total['fats'] += recipe['fats'] * max_possible

        # Stop if all macros are close enough (within 5% of requirements)
        if all(total[k] >= 0.95 * requirements[k] for k in requirements):
            break

    return plan

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/recipes', methods=['GET', 'POST'])
@login_required
def recipes():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['name']
        type_ = request.form['type']
        image_url = request.form.get('image_url') or None
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        # Get nutrition info from user input
        calories = request.form.get('calories') or 0
        protein = request.form.get('protein') or 0
        carbs = request.form.get('carbs') or 0
        fats = request.form.get('fats') or 0
        cursor.execute(
            "INSERT INTO recipes (user_id, name, type, image_url, ingredients, instructions, calories, protein, carbs, fats, is_approved) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)",
            (session['user_id'], name, type_, image_url, ingredients, instructions, calories, protein, carbs, fats)
        )
        db.commit()
        flash('Recipe submitted! Awaiting admin approval.', 'info')

    # Filtering logic
    query = "SELECT * FROM recipes WHERE is_approved=1"
    params = []
    selected_type = request.args.get('type')
    search = request.args.get('search')
    max_calories = request.args.get('max_calories')
    if selected_type in ['breakfast', 'salad', 'smoothie']:
        query += " AND type=%s"
        params.append(selected_type)
    if search:
        query += " AND (name LIKE %s OR ingredients LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])
    if max_calories:
        query += " AND (calories IS NULL OR calories <= %s)"
        params.append(max_calories)
    cursor.execute(query, tuple(params))
    recipes = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template(
        'recipes.html',
        recipes=recipes,
        selected_type=selected_type,
        search=search,
        max_calories=max_calories
    )

@app.route('/recipe/<int:recipe_id>')
@login_required
def recipe_detail(recipe_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM recipes WHERE id=%s AND is_approved=1", (recipe_id,))
    recipe = cursor.fetchone()
    cursor.close()
    db.close()
    if not recipe:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('recipes'))
    return render_template('recipe_detail.html', recipe=recipe)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                           (username, email, password))
            db.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error:
            flash('Username or email already exists.', 'danger')
        finally:
            cursor.close()
            db.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM recipes WHERE is_approved=1")
    all_recipes = cursor.fetchall()
    cursor.execute("SELECT age, weight, gender, goal FROM users WHERE id=%s", (session['user_id'],))
    user_profile = cursor.fetchone()
    cursor.close()
    db.close()
    # Group recipes by type
    recipes_by_type = {
        'breakfast': [r for r in all_recipes if r['type'] == 'breakfast'],
        'salad': [r for r in all_recipes if r['type'] == 'salad'],
        'smoothie': [r for r in all_recipes if r['type'] == 'smoothie'],
    }
    return render_template(
        'dashboard.html',
        recipes_by_type=recipes_by_type,
        username=session['username'],
        is_admin=session.get('is_admin'),
        user_profile=user_profile
    )


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    user_id = session['user_id']
    if request.method == 'POST':
        age = request.form.get('age')
        weight = request.form.get('weight')
        gender = request.form.get('gender')
        goal = request.form.get('goal')
        try:
            cursor.execute("""
                UPDATE users SET age=%s, weight=%s, gender=%s, goal=%s WHERE id=%s
            """, (age, weight, gender, goal, user_id))
            db.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            flash('Error updating profile.', 'danger')
    cursor.execute("SELECT age, weight, gender, goal FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return render_template('profile.html', user=user)

@app.route('/gym', methods=['GET', 'POST'])
@login_required
def gym():
    nutrition = None
    requirements = None
    meal_plan = []
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT age, weight, gender, goal FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()

    if request.method == 'POST':
        gym_hours = int(request.form['gym_hours'])
        nutrition = calculate_nutrition(
            age=user['age'] or 25,
            weight=user['weight'] or 70,
            gender=user['gender'] or 'male',
            goal=user['goal'] or 'maintain',
            gym_hours=gym_hours
        )
        requirements = {
            'calories': nutrition['calories'],
            'protein': nutrition['protein'],
            'carbs': nutrition['carbs'],
            'fats': nutrition['fats']
        }
        # Fetch recipes and suggest meal plan
        cursor.execute("SELECT * FROM recipes WHERE is_approved=1")
        recipes = cursor.fetchall()
        meal_plan = suggest_meal_plan(recipes, requirements)
    cursor.close()
    db.close()
    return render_template('gym.html', requirements=requirements, meal_plan=meal_plan, nutrition=nutrition)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not session.get('is_admin'):
        flash('Admin access required.', 'danger')
        return redirect(url_for('dashboard'))
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        recipe_id = request.form['recipe_id']
        cursor.execute("UPDATE recipes SET is_approved=1 WHERE id=%s", (recipe_id,))
        db.commit()
        flash('Recipe approved!', 'success')
    cursor.execute("SELECT * FROM recipes WHERE is_approved=0")
    pending = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('admin.html', pending=pending)


# API for AI agent (optional, simple logic)
@app.route('/api/nutrition', methods=['POST'])
@login_required
def api_nutrition():
    data = request.json
    gym_hours = data.get('gym_hours')
    gym_time = data.get('gym_time')
    # Simple AI: more hours = more calories/protein
    base = {'calories': 2000, 'protein': 100, 'carbs': 250, 'fats': 70}
    if gym_hours and gym_time:
        base['calories'] += gym_hours * 200
        base['protein'] += gym_hours * 20
    return jsonify(base)

if __name__ == '__main__':
    app.run(debug=True)

