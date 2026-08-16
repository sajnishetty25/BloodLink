from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
# REMOVED: from flask_mysqldb import MySQL
# REMOVED: import MySQLdb.cursors
import mysql.connector # Use direct connector
from server import server
from mainhomepage import app as dash_homepage  # Import Dash homepage
from login import init_login_app  # If you have login as another Dash app
from flask_mail import Mail, Message
import re, random, string
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
# Note: BytesIO, random, string, reportlab imports are already correct

# --- Configuration for Direct DB Connection ---
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "@Pritu50421",
    "database": "final"
}

def get_db_connection():
    """Establishes a new database connection."""
    return mysql.connector.connect(**db_config)

# --- Flask App Setup ---
app = server   # Use the Flask server from the Dash app
login_dash_app = init_login_app(app)
app.secret_key = 's3cr3t_k3y_123!@#'

# REMOVED: MySQL Configuration (Not needed for direct connector)
# app.config['MYSQL_HOST'] = 'localhost'
# ... and so on
# REMOVED: mysql = MySQL(app) 

# Flask-Mail Configuration (Gmail SMTP)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'priteshshetty89@gmail.com'
app.config['MAIL_PASSWORD'] = 'ecfa kequ dpep shxy'
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@gmail.com'

mail = Mail(app)

# Function to send email
def send_email(to, subject, body):
    try:
        msg = Message(subject, recipients=[to])
        msg.body = body
        mail.send(msg)
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

# Home Route (Redirects to Dash App)
@app.route('/')
def home():
    return render_template('homepage.html') 

# Registration Page with Email Notification
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and all(key in request.form for key in ['name', 'email', 'password', 'dob', 'bloodgroup', 'phone']):
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        dob = request.form['dob']
        bloodgroup = request.form['bloodgroup']
        phone = request.form['phone']
        
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            # Use dictionary=True for DictCursor-like functionality
            cursor = conn.cursor(dictionary=True) 
            
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            account = cursor.fetchone()

            if account:
                flash('Account already exists!', 'error')
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('Invalid email address!', 'error')
            else:
                cursor.execute(
                    'INSERT INTO users (name, email, bloodgroup, dob, phone, password) VALUES (%s, %s, %s, %s, %s, %s)',
                    (name, email, bloodgroup, dob, phone, password)
                )
                conn.commit() # Use conn.commit()
                flash('🎉 Registration  is sucessfull', 'success')
                session['redirect'] = True  
                return redirect(url_for('register')) 
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'error')
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template('register.html')

# Login Page
@app.route('/login/', methods=['GET', 'POST'])
def login(): 
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        conn = None
        cursor = None

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True) # Use dictionary=True for DictCursor-like functionality
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            account = cursor.fetchone()

            if account and account['password'] == password:
                flash('Logged in successfully!', 'success')
                session["user_id"] = account["id"]
                session['username'] = account['name']
                session['blood_group'] = account['bloodgroup']
                return redirect(url_for('dash'))  # Redirect to dashboard after successful login
            else:
                flash('Incorrect username or password!', 'error')
                return render_template('login.html')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
            return render_template('login.html')
        finally:
            # Always close cursor and connection
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
    return render_template('login.html')

@app.route('/dash')
def dash():
    return render_template('index.html')

