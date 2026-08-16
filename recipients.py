import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, no_update
import pandas as pd
from flask import Flask
import mysql.connector
from datetime import datetime
from server import server

app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://use.fontawesome.com/releases/v5.15.4/css/all.css",
        "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap"
    ],
    routes_pathname_prefix='/dash/recipients/',
    requests_pathname_prefix='/dash/recipients/',
    suppress_callback_exceptions=True
)
app.title = "BloodLink"

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '@Pritu50421',
    'database': 'final'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Sample User Data
# user_data = {
#     "name": "Piyush Singh",
#     "email": "piyush@example.com",
#     "blood_type": "AB+"
# }

# Custom styles
CARD_STYLE = {
    "background-color": "#2C3E50",
    "border-radius": "15px",
    "box-shadow": "0 4px 6px rgba(0, 0, 0, 0.1)",
    "margin-bottom": "20px",
    "padding": "20px"
}

INPUT_STYLE = {
    "background-color": "#34495E",
    "border": "1px solid #445566",
    "border-radius": "8px",
    "color": "white"
}

BUTTON_STYLE = {
    "background-color": "#E74C3C",
    "border": "none",
    "border-radius": "8px",
    "padding": "12px 24px",
    "font-weight": "600",
    "transition": "all 0.3s ease"
}

# Navigation Menu
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="/dash/recipients/", style={"color": "white"})),
        dbc.NavItem(dbc.NavLink("Blood Request Queue", href="/dash/recipients/queue", style={"color": "white"})),
    ],
    brand="🩸 BloodLink",
    brand_href="/dash/recipients/",
    color="dark",
    dark=True,
    style={"padding": "15px", "margin-bottom": "30px"}
)

