import mysql.connector
import re
from datetime import datetime

# ---------- DB connection ----------
def connect_db(user='root', password='qwer123', host='localhost'):
    # Connects to MySQL server (doesn't require DB to exist yet)
    return mysql.connector.connect(host=host, user=user, password=password)

def ensure_db_and_tables(user='root', password='qwer123', host='localhost'):
    conn = connect_db(user, password, host)
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS feedback_db;")
    cursor.execute("USE feedback_db;")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        feedback_id INT AUTO_INCREMENT PRIMARY KEY,
        user_name VARCHAR(100),
        email VARCHAR(150),
        comments TEXT NOT NULL,
        rating TINYINT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sentimental_feedback (
        sentiment_id INT AUTO_INCREMENT PRIMARY KEY,
        feedback_id INT NOT NULL,
        sentiment_label ENUM('positive','neutral','negative') NOT NULL,
        sentiment_score DECIMAL(6,4) NOT NULL,
        matched_keywords VARCHAR(255),
        analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (feedback_id) REFERENCES feedback(feedback_id) ON DELETE CASCADE
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()

# ---------- Simple rule-based sentiment analyzer ----------
POSITIVE_WORDS = {
    'good','great','excellent','amazing','awesome','nice','tasty','delicious','perfect','pleasant',
    'love','loved','like','liked','satisfied','best','superb','fresh','friendly','clean','recommend',
    'enjoy','enjoyed','fantastic','wonderful','happy','yum','yummy','value','affordable','prompt'
}

NEGATIVE_WORDS = {
    'bad','terrible','awful','horrible','disappoint','disappointed','hate','hated','poor','cold',
    'bland','burnt','late','slow','rude','dirty','stale','overpriced','expensive','sick','sour',
    'undercooked','raw','worse','worst','problem','issue','dry','not'
}

def simple_sentiment_analysis(text):
    # Normalize and tokenize words (basic)
    words = re.findall(r"\b[a-zA-Z']+\b", text.lower())
    if not words:
        return 0.0, 'neutral', ''

    pos_matches = [w for w in words if w in POSITIVE_WORDS]
    neg_matches = [w for w in words if w in NEGATIVE_WORDS]

    pos_count = len(pos_matches)
    neg_count = len(neg_matches)
    total = len(words)

    # Score in range [-1.0, 1.0] with simple formula
    score = (pos_count - neg_count) / total
    # Round score
    score = round(score, 4)

    # Thresholds to label sentiment
    if score > 0.03 and pos_count > neg_count:
        label = 'positive'
    elif score < -0.03 and neg_count > pos_count:
        label = 'negative'
    else:
        label = 'neutral'

    # Prepare matched keywords (unique, limited length)
    keywords = list(dict.fromkeys(pos_matches + neg_matches))  # preserve order, unique
    matched = ','.join(keywords)[:250]  # limit to 250 chars

    return score, label, matched

# ---------- Insert feedback and auto-analyze ----------
def submit_feedback(user='root', password='qwer123', host='localhost'):
    # collect input
    name = input("Enter your name (optional): ").strip()
    email = input("Enter your email (optional): ").strip()
    comments = input("Enter feedback comments (required): ").strip()
    if not comments:
        print("Feedback comments cannot be empty.")
        return
    rating_input = input("Enter rating (1-5) or press Enter to skip: ").strip()
    rating = int(rating_input) if rating_input.isdigit() and 1 <= int(rating_input) <= 5 else None

    # ensure DB/tables exist
    ensure_db_and_tables(user, password, host)
    conn = mysql.connector.connect(host=host, user=user, password=password, database='feedback_db')
    cursor = conn.cursor()

    # insert into feedback
    cursor.execute(
        "INSERT INTO feedback (user_name, email, comments, rating) VALUES (%s, %s, %s, %s)",
        (name or None, email or None, comments, rating)
    )
    conn.commit()
    feedback_id = cursor.lastrowid
    print(f"Inserted feedback with ID: {feedback_id}")

    # analyze sentiment
    score, label, matched = simple_sentiment_analysis(comments)
    cursor.execute(
        "INSERT INTO sentimental_feedback (feedback_id, sentiment_label, sentiment_score, matched_keywords) VALUES (%s, %s, %s, %s)",
        (feedback_id, label, score, matched)
    )
    conn.commit()
    print(f"Analyzed sentiment: {label} (score: {score}), keywords: {matched or 'None'}")

    cursor.close()
    conn.close()

# ---------- View feedbacks and sentiment ----------
def view_all_feedbacks(user='root', password='qwer123', host='localhost'):
    ensure_db_and_tables(user, password, host)
    conn = mysql.connector.connect(host=host, user=user, password=password, database='feedback_db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.feedback_id, f.user_name, f.email, f.comments, f.rating, f.created_at,
               s.sentiment_label, s.sentiment_score, s.matched_keywords, s.analyzed_at
        FROM feedback f
        LEFT JOIN sentimental_feedback s ON f.feedback_id = s.feedback_id
        ORDER BY f.created_at DESC;
    """)
    rows = cursor.fetchall()
    if not rows:
        print("No feedback entries found.")
    else:
        for r in rows:
            print("-" * 60)
            print(f"Feedback ID : {r[0]}")
            print(f"User        : {r[1] or 'Anonymous'}")
            print(f"Email       : {r[2] or 'N/A'}")
            print(f"Comments    : {r[3]}")
            print(f"Rating      : {r[4] or 'N/A'}")
            print(f"Created At  : {r[5]}")
            print(f"Sentiment   : {r[6] or 'N/A'} (score: {r[7] if r[7] is not None else 'N/A'})")
            print(f"Keywords    : {r[8] or 'None'}")
            print(f"Analyzed At : {r[9] or 'N/A'}")
        print("-" * 60)
    cursor.close()
    conn.close()

def analyze_existing_feedback(user='root', password='your_password', host='localhost'):
    conn = mysql.connector.connect(host=host, user=user, password=password, database='feedback_db')
    cursor = conn.cursor()

    # Select feedback without sentiment
    cursor.execute("""
        SELECT feedback_id, comments
        FROM feedback
        WHERE feedback_id NOT IN (SELECT feedback_id FROM sentimental_feedback);
    """)
    rows = cursor.fetchall()

    if not rows:
        print("All feedbacks already analyzed.")
        cursor.close()
        conn.close()
        return

    for feedback_id, comments in rows:
        score, label, matched = simple_sentiment_analysis(comments)
        cursor.execute(
            "INSERT INTO sentimental_feedback (feedback_id, sentiment_label, sentiment_score, matched_keywords) VALUES (%s, %s, %s, %s)",
            (feedback_id, label, score, matched)
        )
        print(f"Feedback ID {feedback_id} analyzed: {label} (score: {score})")

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ All pending feedback analyzed and inserted.")

# ---------- CLI for feedback system ----------
def feedback_cli():
    db_user =  "root"
    db_pass = "qwer123"
    db_host =  'localhost'

    ensure_db_and_tables(db_user, db_pass, db_host)

    while True:
        print("\n=== FEEDBACK SYSTEM ===")
        print("1. Submit new feedback")
        print("2. View all feedback & sentiment")
        print("3. Analyze existing feedback")
        print("0. Exit")
        choice = input("Choice: ").strip()

        if choice == "1":
            submit_feedback(user=db_user, password=db_pass, host=db_host)
        elif choice == "2":
            view_all_feedbacks(user=db_user, password=db_pass, host=db_host)
        elif choice == "3":
            analyze_existing_feedback(user=db_user, password=db_pass, host=db_host)
        elif choice == "0":
            print("Exiting.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    feedback_cli()