@app.route('/select_timeslot', methods=['POST'])
def select_timeslot():
    # This route is purely static and doesn't require DB access, so no changes needed
    try:
        data = request.get_json()
        bloodbank_id = data.get('bloodbank')

        if not bloodbank_id:
            return jsonify({'error': 'Blood bank ID is required'}), 400

        # Predefined static slots
        timeslots = [
            {"id": 1, "slot": "9:00 AM - 12:00 PM"},
            {"id": 2, "slot": "1:00 PM - 3:00 PM"},
            {"id": 3, "slot": "4:00 PM - 6:00 PM"}
        ]

        return jsonify(timeslots)
    
    except Exception as e:
        print("Error in select_timeslot:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/bloodbank/register', methods=['GET', 'POST'])
def register_bloodbank():
    if request.method == 'POST' and all(key in request.form for key in ['bloodbank', 'govt_id', 'email', 'contact', 'city', 'username', 'password']):
        bloodbank = request.form['bloodbank']
        govt_id = request.form['govt_id']
        email = request.form['email']
        contact = request.form['contact']
        city = request.form['city']
        username = request.form['username']
        password = request.form['password']
        
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT * FROM bloodbanks WHERE email = %s OR username = %s', (email, username))
            account = cursor.fetchone()

            if account:
                flash('⚠️ Account with this email or username already exists!', 'error')
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('⚠️ Invalid email address!', 'error')
            elif not all([bloodbank, govt_id, email, contact, city, username, password]):
                flash('⚠️ Please fill out all fields!', 'error')
            else:
                cursor.execute(
                    'INSERT INTO bloodbanks (name, govt_id, email, contact, city, username, password, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                    (bloodbank, govt_id, email, contact, city, username, password, 'PENDING')
                )
                conn.commit()
                flash('🎉 Registration successful! Once approved, you will receive an email.', 'success')
                return redirect(url_for('register_bloodbank'))
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'error')
            return redirect(url_for('register_bloodbank'))
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    return render_template('bloodbank_reg.html')

@app.route('/bloodbank')
def boodbank():
    return render_template('bloodbank_reg.html')

@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    conn = None
    cursor = None
    try:
        data = request.get_json()  
        city = data.get('city', '')  

        if not city:
            return jsonify({'error': 'City is required'}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bloodbanks WHERE city = %s AND status='APPROVED'" , (city,))
        bloodbanks = cursor.fetchall()

        return jsonify(bloodbanks)  

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

def generate_receipt_number():
    """Generate a unique receipt number"""
    letters = string.ascii_uppercase
    return f"BLD-{''.join(random.choice(letters) for i in range(3))}-{random.randint(1000, 9999)}"

@app.route('/confirm_appointment', methods=['POST'])
def confirm_appointment():
    conn = None
    try:
        data = request.get_json()
        donor_id = session.get("user_id")
        blood_bank_id = data.get('blood_bank_id')
        appointment_date = data.get('appointment_date')
        timeslot = data.get('timeslot')
        medical_history = data.get('medical_history', '')

        if not all([donor_id, blood_bank_id, appointment_date, timeslot]):
            return jsonify({'error': 'All fields are required!'}), 400
        
        conn = get_db_connection()
        with conn.cursor(dictionary=True) as cursor: # Using a 'with' block for connection management
            # Check for existing scheduled appointment
            cursor.execute("""
                SELECT 1 FROM appointments 
                WHERE donor_id = %s AND status = 'Scheduled'
                LIMIT 1
            """, (donor_id,))
            if cursor.fetchone():
                return jsonify({'error': 'You already have a scheduled appointment!'}), 400

            # Get user details
            cursor.execute("""
                SELECT name, email, bloodgroup, dob, phone 
                FROM users 
                WHERE id = %s
            """, (donor_id,))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'error': 'User not found!'}), 404

            # Get blood bank details
            cursor.execute("""
                SELECT name, city, contact
                FROM bloodbanks 
                WHERE bloodbank_id = %s
            """, (blood_bank_id,))
            blood_bank = cursor.fetchone()
            
            if not blood_bank:
                return jsonify({'error': 'Blood bank not found!'}), 404

            # Check donor eligibility
            cursor.execute("""
                SELECT eligibility_status, last_donated
                FROM Bloodbankdonors 
                WHERE donor_id = %s
            """, (donor_id,))
            donor_record = cursor.fetchone()

            if donor_record and donor_record['eligibility_status'] != 'Eligible':
                return jsonify({'error': 'You are not currently eligible to donate blood. Please wait until you become eligible again.'}), 400

            # Insert or update donor record
            cursor.execute("""
                INSERT INTO Bloodbankdonors (
                    donor_id, 
                    first_name, 
                    last_name, 
                    date_of_birth, 
                    blood_type, 
                    contact_number, 
                    email, 
                    bloodbank_id,
                    eligibility_status
                )
                SELECT 
                    %s, 
                    SUBSTRING_INDEX(%s, ' ', 1),
                    CASE 
                        WHEN LOCATE(' ', %s) > 0 
                        THEN SUBSTRING(%s, LOCATE(' ', %s) + 1) 
                        ELSE '' 
                    END,
                    %s, %s, %s, %s, %s, 'Eligible'
                FROM dual
                WHERE NOT EXISTS (
                    SELECT 1 FROM Bloodbankdonors 
                    WHERE donor_id = %s
                )
            """, (
                donor_id, user['name'], user['name'], user['name'], user['name'],
                user['dob'], user['bloodgroup'], user['phone'], user['email'], blood_bank_id,
                donor_id
            ))

            # Generate receipt number
            receipt_number = generate_receipt_number()

            # Insert appointment
            cursor.execute("""
                INSERT INTO appointments (
                    donor_id, 
                    bloodbank_id, 
                    appointment_date, 
                    timeslot, 
                    medical_history, 
                    status,
                    receipt_number,
                    receipt_generated
                ) VALUES (%s, %s, %s, %s, %s, 'Scheduled', %s, TRUE)
            """, (donor_id, blood_bank_id, appointment_date, timeslot, medical_history, receipt_number))
            
            # Get the inserted appointment ID
            appointment_id = cursor.lastrowid
            
            conn.commit()

        # Send confirmation email
        subject = "Blood Donation Appointment Confirmation"
        body = f"""Dear {user['name']},
Your appointment at {blood_bank['name']} ({blood_bank['city']}) 
is confirmed for {appointment_date} at {timeslot}.

Receipt Number: {receipt_number}

Thank you for donating blood!
"""
        send_email(user['email'], subject, body)

        return jsonify({
            'success': 'Appointment confirmed successfully!',
            'appointment_id': appointment_id,
            'receipt_number': receipt_number
        }), 200

    except mysql.connector.Error as e:
        if conn:
            conn.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()