# Blood Request Form Page
request_form_layout = dbc.Container(
    fluid=True,
    children=[
        navbar,
        dbc.Container([
            html.Div(
                style={
                    "text-align": "center",
                    "margin-bottom": "40px",
                    "color": "white"
                },
                children=[
                    html.H1("Blood Request Form", className="display-4 mb-3"),
                    html.H4(f"Welcome!", className="text-muted")
                ]
            ),

            # Patient Details Card
            dbc.Card(
                dbc.CardBody([
                    html.H3("Patient Details", className="card-title mb-4"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Input(
                                id="patient_name",
                                placeholder="Patient Name",
                                type="text",
                                className="mb-3",
                                style=INPUT_STYLE
                            ),
                            dbc.Input(
                                id="patient_age",
                                placeholder="Patient Age",
                                type="number",
                                className="mb-3",
                                style=INPUT_STYLE
                            ),
                            dcc.Dropdown(
                                id="patient_gender",
                                options=[
                                    {"label": "Male", "value": "Male"},
                                    {"label": "Female", "value": "Female"},
                                    {"label": "Other", "value": "Other"}
                                ],
                                placeholder="Select Gender",
                                className="mb-3",
                                style={"background-color": "#34495E", "color": "black"}
                            ),
                        ], width=6),
                        dbc.Col([
                            dbc.Input(
                                id="patient_contact",
                                placeholder="Patient Contact",
                                type="text",
                                className="mb-3",
                                style=INPUT_STYLE
                            ),
                            dbc.Input(
                                id="patient_email",
                                placeholder="Patient Email",
                                type="email",
                                className="mb-3",
                                style=INPUT_STYLE
                            ),
                            dbc.Textarea(
                                id="patient_address",
                                placeholder="Patient Address",
                                className="mb-3",
                                style=INPUT_STYLE
                            ),
                        ], width=6),
                    ]),
                ]),
                style=CARD_STYLE
            ),

            # Request Type Card
            dbc.Card(
                dbc.CardBody([
                    html.H3("Request Type", className="card-title mb-4"),
                    dbc.RadioItems(
                        id="request_type",
                        options=[
                            {"label": "Emergency", "value": "Emergency"},
                            {"label": "Scheduled", "value": "Scheduled"},
                        ],
                        inline=True,
                        style={"color": "white"}
                    ),
                    html.Div(
            id="scheduled_date_container",
            children=[
                html.Br(),
                html.H5("Select Scheduled Date", className="card-title mb-3"),
                dcc.DatePickerSingle(
                    id='scheduled_date',
                    min_date_allowed=datetime.now().date(),
                    initial_visible_month=datetime.now().date(),
                    date=datetime.now().date(),
                    style={"background-color": "#34495E", "color": "black"}
                )
            ],
            style={"display": "none"}  # Initially hidden
        )
                ]),
                
                style=CARD_STYLE
            ),
            

            # Terms and Conditions Card
            dbc.Card(
                dbc.CardBody([
                    html.H3("Terms and Conditions", className="card-title mb-4"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Checklist(
                                id="terms_checklist",
                                options=[
                                    {"label": "I agree to blood collection timings (9:00 AM - 1:00 PM and 4:00 PM - 8:00 PM)", "value": "timing"},
                                    {"label": "I will provide valid medical documents/prescription during collection", "value": "documents"},
                                    {"label": "I understand blood will only be issued to the registered patient", "value": "patient"},
                                    {"label": "I acknowledge that misuse will result in legal action", "value": "legal"},
                                    {"label": "I understand emergency requests are prioritized based on availability", "value": "emergency"}
                                ],
                                style={"color": "white"},
                                className="mb-3"
                            ),
                        ], width=12)
                    ])
                ]),
                style=CARD_STYLE
            ),

            # Location and Hospital Selection Card
            dbc.Card(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.H3("Enter Location", className="card-title mb-4"),
                            dbc.Input(
                    id="location_input",
                    placeholder="Enter location (city or area)",
                    type="text",
                    className="mb-3",
                    style=INPUT_STYLE
                ),
            ], width=6),
                        dbc.Col([
                            html.H3("Available Blood Banks", className="card-title mb-4"),
                            dcc.Dropdown(
                                id="hospital_dropdown",
                    placeholder="Blood banks will appear after entering location",
                    style={"background-color": "#34495E", "color": "black"},
                    disabled=True
                            ),
                        ], width=6),
                    ]),
                ]),
                style=CARD_STYLE
            ),

            # Blood Group Selection Card
            dbc.Card(
                dbc.CardBody([
                    html.H3("Choose Blood Group", className="card-title mb-4"),
                    dcc.Dropdown(
                        id="blood_group_dropdown",
                        options=[
                            {"label": "A+", "value": "A+"},
                            {"label": "B+", "value": "B+"},
                            {"label": "O+", "value": "O+"},
                            {"label": "AB+", "value": "AB+"},
                            {"label": "A-", "value": "A-"},
                            {"label": "B-", "value": "B-"},
                            {"label": "O-", "value": "O-"},
                            {"label": "AB-", "value": "AB-"},
                        ],
                        placeholder="Select Blood Group",
                        style={"background-color": "#34495E", "color": "black"}
                    ),
                ]),
                style=CARD_STYLE
            ),

            # Reason Card
            dbc.Card(
                dbc.CardBody([
                    html.H3("Reason for Blood Request", className="card-title mb-4"),
                    dbc.Textarea(
                        id="reason_input",
                        placeholder="Please provide detailed reason for blood request...",
                        style={**INPUT_STYLE, "height": "150px"}
                    ),
                ]),
                style=CARD_STYLE
            ),

            # Submit Button
            html.Div(
                [
                    dbc.Button(
                        "Submit Request",
                        id="submit_request",
                        color="danger",
                        size="lg",
                        style=BUTTON_STYLE
                    ),
                    html.Div(
                        id="submission_status",
                        className="mt-3",
                        style={
                            "color": "white",
                            "font-weight": "bold",
                            "margin-top": "20px"
                        }
                    )
                ],
                style={"text-align": "center", "margin-top": "40px", "margin-bottom": "40px"}
            ),
        ], style={"max-width": "1200px"})
    ],
    style={"background-color": "#1A1A1A", "min-height": "100vh", "padding-bottom": "50px"}
)

