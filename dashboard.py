import dash
from dash import dcc, html, Input, Output, State
from numpy import conj
import pandas as pd
import dash_bootstrap_components as dbc
import mysql.connector
from flask import session  # NEW: Import session from Flask
from flask import Flask, session
from flask_session import Session
from server import server
from urllib.parse import parse_qs
from dash import dcc, html, dash_table, Input, Output, State
import mysql.connector
import pandas as pd
import dash
from dash import html, dcc, Output, Input
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from datetime import date
from datetime import datetime, timedelta
import pymysql
import time
import datetime
from dash import html
from datetime import date 


# Database Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "@Pritu50421",
    "database": "final"
}


  # Make sure main.py is in your PYTHONPATH
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    routes_pathname_prefix='/dashboard/',
    requests_pathname_prefix='/dashboard/',
    suppress_callback_exceptions=True
)
app.title = "Blood Bank Dashboard"

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="@Pritu50421",
        database="final"
    )

# -------------------- Data Fetch Functions --------------------

import smtplib
from email.mime.text import MIMEText
import smtplib
from email.mime.text import MIMEText

def send_email_approve(to_email):
    print(f"📧 Sending email to {to_email}...")  # Debugging print

    subject = "Blood Request Approved ✅"
    body = """Dear Patient, 

Your blood request has been approved. Please visit the hospital to collect your blood packet.

Best Regards,
Your Hospital Team"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "yourhospital@email.com"
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("priteshshetty89@gmail.com", "ecfa kequ dpep shxy")  # Use your app password here
        server.sendmail("yourhospital@email.com", to_email, msg.as_string())
        server.quit()
        print("✅ Email sent successfully to", to_email)
    except Exception as e:
        print("❌ Email sending failed:", str(e))
 


def fetch_scheduled_requests(bloodbank_id, scheduled_date):
    try:
        conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        query = """
        SELECT 
            br.request_id,
            br.patient_id,
            p.patient_name,
            br.blood_type,
            br.scheduled_date,
            br.status,
            br.request_type
        FROM BloodRequests br
        JOIN Patients p ON br.patient_id = p.patient_id
        WHERE br.bloodbank_id = %s 
        AND br.scheduled_date = %s
        AND br.status IN ('Approved', 'Pending') 
        AND LOWER(br.request_type) = 'scheduled'  -- ✅ Case-insensitive check
        ORDER BY br.scheduled_date ASC;
        """

        cursor.execute(query, (bloodbank_id, scheduled_date))
        scheduled_requests = cursor.fetchall()

        cursor.close()
        conn.close()

        return scheduled_requests if scheduled_requests else []

    except Exception as e:
        return f"❌ Error: {str(e)}"



def fetch_emergency_requests(bloodbank_id):
    try:
        conn = mysql.connector.connect(**db_config)  # Connect to MySQL
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT 
            br.request_id,
            br.patient_id,
            p.patient_name,
            p.patient_contact,
            br.blood_type,
            br.reason,
            br.hospital_address
        FROM BloodRequests br
        JOIN Patients p ON br.patient_id = p.patient_id
        WHERE br.bloodbank_id = %s 
        AND br.request_type = 'Emergency' 
        AND br.status = 'Pending';
        """
        
        cursor.execute(query, (bloodbank_id,))
        emergency_requests = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return emergency_requests if emergency_requests else []
    
    except Exception as e:
        print(f"❌ Error fetching emergency: {str(e)}") 
        return []



import mysql.connector
def fetch_patients(bloodbank_id):
    try:
        conn = mysql.connector.connect(**db_config)  # Connect to MySQL
        cursor = conn.cursor(dictionary=True)
        
        query = """
        SELECT 
            p.patient_id,
            br.request_id, 
            p.patient_name, 
            p.patient_contact, 
            p.age, 
            p.gender, 
            p.emergency_case, 
            p.location, 
            br.status AS request_status  -- Fetch request status directly
        FROM Patients p
        JOIN BloodRequests br ON p.patient_id = br.patient_id  -- Ensuring every patient has a request
        WHERE p.bloodbank_id = %s
        """
        
        cursor.execute(query, (bloodbank_id,))
        patients = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return patients if patients else []
    
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
        return []



def get_eligible_donors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT DISTINCT d.email, d.first_name
        FROM BloodBankDonors d
        LEFT JOIN Appointments a ON d.donor_id = a.donor_id 
        WHERE d.eligibility_status = 'Eligible' 
        AND (a.appointment_date IS NULL OR a.appointment_date < %s)
    """
    cursor.execute(query, (date.today(),))
    donors = cursor.fetchall()

    conn.close()
    return donors

def send_email():
    donors = get_eligible_donors()
    
    if not donors:
        return "No eligible donors available for email notifications."

    sender_email = "lendlogixloans@gmail.com"
    sender_password = "kxwa rezx jkvj wgod"

    subject = " Blood Donation Request"
    email_body_template = """Dear {name},

We urgently need blood donations. If you are available, please consider visiting your registered blood bank.

Thank you for your support.

Best regards,
BloodLink Team
"""

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)

        for donor in donors:
            recipient_email = donor["email"]
            body = email_body_template.format(name=donor["first_name"])
            
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = recipient_email

            server.sendmail(sender_email, recipient_email, msg.as_string())

        server.quit()
        return "Emails sent successfully!"
    except Exception as e:
        return f"Failed to send emails: {str(e)}"



def generate_inventory_cards(blood_data):
    return dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"{row['units_available']}", className="text-white fw-bold text-center", style={"fontSize": "2rem"}),
                    html.P(row["blood_type"], className="text-white text-center", style={"fontSize": "1.2rem"}),
                ])
            ], className="shadow-sm bg-danger rounded", style={"padding": "20px", "borderRadius": "10px"}), 
            width=3, className="mb-4"
        )
        for _, row in blood_data.iterrows()
    ], className="justify-content-center px-4")



def fetch_appointments_by_date(bloodbank_id, selected_date):#***************************************************************************************************************
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT a.appointment_id, 
               d.donor_id,
               d.first_name AS donor_name, 
               d.blood_type, 
               a.appointment_date, 
               a.status 
        FROM Appointments a
        JOIN BloodBankDonors d ON a.donor_id = d.donor_id
        WHERE d.bloodbank_id = %s AND a.appointment_date = %s
    """
    
    cursor.execute(query, (bloodbank_id, selected_date))
    appointments = cursor.fetchall()
    
    cursor.close()
    connection.close()
    return appointments