@app.route('/get_booked_appointments')
def get_booked_appointments():
    conn = None
    cursor = None
    try:
        donor_id = session.get("user_id")
        if not donor_id or not str(donor_id).isdigit():
            return jsonify({"error": "User not logged in or invalid session"}), 401

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                a.appointment_id,
                a.appointment_date, 
                a.timeslot, 
                b.name AS blood_bank, 
                b.city, 
                a.status,
                a.receipt_number,
                a.receipt_generated
            FROM appointments a
            JOIN bloodbanks b ON a.bloodbank_id = b.bloodbank_id
            WHERE a.donor_id = %s
            ORDER BY a.appointment_date DESC
        """
        
        cursor.execute(query, (int(donor_id),))
        appointments = cursor.fetchall()

        if not appointments:
            return jsonify({"message": "No appointments found"}), 200

        return jsonify(appointments)

    except mysql.connector.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/download_receipt/<int:appointment_id>')
def download_receipt(appointment_id):
    conn = None
    cursor = None
    try:
        donor_id = session.get("user_id")
        if not donor_id:
            return jsonify({"error": "Unauthorized"}), 401

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get appointment details
        cursor.execute("""
            SELECT a.*, u.name as donor_name, u.bloodgroup, b.name as bloodbank_name, 
                   b.city as bloodbank_city, b.contact as bloodbank_contact
            FROM appointments a
            JOIN users u ON a.donor_id = u.id
            JOIN bloodbanks b ON a.bloodbank_id = b.bloodbank_id
            WHERE a.appointment_id = %s AND a.donor_id = %s
        """, (appointment_id, donor_id))
        
        appointment = cursor.fetchone()

        if not appointment:
            return jsonify({"error": "Appointment not found"}), 404

        if not appointment.get('receipt_number'):
            return jsonify({"error": "Receipt not generated for this appointment"}), 400

        # Create PDF (rest of the logic remains the same)
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # PDF Content
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Blood Donation Appointment Receipt")
        p.setFont("Helvetica", 12)
        
        y_position = 700
        p.drawString(100, y_position, f"Receipt Number: {appointment['receipt_number']}")
        y_position -= 30
        p.drawString(100, y_position, f"Donor Name: {appointment['donor_name']}")
        y_position -= 30
        p.drawString(100, y_position, f"Blood Group: {appointment['bloodgroup']}")
        y_position -= 30
        p.drawString(100, y_position, f"Appointment Date: {appointment['appointment_date']}")
        y_position -= 30
        p.drawString(100, y_position, f"Time Slot: {appointment['timeslot']}")
        y_position -= 30
        p.drawString(100, y_position, f"Blood Bank: {appointment['bloodbank_name']}")
        y_position -= 30
        p.drawString(100, y_position, f"Location: {appointment['bloodbank_city']}")
        y_position -= 30
        p.drawString(100, y_position, f"Contact: {appointment['bloodbank_contact']}")
        y_position -= 50
        
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y_position, "Thank you for your donation!")
        p.setFont("Helvetica", 10)
        y_position -= 30
        p.drawString(100, y_position, "This receipt confirms your blood donation appointment.")
        y_position -= 20
        p.drawString(100, y_position, "Please bring this receipt and a valid ID to your appointment.")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"BloodDonationReceipt_{appointment['receipt_number']}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/logout')
def logout():
    session.clear()  
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route("/forgot_password")
def forgot_password():
    return render_template("forgot_password.html")

@app.route("/send_otp", methods=["POST"])
def send_otp():
    conn = None
    cursor = None
    try:
        data = request.json
        phone = data.get("phone")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT email FROM users WHERE phone = %s", (phone,))
        user = cursor.fetchone()

        if user:
            otp = str(random.randint(100000, 999999))
            session["otp"] = otp
            session["email"] = user["email"]

            send_email(user["email"], "Your OTP Code", f"Your OTP is: {otp}")
            return jsonify({"success": True, "message": "OTP has been sent to your registered email."})
        else:
            return jsonify({"success": False, "message": "User not found."})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
   
@app.route("/verify_otp", methods=["POST"])
def verify_otp():
    data = request.json
    otp = data["otp"]

    if "otp" in session and session["otp"] == otp:
        return jsonify({"success": True, "message": "OTP verified successfully!"})
    
    return jsonify({"success": False, "message": "Invalid OTP."})

@app.route("/reset_password", methods=["POST"])
def reset_password():
    conn = None
    cursor = None
    try:
        data = request.json
        new_password = data.get("password")

        if "email" in session:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, session["email"]))
            conn.commit()

            session.pop("otp", None)
            session.pop("email", None)

            return jsonify({"success": True, "message": "Password reset successfully. Redirecting to login..."})
        
        return jsonify({"success": False, "message": "Session expired. Try again."})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/get_donation_history', methods=['GET'])
def get_donation_history():
    conn = None
    cursor = None
    try:
        donor_id = session.get("user_id")

        if not donor_id:
            return jsonify({"error": "Unauthorized"}), 401

        query = """
            SELECT appointments.appointment_date, bloodbanks.name AS blood_bank, 
                   bloodbanks.city, users.bloodgroup 
            FROM appointments
            JOIN bloodbanks ON appointments.bloodbank_id = bloodbanks.bloodbank_id
            JOIN users ON appointments.donor_id = users.id
            WHERE appointments.donor_id = %s AND appointments.status = 'Completed'
            ORDER BY appointments.appointment_date DESC
        """

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (donor_id,))
        history = cursor.fetchall()

        history_list = [
            {"date": row[0], "blood_bank": row[1], "city": row[2], "blood_group": row[3]}
            for row in history
        ]

        return jsonify(history_list)

    except Exception as e:
        print("Error fetching donation history:", str(e))
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = None
        cur = None
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, password FROM admin WHERE username = %s", (username,))
            admin = cur.fetchone()

            if admin:
                admin_id, db_password = admin

                if password == db_password:
                    session['admin_id'] = admin_id
                    flash('Login successful!', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Invalid email or password!', 'danger')
            else:
                flash('Admin not found!', 'danger')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'danger')
            return redirect(url_for('admin_login'))
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

    return render_template('admin_login.html')

@app.route('/admin/dash', methods=['GET'])
def admin_dashboard():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT bloodbank_id, name, city AS location, contact, govt_id AS license_no, status FROM bloodbanks WHERE status='PENDING'")
        blood_bank_requests = cur.fetchall()
        
        return render_template("admin_dashboard.html", blood_bank_requests=blood_bank_requests)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template("admin_dashboard.html", blood_bank_requests=[])
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@app.route('/admin/bloodbank/<int:id>')
def view_blood_bank(id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT bloodbank_id, name, city AS location, contact, govt_id AS license_no, status FROM bloodbanks WHERE bloodbank_id=%s", (id,))
        blood_bank_details = cur.fetchone()
        
        return render_template("blood_bank_details.html", details=blood_bank_details)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return render_template("blood_bank_details.html", details=None)
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@app.route('/admin/api/bloodbanks/pending')
def fetch_pending_bloodbanks():
    conn = None
    cur = None
    blood_bank_requests = []
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True) # Use dictionary=True for API response
        cur.execute("SELECT bloodbank_id, name, city, contact, govt_id, status FROM bloodbanks WHERE status='PENDING'")
        blood_bank_requests = cur.fetchall()
        
        # Check if this is an API request or template request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify(blood_bank_requests)
        else:
            return render_template("partials/pending_bloodbanks.html", blood_bank_requests=blood_bank_requests)
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({"error": str(e)}), 500
        else:
            flash(f'Error: {str(e)}', 'danger')
            return render_template("partials/pending_bloodbanks.html", blood_bank_requests=[])
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@app.route('/admin/api/donors')
def fetch_donors():
    conn = None
    cur = None
    donors = []
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True) # Use dictionary=True for API response
        cur.execute("SELECT id, name, email, bloodgroup, phone FROM users")
        donors = cur.fetchall()
        
        # Check if this is an API request or template request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify(donors)
        else:
            return render_template("partials/donors.html", donors=donors)
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            return jsonify({"error": str(e)}), 500
        else:
            flash(f'Error: {str(e)}', 'danger')
            return render_template("partials/donors.html", donors=[])
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@app.route('/admin/bloodbank/approve/<int:id>', methods=['POST'])
def approve_blood_bank(id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, email FROM bloodbanks WHERE bloodbank_id = %s", (id,))
        blood_bank = cur.fetchone()

        if not blood_bank:
            return jsonify({"error": "Blood bank not found!"}), 404

        name, email = blood_bank

        cur.execute("UPDATE bloodbanks SET status = 'APPROVED' WHERE bloodbank_id = %s", (id,))
        conn.commit()

        subject = "Welcome to BloodLink!"
        body = f"Dear {name},\n\nThank you for registering on BloodLink. Your account is now active! You can now login using your username and password."

        send_email(email, subject, body)

        return jsonify({"message": "Blood bank approved successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@app.route('/admin/bloodbank/reject/<int:id>', methods=['POST'])
def reject_blood_bank(id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE bloodbanks SET status='REJECTED' WHERE bloodbank_id=%s", (id,))
        conn.commit()
        return jsonify({"message": "Blood bank rejected successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()

@app.route('/bloodbank/login/', methods=['GET'])
def bloodbank_login():
    return login_dash_app.index()

@app.route('/admin/api/bloodbanks/approved')
def fetch_approved_bloodbanks():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT bloodbank_id, name, city, contact, govt_id FROM bloodbanks WHERE status='APPROVED'")
        approved_bloodbanks = cur.fetchall()
        
        return render_template("partials/approved_bloodbanks.html", approved_bloodbanks=approved_bloodbanks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/admin/bloodbank/edit/<int:id>', methods=['GET', 'POST'])
def edit_blood_bank(id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        if request.method == 'POST':
            name = request.form['name']
            city = request.form['city']
            contact = request.form['contact']
            cur.execute("UPDATE bloodbanks SET name=%s, city=%s, contact=%s  WHERE bloodbank_id=%s", 
                        (name, city, contact, id))
            conn.commit()
            return jsonify({"message": "Blood bank details updated successfully!"})
        else:
            cur.execute("SELECT bloodbank_id, name, city, contact, govt_id FROM bloodbanks WHERE bloodbank_id=%s", (id,))
            blood_bank = cur.fetchone()
            return render_template("partials/edit_bloodbank.html", blood_bank=blood_bank)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/admin/bloodbank/delete/<int:id>', methods=['POST'])
def delete_blood_bank(id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM bloodbanks WHERE bloodbank_id=%s", (id,))
        conn.commit()
        return jsonify({"message": "Blood bank deleted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/admin/donor/delete/<int:id>', methods=['POST'])
def delete_donor(id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM appointments WHERE donor_id = %s", (id,))
        cur.execute("DELETE FROM users WHERE id=%s", (id,))
        conn.commit()
        return jsonify({"message": "Donor deleted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/admin/api/admins')
def manage_admins():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, username FROM admin")
        admins = cur.fetchall()
        return render_template('partials/admin_management.html', admins=admins)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/add_admin', methods=['POST'])
def add_admin():
    conn = None
    cur = None
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO admin (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            return jsonify({"message": "New admin added successfully!"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

@app.route('/delete_admin/<int:id>', methods=['POST'])
def delete_admin(id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM admin WHERE id = %s", (id,))
        conn.commit()
        return jsonify({"message": "Admin deleted successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/get_donation_dates')
def get_donation_dates():
    conn = None
    cur = None
    try:
        donor_id = session.get('user_id')
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT last_donated FROM bloodbankdonors WHERE donor_id = %s", (donor_id,))
        donor_data = cur.fetchone()

        cur.execute("""
            SELECT appointment_date FROM appointments 
            WHERE donor_id = %s AND status = 'Completed' 
            ORDER BY appointment_date DESC LIMIT 1
        """, (donor_id,))
        appointment_data = cur.fetchone()

        last_donation = None
        if donor_data and donor_data['last_donated']:
            last_donation = donor_data['last_donated']
        
        if appointment_data:
            if not last_donation or appointment_data['appointment_date'] > last_donation:
                last_donation = appointment_data['appointment_date']
        
        next_eligible = None
        if last_donation:
            # Note: last_donation will be a datetime.date object from mysql.connector, convert to string for timedelta
            last_date = datetime.strptime(str(last_donation), '%Y-%m-%d')
            next_eligible = (last_date + timedelta(days=90)).strftime('%Y-%m-%d')

        return jsonify({
            'last_donation': last_donation.strftime('%Y-%m-%d') if last_donation else None,
            'next_eligible': next_eligible
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/admin/api/recipients')
def fetch_recipients():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT p.patient_id AS id, 
                   p.patient_name AS name, 
                   p.email, 
                   br.blood_type AS bloodgroup,
                   p.patient_contact AS phone,
                   br.reason AS medical_condition
            FROM patients p
            JOIN bloodrequests br ON p.patient_id = br.patient_id
            ORDER BY p.patient_name
        """)
        recipients = cur.fetchall()
        
        return render_template("partials/recipients.html", recipients=recipients)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/admin/api/recipients/delete/<int:recipient_id>', methods=['POST'])
def delete_recipient(recipient_id):
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM patients WHERE patient_id = %s", (recipient_id,)) # Assuming 'patient_id' is the primary key name
        conn.commit()
        affected_rows = cur.rowcount
        
        if affected_rows > 0:
            return jsonify({"success": True, "message": "Recipient deleted successfully"})
        else:
            return jsonify({"success": False, "message": "Recipient not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    server.run(debug=True, port=8051)