# Blood Request Queue Page
# Updated Blood Request Queue Page
queue_layout = html.Div([
    dbc.Navbar(
        dbc.Container([
            html.A([
                html.I(className="fas fa-tint me-2 text-danger"),
                "BloodLink"
            ], href="/dash/recipients/", className="navbar-brand text-white"),
            dbc.Nav([
                dbc.NavLink("Dashboard", href="/dash/recipients/", className="text-white"),
                dbc.NavLink("Blood Request Queue", href="/dash/recipients/queue", className="text-white active"),
            ], className="ms-auto")
        ]),
        dark=True,
        color="dark",
        className="mb-4"
    ),
    dbc.Container([
        html.H1("Blood Request Queue", className="text-center mb-4 text-white"),
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Input(
                            id="patient-identifier",
                            placeholder="Enter your contact number or email",
                            type="text",
                            style=INPUT_STYLE
                        )
                    ], width=8),
                    dbc.Col([
                        dbc.Button(
                            "Check Position",
                            id="check-position-btn",
                            color="danger",
                            style=BUTTON_STYLE
                        )
                    ], width=4)
                ]),
                html.Div(id="queue-content", className="mt-4"),
                html.Div(id="queue-table", className="mt-4")
            ]),
            style=CARD_STYLE
        )
    ])
])
@app.callback(
    Output("hospital_dropdown", "options"),
    Output("hospital_dropdown", "disabled"),
    Input("location_input", "value")
)
def update_blood_banks(location):
    if not location:
        return [], True
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Query to fetch blood banks in the specified location
        query = "SELECT bloodbank_id, name FROM bloodbanks WHERE city LIKE %s"
        cursor.execute(query, (f"%{location}%",))
        blood_banks = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Create dropdown options
        options = [{"label": bank["name"], "value": bank["bloodbank_id"]} 
                  for bank in blood_banks]
        
        return options, False  # Enable dropdown if options found
    
    except Exception as e:
        print(f"Error fetching blood banks: {e}")
        return [], True

# App Layout
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    html.Div(id="page_content")
])
@app.callback(
    Output("scheduled_date_container", "style"),
    Input("request_type", "value")
)
def toggle_date_picker(request_type):
    if request_type == "Scheduled":
        return {"display": "block", "margin-top": "15px"}
    return {"display": "none"}
