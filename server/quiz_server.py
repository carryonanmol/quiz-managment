# quiz_server.py
# Main application file for the Flask backend server.

import os
import sqlite3
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# --- App Configuration ---
app = Flask(__name__)
DATABASE = 'quiz_system.db'
app.config['SECRET_KEY'] = 'a_super_secret_key_for_jwt_or_sessions'

# --- Database Setup ---
def get_db():
    """Establishes a connection to the SQLite database."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_database():
    """
    Initializes the database ONLY if the file does not exist.
    Data will now persist between server restarts.
    """
    if os.path.exists(DATABASE):
        print("Database already exists.")
        return

    print("Creating a new database...")
    try:
        db = get_db()
        with open('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

        # Add default users for easy testing
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO User (username, password_hash, role) VALUES (?, ?, ?)",
            ('admin', generate_password_hash('admin123'), 'Admin')
        )
        cursor.execute(
            "INSERT INTO User (username, password_hash, role) VALUES (?, ?, ?)",
            ('student', generate_password_hash('student123'), 'Student')
        )
        db.commit()
        print("Database initialized with default users (admin/admin123, student/student123).")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        if 'db' in locals() and db:
            db.close()

# --- API Endpoints ---

@app.route('/register', methods=['POST'])
def register():
    """Handles new user registration."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'Student') # Default role to Student

        if not username or not password:
            return jsonify({"success": False, "message": "Username and password are required."}), 400

        db = get_db()
        cursor = db.cursor()
        
        user = cursor.execute('SELECT * FROM User WHERE username = ?', (username,)).fetchone()
        if user:
            db.close()
            return jsonify({"success": False, "message": "Username already taken."}), 409

        cursor.execute(
            "INSERT INTO User (username, password_hash, role) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), role)
        )
        db.commit()
        user_id = cursor.lastrowid
        db.close()
        
        return jsonify({
            "success": True, 
            "message": "User registered successfully!", 
            "user_id": user_id
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@app.route('/login', methods=['POST'])
def login():
    """Handles user login requests."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"success": False, "message": "Username and password are required."}), 400

        db = get_db()
        user = db.execute('SELECT * FROM User WHERE username = ?', (username,)).fetchone()
        db.close()

        if user and check_password_hash(user['password_hash'], password):
            return jsonify({
                "success": True,
                "message": "Login successful!",
                "user": { "user_id": user['user_id'], "username": user['username'], "role": user['role'] }
            }), 200
        else:
            return jsonify({"success": False, "message": "Invalid username or password."}), 401
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@app.route('/quizzes', methods=['POST'])
def create_quiz():
    """Endpoint for an Admin to create a new quiz."""
    try:
        data = request.get_json()
        title, time_limit, creator_id = data.get('title'), data.get('time_limit_minutes'), data.get('creator_id')

        if not all([title, time_limit, creator_id]):
            return jsonify({"success": False, "message": "Missing required fields."}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO Quiz (title, time_limit_minutes, creator_id) VALUES (?, ?, ?)", (title, time_limit, creator_id))
        db.commit()
        quiz_id = cursor.lastrowid
        db.close()
        return jsonify({"success": True, "message": "Quiz created successfully!", "quiz_id": quiz_id}), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@app.route('/quizzes', methods=['GET'])
def get_all_quizzes():
    """Endpoint to get a list of all available quizzes."""
    try:
        db = get_db()
        quizzes_cursor = db.execute('SELECT quiz_id, title, time_limit_minutes FROM Quiz').fetchall()
        db.close()
        return jsonify({"success": True, "quizzes": [dict(row) for row in quizzes_cursor]}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@app.route('/quizzes/<int:quiz_id>', methods=['GET'])
def get_quiz_details(quiz_id):
    """Endpoint to get details and all questions for a specific quiz (for students)."""
    try:
        db = get_db()
        quiz_details = db.execute('SELECT title, time_limit_minutes FROM Quiz WHERE quiz_id = ?', (quiz_id,)).fetchone()
        if not quiz_details:
            return jsonify({"success": False, "message": "Quiz not found."}), 404
        
        questions_cursor = db.execute(
            'SELECT question_id, question_text, option_a, option_b, option_c, option_d FROM Question WHERE quiz_id = ?', (quiz_id,)
        ).fetchall()
        db.close()
        
        quiz_data = dict(quiz_details)
        quiz_data['questions'] = [dict(q) for q in questions_cursor]
        
        return jsonify({"success": True, "quiz": quiz_data}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

# --- THIS IS THE NEW FUNCTION THAT WAS MISSING ---
@app.route('/quizzes/<int:quiz_id>/all-questions', methods=['GET'])
def get_quiz_questions_admin(quiz_id):
    """Endpoint for an Admin to get all questions for a quiz (includes correct answer)."""
    try:
        db = get_db()
        questions_cursor = db.execute(
            'SELECT question_id, question_text, option_a, option_b, option_c, option_d, correct_option FROM Question WHERE quiz_id = ?', (quiz_id,)
        ).fetchall()
        db.close()
        
        questions_list = [dict(q) for q in questions_cursor]
        
        return jsonify({"success": True, "questions": questions_list}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500
# --- END OF NEW FUNCTION ---

@app.route('/quizzes/<int:quiz_id>/questions', methods=['POST'])
def add_question_to_quiz(quiz_id):
    """Endpoint for an Admin to add a question to a specific quiz."""
    try:
        data = request.get_json()
        keys = ["question_text", "option_a", "option_b", "option_c", "option_d", "correct_option"]
        if not all(key in data for key in keys):
            return jsonify({"success": False, "message": "All question fields are required."}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO Question (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (quiz_id, data['question_text'], data['option_a'], data['option_b'], data['option_c'], data['option_d'], data['correct_option'])
        )
        db.commit()
        question_id = cursor.lastrowid
        db.close()
        return jsonify({"success": True, "message": f"Question added to quiz {quiz_id}!", "question_id": question_id}), 201
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@app.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
def submit_quiz(quiz_id):
    """Endpoint for a student to submit their answers."""
    try:
        data = request.get_json()
        user_id, answers = data.get('user_id'), data.get('answers', [])

        db = get_db()
        correct_answers_cursor = db.execute('SELECT question_id, correct_option FROM Question WHERE quiz_id = ?', (quiz_id,)).fetchall()
        if not correct_answers_cursor:
            return jsonify({"success": False, "message": "Quiz has no questions or does not exist."}), 404
        
        correct_answers = {row['question_id']: row['correct_option'] for row in correct_answers_cursor}
        
        score = 0
        if isinstance(answers, list):
            for answer in answers:
                q_id, user_ans = answer.get('question_id'), answer.get('answer')
                if correct_answers.get(q_id) == user_ans:
                    score += 1
        
        total = len(correct_answers)
        percentage = (score / total) * 100 if total > 0 else 0
        
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Result (user_id, quiz_id, score, total_questions) VALUES (?, ?, ?, ?)",
            (user_id, quiz_id, score, total)
        )
        db.commit()
        db.close()
        
        return jsonify({
            "success": True, "message": "Quiz submitted successfully!", "score": score,
            "total_questions": total, "percentage": round(percentage, 2)
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@app.route('/results/<int:user_id>', methods=['GET'])
def get_user_results(user_id):
    """Endpoint to get all results for a specific student."""
    try:
        db = get_db()
        results_cursor = db.execute(
            """SELECT Q.title, R.score, R.total_questions, R.timestamp
               FROM Result R
               JOIN Quiz Q ON R.quiz_id = Q.quiz_id
               WHERE R.user_id = ?
               ORDER BY R.timestamp DESC""",
            (user_id,)
        ).fetchall()
        db.close()
        return jsonify({"success": True, "results": [dict(row) for row in results_cursor]}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

@app.route('/results/all', methods=['GET'])
def get_all_results():
    """Endpoint for an Admin to get all results for all students."""
    try:
        db = get_db()
        results_cursor = db.execute(
            """SELECT U.username, Q.title, R.score, R.total_questions, R.timestamp
               FROM Result R
               JOIN User U ON R.user_id = U.user_id
               JOIN Quiz Q ON R.quiz_id = Q.quiz_id
               ORDER BY U.username, R.timestamp DESC"""
        ).fetchall()
        db.close()
        return jsonify({"success": True, "results": [dict(row) for row in results_cursor]}), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"An error occurred: {e}"}), 500

# --- Server Startup ---
if __name__ == '__main__':
    init_database()
    app.run(host='0.0.0.0', port=5000, debug=True)