# Fetch Appointments based on Date
def fetch_appointments(bloodbank_id, selected_date):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT a.appointment_id,
               d.donor_id, 
               d.first_name AS donor_name, 
               d.blood_type, 
               a.appointment_date, 
               a.status 
        FROM Appointments a
        JOIN BloodBankDonors d ON a.donor_id = d.donor_id
        WHERE d.bloodbank_id = %s AND a.appointment_date = %s
    """
    
    cursor.execute(query, (bloodbank_id, selected_date))
    appointments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return appointments


def fetch_donors(bloodbank_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT donor_id, first_name, last_name, blood_type, contact_number, email, 
               last_donated, donation_count, eligibility_status
        FROM BloodBankDonors 
        WHERE bloodbank_id = %s
        """
        cursor.execute(query, (bloodbank_id,))
        donors = cursor.fetchall()
        cursor.close()
        conn.close()
        return donors if donors else []
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
        return []

def fetch_blood_inventory(bloodbank_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT blood_type, COUNT(*) AS units_available
        FROM BloodInventory
        WHERE bloodbank_id = %s AND status = 'Available'
        GROUP BY blood_type
        """
        cursor.execute(query, (bloodbank_id,))
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return pd.DataFrame(data) if data else pd.DataFrame(columns=["Blood Type", "Units Available"])
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
        return pd.DataFrame(columns=["Blood Type", "Units Available"])


def fetch_donor_stats(bloodbank_id):
    return {
        "Total Donors": 10 + int(bloodbank_id),
        "Total Requests": 20 + int(bloodbank_id),
        "Approved Requests": 15 + int(bloodbank_id),
        "Total Blood Unit (ml)": 5000 + (int(bloodbank_id) * 100)
    }

# -------------------- Function to Update Eligibility --------------------




def update_eligibility_status(bloodbank_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = """
        UPDATE BloodBankDonors
        SET eligibility_status = 'Eligible' 
        WHERE last_donated IS NOT NULL 
        AND DATEDIFF(CURDATE(), last_donated) >= 90 
        AND eligibility_status = 'Not Eligible'
        AND bloodbank_id = %s
        """
        cursor.execute(query, (bloodbank_id,))
        conn.commit()
        updated_rows = cursor.rowcount
        cursor.close()
        conn.close()
        return updated_rows
    except mysql.connector.Error as e:
        print(f"Database Error: {e}")
        return 0

# -------------------- Dashboard Layout & Sidebar --------------------
sidebar = dbc.Col([
    html.H2("Welcome", className="text-white text-left mt-3"),
    html.Hr(),
    dbc.Nav([
        dbc.NavLink("Home", href="/", active="exact", className="nav-link text-white"),
        dbc.NavLink("Donors", href="/donors", active="exact", className="nav-link text-white"),
        dbc.NavLink("Check Slots", href="/check-slots", active="exact", className="nav-link text-white"),
        dbc.NavLink("Patients", href="/patients", active="exact", className="nav-link text-white"),
        dbc.NavLink("Check Request", href="/request-history", active="exact", className="nav-link text-white"),
        dbc.NavLink([
             "Emergency Request ",
            html.Span(id="emergency-sidebar-count", className="badge bg-danger ms-2"),  # 🔴 Badge
            html.I(className="bi bi-bell-fill text-warning ms-2")  # 🔔 Bell Icon
        ], href="/emergency", active="exact", className="text-white"),
        dbc.NavLink("Request Blood", href="/request-blood", active="exact", className="nav-link text-white")
    ], vertical=True, pills=True, className="flex-column"),
     dcc.Interval(
        id="interval-component",
        interval=5000,  # ✅ Refresh every 5 seconds
        n_intervals=0
    ),
], width=2, className="p-3 vh-100", style={"backgroundColor": "#b30000", "color": "white"})

def generate_dashboard_layout(bloodbank_id):
    blood_data = fetch_blood_inventory(bloodbank_id)

    return dbc.Col([
        html.H1("Blood Bank Dashboard", className="text-center mt-3 text-white"),
        html.H5(f"Blood Bank ID: {bloodbank_id}", className="text-center text-white"),

        # 🚀 Inventory Display Section
        html.Div(id="blood-inventory-display", children=generate_inventory_cards(blood_data)),  

        html.Div([
            html.Button("Update Inventory", id="update-inventory-btn", n_clicks=0, className="btn btn-primary"),
            html.Div(id="inventory-update-msg", style={"textAlign": "center", "marginTop": "10px", "color": "white"})
        ])
    ], width=10, className="p-4 bg-dark")


from datetime import date  # ✅ Import correctly

@app.callback(
    [Output("inventory-update-msg", "children"),
     Output("inventory-update-msg", "style"),
     Output("blood-inventory-display", "children")],  # 🔄 Updates UI dynamically
    Input("update-inventory-btn", "n_clicks"),
    State("bloodbank-store", "data"),  # ✅ Use the correct ID from your layout
    prevent_initial_call=True
)
def update_inventory(n_clicks, bloodbank_data):
    bloodbank_id = session.get("bloodbank_id")
    if not bloodbank_id:
        return html.H3("⚠ No BloodBank ID Provided!", className="text-center text-danger mt-5")

    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        today = date.today().strftime("%Y-%m-%d")  # ✅ FIXED

        cursor.execute("""
            UPDATE BloodInventory 
            SET status = 'Expired' 
            WHERE expiry_date <= %s  
            AND status IN ('Available', 'Used') 
            AND bloodbank_id = %s
        """, (today, bloodbank_id))

        affected_rows = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        message = f"✅ {affected_rows} blood packets expired and updated." if affected_rows > 0 else "ℹ No packets expired today."

        # 🚀 FETCH UPDATED INVENTORY AFTER UPDATING STATUS
        updated_inventory = fetch_blood_inventory(bloodbank_id)  
        new_inventory_display = generate_inventory_cards(updated_inventory)  

        return message, {"display": "block"}, new_inventory_display  # 🔄 Update inventory dynamically

    except Exception as e:
        return f"❌ Error updating inventory: {str(e)}", {"display": "block"}, dash.no_update







def page_content(title):
    return dbc.Col([
        html.H1(title, className="text-center mt-3 text-white"),
        html.P("This section is under development.", className="text-center text-white")
    ], width=10, className="p-4 bg-dark")

# -------------------- App Layout --------------------
app.layout = dbc.Container([
    dcc.Location(id="url", refresh=False),
    dcc.Location(id="url-refresh", refresh=True),
    dcc.Store(id="bloodbank-store", storage_type="session"),
    dcc.Interval(id="refresh-trigger", interval=1, max_intervals=1),
    dcc.Interval(id="clear-msg-trigger", interval=3000, max_intervals=1), # Hide message after 3 seconds

    dbc.Row([
        sidebar,
        dbc.Col(id="page-content", width=10, className="p-4 bg-dark")
    ]),
    html.Div(
    dbc.Button("Logout", id="logout-btn", color="danger", className="mt-3"),
    style={
        "position": "fixed",  # Fixed position so it stays on screen
        "bottom": "20px",  # 20px from the bottom
        "right": "20px",  # 20px from the right
        "zIndex": "1000"  # Ensures it stays on top of other elements
    }
)
], fluid=True, className="bg-dark text-white")

# -------------------- Callback to Update Page Content --------------------
from dash import no_update
from datetime import date
import pymysql
 # Assuming this function returns a connected DB instance

@app.callback(
    Output("update-appointments-btn", "disabled"),  # Dummy output to avoid Dash callback errors
    Input("update-appointments-btn", "n_clicks"),
    prevent_initial_call=True
)
def update_appointments(n_clicks):
    if n_clicks:
        try:
            today_date = date.today().strftime("%Y-%m-%d")

            # ✅ Use your existing DB connection function
            connection = get_db_connection()
            cursor = connection.cursor()

            # ✅ Update only past "Scheduled" appointments to "Absent"
            sql = """
                UPDATE Appointments
                SET status = 'Absent'
                WHERE appointment_date < %s 
                AND status = 'Scheduled'
            """
            cursor.execute(sql, (today_date,))
            connection.commit()

            cursor.close()
            connection.close()
            print("✅ Expired 'Scheduled' appointments updated to 'Absent'.")

        except Exception as e:
            print(f"❌ Error updating appointments: {str(e)}")
    
    return no_update  # Prevents Dash output error


@app.callback(
    Output("update_status", "children"),
    [Input("update_requests_btn", "n_clicks")]
)
def update_requests(n_clicks):
    if not n_clicks:
        raise PreventUpdate

    conn = pymysql.connect(host="localhost", user="root", password="@Pritu50421", database="final")
    cursor = conn.cursor()

    try:
        today_date = datetime.now().strftime("%Y-%m-%d")

        # ✅ 1️⃣ CANCEL ALL PENDING REQUESTS WITH PAST SCHEDULED DATE
        cursor.execute("""
            UPDATE BloodRequests 
            SET status = 'Cancelled' 
            WHERE status = 'Pending' AND scheduled_date < %s
        """, (today_date,))
        
        # ✅ 2️⃣ FIND ALL APPROVED REQUESTS WHERE PATIENT NEVER CAME
        cursor.execute("""
            SELECT request_id, inventory_id FROM BloodRequests 
            WHERE status = 'Approved' AND scheduled_date < %s
        """, (today_date,))
        
        expired_requests = cursor.fetchall()

        for request_id, inventory_id in expired_requests:
            if inventory_id:
                # ✅ 3️⃣ MARK BLOOD PACKET AS AVAILABLE AGAIN
                cursor.execute("""
                    UPDATE BloodInventory 
                    SET status = 'Available' 
                    WHERE inventory_id = %s
                """, (inventory_id,))

                # ✅ 4️⃣ CHANGE REQUEST STATUS TO CANCELLED
                cursor.execute("""
                    UPDATE BloodRequests 
                    SET status = 'Cancelled' 
                    WHERE request_id = %s
                """, (request_id,))

        conn.commit()
        return "✅ Requests Updated Successfully!"

    except Exception as e:
        conn.rollback()
        return f"❌ Error: {str(e)}"

    finally:
        cursor.close()
        conn.close()


from datetime import datetime
import dash_bootstrap_components as dbc
from flask import session
from dash import html


@app.callback(
    Output("scheduled_requests_table", "children"),  # ✅ Update Table Body
    Input("fetch_requests_btn", "n_clicks"),  # ✅ Button Click
    State("scheduled_date_input", "date"),  # ✅ Date Input
    prevent_initial_call=True
)
def update_scheduled_requests(n_clicks, scheduled_date):
    bloodbank_id = session.get("bloodbank_id")

    if not bloodbank_id:
        return html.Tr(html.Td("⚠ No BloodBank ID Provided!", colSpan=5, className="text-center text-danger"))

    if not scheduled_date:
        return html.Tr(html.Td("⚠ Please select a date.", colSpan=5, className="text-center text-warning"))

    # ✅ Convert Dash date format to MySQL-compatible format
    try:
        formatted_date = datetime.strptime(scheduled_date, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return html.Tr(html.Td("❌ Invalid Date Format!", colSpan=5, className="text-center text-danger"))

    # ✅ Fetch Scheduled Requests
    scheduled_requests = fetch_scheduled_requests(bloodbank_id, formatted_date)

    # ✅ Handle Errors
    if isinstance(scheduled_requests, str):  # If function returns an error message
        return html.Tr(html.Td(scheduled_requests, colSpan=5, className="text-center text-danger"))

    # ✅ If No Requests Found
    if not scheduled_requests:
        return html.Tr(html.Td("No requests found for this date.", colSpan=5, className="text-center text-white"))

    # ✅ Return Table Rows with Data
    return [
        html.Tr([
            html.Td(req["request_id"]),
            html.Td(req["patient_name"]),
            html.Td(req["blood_type"]),
            html.Td(req["scheduled_date"]),
            html.Td(req["status"])
        ]) for req in scheduled_requests
    ]

import pymysql
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from flask import session
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
@app.callback(
    Output("approve_status", "children"),
    [Input("approve_request_btn", "n_clicks")],
    [State("request_id_input", "value"), State("blood_type_input", "value"), State("bloodbank-store", "data")]
)
def approve_request(n_clicks, request_id, blood_type, bloodbank_data):
    if not n_clicks or not request_id or not blood_type:
        raise PreventUpdate

    bloodbank_id = session.get("bloodbank_id")
    if not bloodbank_id:
        return "Error: Blood Bank ID Not Found"

    conn = pymysql.connect(host="localhost", user="root", password="@Pritu50421", database="final")
    cursor = conn.cursor()

    try:
        # ✅ 1️⃣ CHECK IF ALREADY APPROVED
        cursor.execute("SELECT status, patient_id FROM BloodRequests WHERE request_id = %s", (request_id,))
        result = cursor.fetchone()
        
        if not result:
            return "Error: Request Not Found"

        status, patient_id = result

        if status in ["Approved", "Completed"]:
          return f"Request is already {status}. Cannot approve again."


        # ✅ 2️⃣ FIND PATIENT EMAIL
        cursor.execute("SELECT email FROM Patients WHERE patient_id = %s", (patient_id,))
        email_result = cursor.fetchone()
        if not email_result:
            return "Error: Patient Email Not Found"

        patient_email = email_result[0]

        # ✅ 3️⃣ FIND AVAILABLE BLOOD PACKET
        cursor.execute("""
            SELECT inventory_id FROM BloodInventory 
            WHERE blood_type = %s AND status = 'Available' 
            AND bloodbank_id = %s
            ORDER BY expiry_date ASC LIMIT 1
        """, (blood_type, bloodbank_id))

        packet = cursor.fetchone()
        if not packet:
            return "No Available Blood Packets!"

        inventory_id = packet[0]

        # ✅ 4️⃣ UPDATE INVENTORY & REQUEST STATUS
        cursor.execute("UPDATE BloodInventory SET status = 'Used' WHERE inventory_id = %s", (inventory_id,))
        cursor.execute("UPDATE BloodRequests SET status = 'Approved', inventory_id = %s WHERE request_id = %s", (inventory_id, request_id))
        conn.commit()

        # ✅ 5️⃣ SEND EMAIL WITH CORRECT PARAMETERS
        send_email_approve(patient_email)

        return "Request Approved & Email Sent ✅"

    except Exception as e:
        conn.rollback()
        return f"Error: {str(e)}"

    finally:
        cursor.close()
        conn.close()



@app.callback(
    Output("complete_status", "children"),
    [Input("complete_request_btn", "n_clicks")],
    [State("request_id_input", "value"), State("blood_type_input", "value"), State("bloodbank-store", "data")]
)
def complete_request(n_clicks, request_id, blood_type, bloodbank_data):
    if not n_clicks or not request_id or not blood_type:
        raise PreventUpdate

    bloodbank_id = session.get("bloodbank_id")
    if not bloodbank_id:
        return "Error: Blood Bank ID Not Found"

    conn = pymysql.connect(host="localhost", user="root", password="@Pritu50421", database="final")
    cursor = conn.cursor()

    try:
        # ✅ 1️⃣ CHECK IF REQUEST EXISTS AND FETCH STATUS
        cursor.execute("SELECT status FROM BloodRequests WHERE request_id = %s", (request_id,))
        result = cursor.fetchone()
        
        if not result:
            return "Error: Request Not Found"

        status = result[0]

        # ❌ IF NOT APPROVED, ASK TO APPROVE FIRST
        if status != "Approved":
            return "Error: Request must be approved first!"

        # ✅ 2️⃣ UPDATE REQUEST STATUS TO 'COMPLETED'
        cursor.execute("UPDATE BloodRequests SET status = 'Completed' WHERE request_id = %s", (request_id,))
        conn.commit()

        return "Request Successfully Marked as Completed ✅"

    except Exception as e:
        conn.rollback()
        return f"Error: {str(e)}"

    finally:
        cursor.close()
        conn.close()



from dash import Input, Output, State, ctx, html
import mysql.connector

import pymysql
from dash import dcc, html, Input, Output, State, callback
from flask import session

# Confirm button callback
@app.callback(
    Output("confirm-status", "children"),
    Input("confirm-btn", "n_clicks"),
    State("blood_type_input", "value"),
    State("packet_count_input", "value"),
    State("request_id_input", "value"),
    prevent_initial_call=True
)
def confirm_blood_request(n_clicks, blood_type, packet_count, request_id):
    bloodbank_id = session.get("bloodbank_id")

    if not bloodbank_id:
        return "❌ Error: BloodBank ID missing. Please log in again."

    conn = None
    cursor = None

    try:
        # ✅ Connect to DB with DictCursor
        conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        # ✅ 1. Check available blood packets (FIFO order)
        cursor.execute(
            """
            SELECT inventory_id FROM BloodInventory 
            WHERE bloodbank_id = %s AND blood_type = %s AND status = 'Available'
            ORDER BY collected_date ASC LIMIT %s
            """,
            (bloodbank_id, blood_type, int(packet_count))
        )
        available_packets = cursor.fetchall()

        # ✅ 2. If enough packets are available, process request
        if len(available_packets) >= int(packet_count):
            # Get packet IDs
            packet_ids = [packet["inventory_id"] for packet in available_packets]

            # ✅ 3. Mark packets as 'Used'
            cursor.executemany(
                "UPDATE BloodInventory SET status = 'Used' WHERE inventory_id = %s",
                [(packet_id,) for packet_id in packet_ids]
            )

            # ✅ 4. Update request status to 'Completed'
            cursor.execute(
                "UPDATE BloodRequests SET status = 'Completed' WHERE request_id = %s",
                (request_id,)
            )

            conn.commit()
            return f"✅ Request {request_id} has been fulfilled. {packet_count} packet(s) assigned."
        
        else:
            # ✅ 5. If not enough packets, mark request as 'Cancelled'
            cursor.execute(
                "UPDATE BloodRequests SET status = 'Cancelled' WHERE request_id = %s",
                (request_id,)
            )
            conn.commit()
            return f"❌ Not enough blood packets available. Request {request_id} has been cancelled."

    except Exception as e:
        return f"❌ Error: {str(e)}"

    finally:
        # ✅ Close cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.callback(
    Output("emergency-sidebar-count", "children"),  # ✅ Update Sidebar Badge
    Input("interval-component", "n_intervals")  # ✅ Auto-refresh every 5s
)
def update_sidebar_emergency_count(n_intervals):
    bloodbank_id = session.get("bloodbank_id")
    if not bloodbank_id:
        return "0"

    emergency_requests = fetch_emergency_requests(bloodbank_id)
    return str(len(emergency_requests))  # Return count as text




from dash import Input, Output, State, ctx, no_update
import dash_bootstrap_components as dbc
import dash.html as html

@app.callback(
    Output("appointments-table-container", "children"),
    Input("date-picker", "date")
)
def update_appointments(selected_date):
    bloodbank_id = session.get("bloodbank_id")
    if not bloodbank_id:
        return html.H3("⚠ No BloodBank ID Provided!", className="text-center text-danger mt-5")

    if not selected_date:
        return html.P("📅 Please select a date to view appointments.", className="text-center text-warning")

    # ✅ Fetch appointments using the new function
    appointments = fetch_appointments(bloodbank_id, selected_date)

    if not appointments:
        return html.P("❌ No appointments found for this date.", className="text-center text-danger")

    return html.Div([
        html.Div([
            dbc.Table([
                html.Thead(html.Tr([
                    html.Th("Appointment ID", className="text-white bg-dark"),
                    html.Th("Donor ID", className="text-white bg-dark"),
                    html.Th("Donor Name", className="text-white bg-dark"),
                    html.Th("Blood Type", className="text-white bg-dark"),
                    html.Th("Appointment Date", className="text-white bg-dark"),
                    html.Th("Appointment Status", className="text-white bg-dark"),
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(appointment["appointment_id"]),
                        html.Td(appointment["donor_id"]),
                        html.Td(appointment["donor_name"]),
                        html.Td(appointment["blood_type"]),
                        html.Td(appointment["appointment_date"]),
                        html.Td(appointment["status"]),
                    ],)
                    for appointment in appointments
                ])
            ], bordered=True, striped=True, hover=True, className="table-dark text-white"),
        ], style={
            "maxHeight": "200px",
            "overflowY": "scroll",
            "border": "1px solid #ddd",
            "borderRadius": "5px",
            "padding": "10px"
        })
    ])


import datetime
@app.callback(
    Output("manual-update-msg", "children"),
    Input("update-donor-btn", "n_clicks"),
    State("manual-donor-id", "value"),
    State("manual-blood-group", "value"),
    prevent_initial_call=True
)
def update_donor_status(n_clicks, donor_id, blood_group):
    bloodbank_id = session.get("bloodbank_id")  # ✅ Get bloodbank_id from session

    if not bloodbank_id:
        return "❌ Error: BloodBank ID missing. Please log in again."

    if not donor_id or not blood_group:
        return "⚠ Please enter both Donor ID and Blood Group."

    try:
        # Connect to MySQL
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()

        # ✅ Check if donor exists and get blood type
        cursor.execute("SELECT blood_type, donation_count, eligibility_status FROM BloodBankDonors WHERE donor_id = %s", (donor_id,))
        donor = cursor.fetchone()

        if donor:
            actual_blood_type, donation_count, eligibility_status = donor

            # ✅ Validate blood group
            if actual_blood_type != blood_group:
                conn.close()
                return f"❌ Error: Entered blood group '{blood_group}' does not match donor {donor_id}'s actual blood group '{actual_blood_type}'."

            # ✅ Check eligibility
            if eligibility_status == "Not Eligible":
                conn.close()
                return f"❌ Donor {donor_id} is already 'Not Eligible' and cannot donate again."

            # ✅ Check appointment status
            cursor.execute("SELECT status FROM appointments WHERE donor_id = %s ORDER BY appointment_id DESC LIMIT 1", (donor_id,))
            appointment = cursor.fetchone()

            if appointment:
                appointment_status = appointment[0]

                # ✅ Prevent updates if appointment is 'Completed' or 'Absent'
                if appointment_status in ["Completed", "Absent"]:
                    conn.close()
                    return f"❌ Cannot update! Donor {donor_id} has an appointment marked as '{appointment_status}'."

                # ✅ Update appointment status to 'Completed' if it's 'Scheduled'
                cursor.execute("""
                    UPDATE appointments 
                    SET status = 'Completed', updated_at = CURRENT_TIMESTAMP
                    WHERE donor_id = %s AND status = 'Scheduled'
                """, (donor_id,))
                conn.commit()

            # Generate unique packet ID
            packet_id = f"PKT{donor_id}{int(time.time())}"  
            collected_date = datetime.today().strftime('%Y-%m-%d')



            # Insert into BloodInventory
            cursor.execute("""
                INSERT INTO BloodInventory (bloodbank_id, blood_type, packet_id, collected_date, status)
                VALUES (%s, %s, %s, %s, 'Available')
            """, (bloodbank_id, blood_group, packet_id, collected_date))

            # Update donor details
            new_count = donation_count + 1
            cursor.execute("""
                UPDATE BloodBankDonors
                SET donation_count = %s, last_donated = %s, eligibility_status = 'Not Eligible'
                WHERE donor_id = %s
            """, (new_count, collected_date, donor_id))

            conn.commit()
            conn.close()

            return f"✅ Donor {donor_id} updated! Blood packet {packet_id} added for BloodBank {bloodbank_id}."

        else:
            conn.close()
            return f"❌ Donor ID {donor_id} not found."

    except Exception as e:
        return f"❌ Error updating donor: {str(e)}"



from datetime import datetime
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    # Use bloodbank_id from Flask session instead of the query string
    bloodbank_id = session.get("bloodbank_id")
    if not bloodbank_id:
        return html.H3("⚠ No BloodBank ID Provided!", className="text-center text-danger mt-5")

    elif pathname == "/donors":
        donors = fetch_donors(bloodbank_id)
        return dbc.Col([
            html.H1("Donors List", className="text-center mt-3 text-white"),
        dbc.Card([
            dbc.CardHeader(html.H4("Registered Donors", className="text-center text-white"), className="bg-danger"),
            dbc.CardBody([
                # Scrollable Container for the Table
                html.Div([
                    dbc.Table([
                        html.Thead(html.Tr([
                            html.Th("Donor Id", className="text-white bg-dark"),
                            html.Th("First Name", className="text-white bg-dark"),
                            html.Th("Last Name", className="text-white bg-dark"),
                            html.Th("Blood Type", className="text-white bg-dark"),
                            html.Th("Contact", className="text-white bg-dark"),
                            html.Th("Email", className="text-white bg-dark"),
                            html.Th("Last Donated", className="text-white bg-dark"),
                            html.Th("Donation Count", className="text-white bg-dark"),
                            html.Th("Eligibility Status", className="text-white bg-dark"),
                        ])),
                        html.Tbody([
                            html.Tr([
                                html.Td(donor["donor_id"]),
                                html.Td(donor["first_name"]),
                                html.Td(donor["last_name"]),
                                html.Td(donor["blood_type"]),
                                html.Td(donor["contact_number"]),
                                html.Td(donor["email"]),
                                html.Td(donor["last_donated"] if donor["last_donated"] else "N/A"),
                                html.Td(donor["donation_count"]),
                                html.Td(donor["eligibility_status"], 
                                        className="text-success" if donor["eligibility_status"] == "Eligible" else "text-danger")
                            ]) for donor in donors
                        ])
                    ], bordered=True, striped=True, hover=True, className="table-dark text-white"),
                ], style={
                    "maxHeight": "400px",  # Adjust the height as needed
                    "overflowY": "auto",
                    "border": "1px solid #ddd",
                    "borderRadius": "5px"
                }),
            ]),
        ], className="shadow-lg mt-4"),


            # Update Eligibility Button
            html.Div([
                dbc.Button("Update Eligibility", id="update-eligibility-btn", color="success", className="mt-3"),
                html.P(id="update-eligibility-msg", className="mt-2")
            ], className="text-center"),
        ], width=10, className="p-4 bg-dark")
    
    
    

    elif pathname == "/check-slots":
        bloodbank_id = session.get("bloodbank_id")
        if not bloodbank_id:
            return html.H3("⚠ No BloodBank ID Provided!", className="text-center text-danger mt-5")

        return dbc.Col([
            html.H1("Check Appointments", className="text-center mt-3 text-white"),

            # Date Picker to Select Appointment Date
            html.Div([
                html.Label("Select Date:", className="text-white"),
                dcc.DatePickerSingle(
                    id="date-picker",
                    min_date_allowed="2025-01-01",
                    max_date_allowed="2025-12-31",
                    display_format="YYYY-MM-DD",
                    placeholder="Select a Date"
                ),
                html.Button("Update Appointments", id="update-appointments-btn", n_clicks=0, className="btn btn-primary ms-3"),
            ], className="mb-3 d-flex align-items-center"),

            # Appointments Table (Dynamically Updated)
            dbc.Card([
                dbc.CardHeader(html.H4("Scheduled Donations", className="text-center text-white"), className="bg-danger"),
                dbc.CardBody([
                    html.Div(id="appointments-table-container")  # Updates based on selected date
                ],)
            ], className="shadow-lg mt-4"),
             html.Br(),

        # Manual Donor Update Section
        dbc.Card([
            dbc.CardHeader(html.H4("Update Donor Status", className="text-center text-white"), className="bg-danger"),
            dbc.CardBody([
                html.Div([
                    html.Span("Enter Donor ID:", style={"color": "white", "margin-bottom": "5px"}),
                    dcc.Textarea(id="manual-donor-id", style={"width": "100%", "height": "30px", "padding": "2px"}),
                ], style={"margin-bottom": "10px"}),

                html.Div([
                    html.Span("Enter Blood Group:", style={"color": "white", "margin-bottom": "5px"}),
                    dcc.Textarea(id="manual-blood-group", style={"width": "100%", "height": "30px", "padding": "2px"}),
                ], style={"margin-bottom": "10px"}),

                dbc.Button("Update Donor Status", id="update-donor-btn", color="primary", className="mt-2"),
                html.P(id="manual-update-msg", className="mt-2 text-white")
            ], className="text-white")  # Ensures all text inside is white
        ], className="shadow-lg mt-2 bg-dark", style={"height": "auto", "min-height": "180px"})

  
        ], width=10, className="p-4 bg-dark")


    elif pathname == "/patients":
        bloodbank_id = session.get("bloodbank_id")
        if not bloodbank_id:
            return html.H3("⚠ No BloodBank ID Provided!", className="text-center text-danger mt-5")

        patients = fetch_patients(bloodbank_id)
        return dbc.Col([
            html.H1("Patients List", className="text-center mt-3 text-white"),
            
            dbc.Card([
                dbc.CardHeader(html.H4("Registered Patients", className="text-center text-white"), className="bg-danger"),
                dbc.CardBody([
                    # Scrollable container for the table
                    html.Div([
                        dbc.Table([
                            html.Thead(html.Tr([
                                html.Th("Patient ID", className="text-white bg-dark"),
                                html.Th("Request ID", className="text-white bg-dark"),
                                html.Th("Name", className="text-white bg-dark"),
                                html.Th("Contact", className="text-white bg-dark"),
                                html.Th("Age", className="text-white bg-dark"),
                                html.Th("Gender", className="text-white bg-dark"),
                                html.Th("Emergency", className="text-white bg-dark"),
                                html.Th("Location", className="text-white bg-dark"),
                                html.Th("Request Status", className="text-white bg-dark"),
                            ])),
                            html.Tbody([
                                html.Tr([
                                    html.Td(patient["patient_id"]),
                                    html.Td(patient["request_id"]),
                                    html.Td(patient["patient_name"]),
                                    html.Td(patient["patient_contact"]),
                                    html.Td(patient["age"]),
                                    html.Td(patient["gender"]),
                                    html.Td("🚨Yes" if patient["emergency_case"] else "No", 
                                            className="text-danger fw-bold" if patient["emergency_case"] else ""),
                                    html.Td(patient["location"] if patient["location"] else "N/A"),
                                    html.Td(patient["request_status"]),
                                ]) for patient in patients
                            ])
                        ], bordered=True, striped=True, hover=True, className="table-dark text-white"),
                    ], style={
                        "maxHeight": "400px",  # Adjust height as needed
                        "overflowY": "scroll",
                        "border": "1px solid #ddd",
                        "borderRadius": "5px"
                    }),
                ]),
            ], className="shadow-lg mt-4"),
            
        ], width=10, className="p-4 bg-dark")

   
    elif pathname == "/request-history":
        bloodbank_id = session.get("bloodbank_id")
        if not bloodbank_id:
            return html.H3("⚠ No BloodBank ID Provided!", className="text-center text-danger mt-5")

        return dbc.Col([
            html.H1("Scheduled Blood Requests", className="text-center mt-3 text-white"),

            # 🔹 Date Selection to View Requests
            dbc.Card([
                dbc.CardHeader(html.H4("Select Date", className="text-center text-white"), className="bg-primary"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Schedules Date", className="text-white"),
                            dcc.DatePickerSingle(
                                id="scheduled_date_input",
                                placeholder="Select Date",
                                date=datetime.today().strftime("%Y-%m-%d")  # Default to today's date
                            ),
                        ], width=6),

                        dbc.Col([
                            dbc.Button("Update Requests", id="update_requests_btn", n_clicks=0,color="info", className="w-100 mt-4"),
                            dbc.Button("Fetch Requests", id="fetch_requests_btn", color="info", className="w-100 mt-4"),
                        ], width=3),
                    ]),
                    html.Div(id="update_status",className="mt-3 text-white"),
                    html.Div(id="fetch_status", className="mt-3 text-white")
                ]),
            ], className="shadow-lg mt-4 bg-dark"),

            # 🔹 Requests Table (Auto-Populates Based on Date Selection)
            dbc.Card([
                dbc.CardHeader(html.H4("Scheduled Requests", className="text-center text-white"), className="bg-dark"),
                dbc.CardBody([
                    dbc.Table([
                        html.Thead(html.Tr([
                            html.Th("Request ID", className="text-white bg-dark"),
                            html.Th("Patient Name", className="text-white bg-dark"),
                            html.Th("Blood Group", className="text-white bg-dark"),
                            html.Th("Scheduled Date", className="text-white bg-dark"),
                            html.Th("Status", className="text-white bg-dark")
                        ])),
                        html.Tbody(id="scheduled_requests_table"),
                    ], bordered=True, striped=True, hover=True, className="table-dark text-white"),
                ]),
            ], className="shadow-lg mt-4 bg-dark"),

            # 🔹 Approve or Complete Request
            dbc.Card([
                dbc.CardHeader(html.H4("Handle Blood Request", className="text-center text-white"), className="bg-success"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Request ID", className="text-white"),
                            dbc.Input(id="request_id_input", type="text", placeholder="Enter Request ID"),
                        ], width=4),

                        dbc.Col([
                            dbc.Label("Blood Group", className="text-white"),
                            dbc.Input(id="blood_type_input", type="text", placeholder="Enter Blood Group"),
                        ], width=4),
                    ], className="mb-3"),

                    dbc.Row([
                        dbc.Col([
                            dbc.Button("Approve Request", id="approve_request_btn", color="primary", className="w-100"),
                        ], width=6),
                        dbc.Col([
                            dbc.Button("Complete Request", id="complete_request_btn", color="warning", className="w-100"),
                        ], width=6),
                    ]),
                    html.Div(id="approve_status", className="mt-3 text-white"),  # ✅ Approve status
                    html.Div(id="complete_status", className="mt-3 text-white")
                ]),
            ], className="shadow-lg mt-4 bg-dark"),

            # 🔄 Auto-Check for Expired Requests (Runs Every 5 Minutes)
            dcc.Interval(
                id="interval-scheduled-requests",
                interval=300000,  # 🔄 Runs every 5 minutes (300,000 ms)
                n_intervals=0
            )
        ], width=10, className="p-4 bg-dark")



    elif pathname == "/emergency":
        bloodbank_id = session.get("bloodbank_id")
        if not bloodbank_id:
            return html.H3("⚠ No BloodBank ID Provided!", className="text-center text-danger mt-5")

        emergency_requests = fetch_emergency_requests(bloodbank_id)
        print(f"Emergency requests data: {emergency_requests}")
        if not emergency_requests:  # Handle empty list case
         return dbc.Col([
            html.H1("Emergency Blood Requests", className="text-center mt-3 text-white"),
            dbc.Alert("No emergency requests found.", color="info", className="mt-3")
        ], width=10, className="p-4 bg-dark")
       # Count the number of requests

        return dbc.Col([
            # Header with Emergency Bell Icon and Count
            html.H1("Emergency Blood Requests", className="text-center mt-3 text-white"),
                    
            # Emergency Requests Table
            dbc.Card([
                dbc.CardHeader(html.H4("Urgent Requests", className="text-center text-white"), className="bg-danger"),
                dbc.CardBody([
                    html.Div([
                        dbc.Table([
                            html.Thead(html.Tr([
                                html.Th("Request ID", className="text-white bg-dark"),
                                html.Th("Patient ID", className="text-white bg-dark"),
                                html.Th("Name", className="text-white bg-dark"),
                                html.Th("Blood Group", className="text-white bg-dark"),
                                html.Th("Contact", className="text-white bg-dark"),
                                html.Th("Reason", className="text-white bg-dark"),
                                html.Th("Hospital Address", className="text-white bg-dark"),
                            ])),
                            html.Tbody([
                                html.Tr([
                                   html.Td(str(req.get("request_id", "N/A"))),  # Use .get() with default
        html.Td(str(req.get("patient_id", "N/A"))),
        html.Td(str(req.get("patient_name", "N/A"))),
        html.Td(str(req.get("blood_type", "N/A"))),
        html.Td(str(req.get("patient_contact", "N/A"))),
        html.Td(str(req.get("reason", "N/A"))),
        html.Td(str(req.get("hospital_address", "N/A"))),
                                ]) for req in emergency_requests
                            ])
                        ], bordered=True, striped=True, hover=True, className="table-dark text-white"),
                    ], style={
                        "maxHeight": "200px",  # Adjust height for better scrolling
                        "overflowY": "scroll",
                        "border": "1px solid #ddd",
                        "borderRadius": "5px"
                    }),
                ]),
            ], className="shadow-lg mt-4"),

            # Input fields for confirming blood request
            dbc.Card([
                dbc.CardHeader(html.H4("Confirm Blood Request", className="text-center text-white"), className="bg-danger"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Blood Group", className="text-white"),
                            dbc.Input(id="blood_type_input", type="text", placeholder="Enter Blood Group"),
                        ], width=4),
                        dbc.Col([
                            dbc.Label("No. of Blood Packets", className="text-white"),
                            dbc.Input(id="packet_count_input", type="number", min=1, placeholder="Enter Quantity"),
                        ], width=4),
                        dbc.Col([
                            dbc.Label("Request ID", className="text-white"),
                            dbc.Input(id="request_id_input", placeholder="Enter Request ID"),
                        ], width=4),
                    ], className="mb-3"),
                    
                    # Confirm Button
                    dbc.Button("Confirm", id="confirm-btn", color="success", className="w-100"),
                    html.Div(id="confirm-status", className="mt-3")
                ]),
            ], className="shadow-lg mt-4 bg-dark text-white"),

        ], width=10, className="p-4 bg-dark")




    elif pathname == "/request-blood":
        bloodbank_id = session.get("bloodbank_id")
        if not bloodbank_id:
            return html.H3("⚠ No BloodBank ID Provided!", className="text-center text-danger mt-5")
        
        return html.Div(
                    [
                        html.H2("Blood Donation Request", style={"textAlign": "center", "marginBottom": "20px"}),
                        html.Div(
                            [
                                html.Button(
                                    "Send Email to Eligible Donors",
                                    id="send_email_btn",
                                    n_clicks=0,
                                    style={
                                        "padding": "15px 30px",
                                        "fontSize": "16px",
                                        "cursor": "pointer",
                                        "backgroundColor": "#28a745",
                                        "color": "white",
                                        "border": "none",
                                        "borderRadius": "5px",
                                        "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
                                        "transition": "background-color 0.3s ease"
                                    }
                                ),
                                html.Div(
                                    id="email_status",
                                    style={"marginTop": "20px", "textAlign": "center", "color": "#28a745"}
                                )
                            ],
                            style={"display": "flex", "flexDirection": "column", "justifyContent": "center", "alignItems": "center"}
                        )
                    ],
                    style={"display": "flex", "flexDirection": "column", "justifyContent": "center", "alignItems": "center", "height": "100vh"}
                )
        
    
    return generate_dashboard_layout(bloodbank_id)

# -------------------- Callback for "Update Eligibility" Button --------------------



@app.callback(
    Output("email_status", "children"),
    Input("send_email_btn", "n_clicks")
)
def update_email_status(n_clicks):
    if n_clicks > 0:
        return send_email()
    return ""


from dash.exceptions import PreventUpdate

@app.callback(
    Output("update-eligibility-msg", "children"),
    Input("update-eligibility-btn", "n_clicks"),
    State("bloodbank-store", "data"),
    prevent_initial_call=True
)
def handle_update_eligibility(n_clicks, stored_data):
    # Instead of using stored_data, get bloodbank_id from session
    bloodbank_id = session.get("bloodbank_id")
    if not n_clicks:
        raise PreventUpdate
    if not bloodbank_id:
        return "⚠ No BloodBank ID Provided!"
    try:
        updated_count = update_eligibility_status(bloodbank_id)
        if updated_count > 0:
            return f"✅ Updated {updated_count} donors to 'Eligible' status."
        else:
            return "✅ No donors needed updates."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# -------------------- Logout Button Callback --------------------
@app.callback(
    Output("url", "href"),
    Input("logout-btn", "n_clicks"),
    prevent_initial_call=True
)
def logout(n_clicks):
    from flask import session
    session.pop("bloodbank_id", None)
    return "/homepage/" 
# -------------------- Run the Dash App --------------------
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