# Database submission callback
# Database submission callback - THIS IS THE CORRECTED VERSION
@app.callback(
    Output("submission_status", "children"),
    [Input("submit_request", "n_clicks")],
    [State("patient_name", "value"),
     State("patient_age", "value"),
     State("patient_gender", "value"),
     State("patient_contact", "value"),
     State("patient_email", "value"),
     State("patient_address", "value"),
     State("request_type", "value"),
     State("scheduled_date", "date"),
     State("location_input", "value"), 
     State("hospital_dropdown", "value"),
     State("blood_group_dropdown", "value"),
     State("reason_input", "value")]
)
def handle_submission(n_clicks, name, age, gender, contact, email, address, 
                     request_type, scheduled_date, location, bloodbank_id, blood_type, reason):
    if not n_clicks:
        return no_update
    
    if not all([name, age, gender, contact, email, blood_type, reason]):
        return dbc.Alert("Please fill all required fields", color="danger")
    
    if request_type == "Scheduled" and not scheduled_date:
        return dbc.Alert("Please select a date for scheduled request", color="danger")
    
    if not location or not bloodbank_id:
        return dbc.Alert("Please enter location and select a blood bank", color="danger")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert patient data
        patient_query = """
        INSERT INTO patients 
        (patient_name,bloodbank_id, patient_contact, age, gender, location, email, emergency_case) 
        VALUES (%s, %s, %s,%s,%s, %s, %s, %s)
        """
        emergency_case = 1 if request_type == "Emergency" else 0
        patient_values = (name,bloodbank_id, contact, age, gender, location, email, emergency_case)
        cursor.execute(patient_query, patient_values)
        patient_id = cursor.lastrowid
        
        # Insert blood request
        request_query = """
        INSERT INTO bloodrequests 
        (patient_id, bloodbank_id, blood_type, quantity, reason, status, request_type, scheduled_date) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Handle scheduled date conversion
        scheduled_date_obj = None
        if request_type == "Scheduled" and scheduled_date:
            scheduled_date_obj = datetime.strptime(scheduled_date[:10], '%Y-%m-%d').date()
        
        # Default quantity to 1, status to Pending
        request_values = (patient_id, bloodbank_id, blood_type, 1, reason, "Pending", request_type, scheduled_date_obj)
        cursor.execute(request_query, request_values)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return dbc.Alert("Request submitted successfully!", color="success")
    
    except Exception as e:
        return dbc.Alert(f"Error submitting request: {str(e)}", color="danger")
    

@app.callback(
    [Output("queue-content", "children"),
     Output("queue-table", "children")],
    [Input("check-position-btn", "n_clicks")],
    [State("patient-identifier", "value")]
)
def display_queue_position(n_clicks, identifier):
    if not n_clicks or not identifier:
        return no_update, no_update
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First, find the patient and their blood bank
        patient_query = """
        SELECT p.patient_id, p.bloodbank_id, b.name AS bloodbank_name, p.patient_name
        FROM patients p
        JOIN bloodbanks b ON p.bloodbank_id = b.bloodbank_id
        WHERE p.patient_contact = %s OR p.email = %s
        """
        cursor.execute(patient_query, (identifier, identifier))
        patient = cursor.fetchone()
        
        if not patient:
            return dbc.Alert("No request found with that contact/email", color="warning"), no_update
        
        # Get all requests for this blood bank ordered by priority and date
        queue_query = """
        SELECT 
            br.request_id,
            br.patient_id,
            p.patient_name,
            br.blood_type,
            br.request_type,
            br.requested_date,
            br.status,
            ROW_NUMBER() OVER (ORDER BY 
                CASE WHEN br.request_type = 'Emergency' THEN 0 ELSE 1 END,
                br.requested_date
            ) AS queue_position
        FROM bloodrequests br
        JOIN patients p ON br.patient_id = p.patient_id
        WHERE br.bloodbank_id = %s AND br.status = 'Pending'
        ORDER BY 
            CASE WHEN br.request_type = 'Emergency' THEN 0 ELSE 1 END,
            br.requested_date
        """
        cursor.execute(queue_query, (patient['bloodbank_id'],))
        queue = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Find the patient's position in the queue
        patient_position = None
        patient_request_id = None
        for request in queue:
            if request['patient_id'] == patient['patient_id']:
                patient_position = request['queue_position']
                patient_request_id = request['request_id']
                break
        
        if not queue:
            return dbc.Alert("No pending requests found for this blood bank", color="info"), no_update
        
        # Create the queue table
        table_header = [
            html.Thead(html.Tr([
                html.Th("Position"),
                html.Th("Name"),
                html.Th("Blood Type"),
                html.Th("Request Type"),
                html.Th("Request Date"),
                html.Th("Status")
            ]))
        ]
        
        table_rows = []
        for request in queue:
            is_current_patient = request['patient_id'] == patient['patient_id']
            row_style = {
                'backgroundColor': '#E74C3C' if is_current_patient else 'inherit',
                'color': 'white' if is_current_patient else 'inherit'
            }
            
            table_rows.append(html.Tr([
                html.Td(request['queue_position']),
                html.Td(request['patient_name']),
                html.Td(request['blood_type']),
                html.Td(request['request_type']),
                html.Td(request['requested_date'].strftime('%Y-%m-%d %H:%M') if request['requested_date'] else ""),
                html.Td(request['status'])
            ], style=row_style))
        
        queue_table = dbc.Table(
            table_header + [html.Tbody(table_rows)],
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
            style={"color": "white"}
        )
        
        if patient_position:
            position_message = dbc.Alert(
                [
                    html.H4(f"Hello, {patient['patient_name']}!", className="alert-heading"),
                    html.P(f"Your current position in the queue at {patient['bloodbank_name']} is: {patient_position}"),
                    html.Hr(),
                    html.P("Emergency requests are prioritized. Your position may change if new emergency requests arrive.", 
                          className="mb-0")
                ],
                color="success",
                className="mb-4"
            )
        else:
            position_message = dbc.Alert(
                [
                    html.H4(f"Hello, {patient['patient_name']}!", className="alert-heading"),
                    html.P("Your request is not in the pending queue (may be completed or cancelled)"),
                ],
                color="info",
                className="mb-4"
            )
        
        return position_message, queue_table
    
    except Exception as e:
        return dbc.Alert(f"Error fetching queue: {str(e)}", color="danger"), no_update   
# Page routing callback
@app.callback(
    Output("page_content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/dash/recipients/queue":
        return queue_layout
    return request_form_layout

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)