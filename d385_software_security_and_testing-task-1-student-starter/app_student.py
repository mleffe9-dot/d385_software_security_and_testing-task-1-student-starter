"""
WGU Construction Equipment Rental - Flask Application (Student Starter)

Scenario:
You have been provided with this partially operational web application.
While it "works" (the site loads and processes requests), it is fragile and insecure.
Previous logs (`network_security_log.txt`) indicate several issues:
1. Application crashes (Runtime Errors).
2. Security vulnerabilities (Unrestricted inputs, suspicious IPs).
3. Lack of real-time logging (Blind spots).

Your Task:
1. Analyze the `network_security_log.txt` to understand the past issues.
2. Review the `static_analysis_report.txt` to see vulnerabilities detected by
   static analysis tools (Flake8 and Bandit) - supports Rubric Aspect A9.
3. Modify this file (`app_student.py`) to:
   - Configure Python's logging module to write to 'Troubleshooting_studentID.log'.
   - Add defensive coding (Assertions, Try/Except blocks) to prevent crashes.
   - Add proper validation (e.g., check for negative days, invalid users).
   - Log all significant events (INFO) and errors (WARNING/ERROR).

Static Analysis Tools Used:
- Flake8: Code quality and PEP 8 style checking (run: python -m flake8 app_student.py)
- Bandit: Security vulnerability detection (run: python -m bandit app_student.py)
"""

import logging

logging.basicConfig(
    filename='Troubleshooting_studentID.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'supersecretkeyforflasksessions'

# ------------------------------------------------------------------------------------------------------------


# Equipment Pricing Data
EQUIPMENT_PRICES = {
    "Bulldozer": 500,
    "Excavator": 450,
    "Crane": 800
}

# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------

def validate_username(username):
    """
    Validates that the username is allowed.
    Currently insecure: it returns True for almost anything!
    """
    assert isinstance(username, str), "Username must be a string"
    assert username.strip() != "", "Username cannot be empty"
    logging.info("ASSERTION PASSED: Username is a valid non-empty string")
    
    allowed_users = {"admin", "alice", "bob", "charlie"}
    if username in allowed_users:
        return True
    return False

# ------------------------------------------------------------
# Routes
# ------------------------------------------------------------

@app.route('/')
def home():
    logging.info("EVENT: Home page accessed")
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Simulated IP address (In a real app, this would be request.remote_addr)
        ip_address = request.remote_addr 
        
        logging.info(f"EVENT: Login attempt - Username: {username}, IP: {ip_address}")

        # Assertion to validate IP address
        assert ip_address is not None and isinstance(ip_address, str), "Invalid IP address"
        logging.info(f"ASSERTION PASSED: Valid IP address detected - {ip_address}")

        # Suspicious IP check
        if not (ip_address.startswith("192.168.") or ip_address.startswith("10.")):
            logging.warning(f"ACTION: Suspicious IP detected - {ip_address}")
        
        # Authentication Logic
        if validate_username(username) and password == "secret123":
            # TODO: Log successful login
            logging.info(f"EVENT: User {username} logged in.")
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for('home'))
        else:
            # TODO: Log failed login (WARNING)
            logging.warning(f"ACTION: Login failed for {username}.")
            flash("Invalid credentials.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/rent', methods=['GET', 'POST'])
def rent_equipment():
    rental_result = None
    
    if request.method == 'POST':
        equipment_type = request.form.get("equipment_type")
        days_str = request.form.get("days")

        logging.info(f"EVENT: Rental request received - Equipment: {equipment_type}, Days: {days_str}")

        # --- VULNERABLE SECTION START ---
        try:
            daily_rate = EQUIPMENT_PRICES[equipment_type]
        except KeyError:
            logging.error(f"ERROR: Invalid equipment type selected: {equipment_type}")
            flash("Invalid equipment type selected.", "danger")
            return render_template('rent.html', rental_result=None)
            
        try:
            days = int(days_str)
        except ValueError:
            logging.warning(f"WARNING: Invalid input for days: {days_str}")
            flash("Please enter a valid number of days.", "danger")
            return render_template('rent.html', rental_result=None)
        
        if days <= 0:
            logging.warning(f"WARNING: Invalid number of days (must be > 0): {days}")
            flash("Number of days must be greater than zero.", "danger")
            return render_template('rent.html', rental_result=None)
        
        total_cost = daily_rate * days
        
        logging.info(f"ACTION: Calculated cost: {total_cost}")

        rental_result = {
            "equipment": equipment_type,
            "days": days,
            "total_cost": total_cost
        }
        flash("Rental calculated successfully!", "success")
        
        # --- VULNERABLE SECTION END ---
        

    return render_template('rent.html', rental_result=rental_result)

if __name__ == '__main__':
    logging.info("EVENT: Starting application...")
    app.run(debug=False, port=5000)