from flask import Flask, session, redirect, url_for
import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import mysql.connector
from flask_session import Session

# Initialize Flask server
server = Flask(__name__)
server.secret_key = 'your_secret_key_here'  # Change this to a secure secret key
server.config['SESSION_TYPE'] = 'filesystem'
Session(server)

# Database Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "@Pritu50421",
    "database": "final"
}

def init_login_app(server):
    # Initialize Dash app with the shared Flask server
    app = dash.Dash(
        __name__,
        server=server,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        url_base_pathname='/bblogin/',
        suppress_callback_exceptions=True
    )
    app.title = "Blood Bank System - Login"

    # Custom styling
    BLOOD_RED = "#b30000"

    # Store the username and bloodbank_id
    app.layout = html.Div([
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="stored-username"),  # Store username for password reset
        dcc.Store(id="stored-bloodbank-id"),  # Store bloodbank_id for dashboard
        html.Div(id="page-content")
    ])

    # Login Page Layout
    login_layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Img(src=app.get_asset_url("logo.png"), style={"width": "120px", "marginBottom": "15px"}),
                    html.H2("Blood Bank Login", className="text-center mb-4", style={"color": BLOOD_RED}),
                    dbc.Input(id="username", type="text", placeholder="Enter Username", className="mb-3"),
                    dbc.Input(id="password", type="password", placeholder="Enter Password", className="mb-3"),
                    dbc.Button("Login", id="login-btn", color="danger", className="w-100"),
                    html.Br(),
                    dbc.Button("Forgot Password?", href="/bblogin/forgot-password", color="link", className="w-100 mt-2"),
                    html.Div(id="login-output", className="mt-3 text-center", style={"color": "red", "fontWeight": "bold"}),
                ], style={"padding": "30px", "borderRadius": "10px", "boxShadow": "0px 4px 8px rgba(0,0,0,0.2)",
                          "backgroundColor": "white", "maxWidth": "400px", "margin": "auto", "textAlign": "center"})
            ], width=12, className="d-flex justify-content-center align-items-center vh-100")
        ])
    ], fluid=True)

    # Forgot Password Page Layout
    forgot_password_layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("Forgot Password", className="text-center mb-4", style={"color": BLOOD_RED}),
                    dbc.Input(id="forgot-username", type="text", placeholder="Enter Username", className="mb-3"),
                    dbc.Input(id="forgot-email", type="email", placeholder="Enter Registered Email", className="mb-3"),
                    dbc.Button("Verify", id="verify-btn", color="primary", className="w-100"),
                    html.Div(id="verify-output", className="mt-3 text-center", style={"color": "red", "fontWeight": "bold"}),
                    dbc.Button("Back to Login", href="/bblogin/", color="link", className="w-100 mt-2"),
                ], style={"padding": "30px", "borderRadius": "10px", "boxShadow": "0px 4px 8px rgba(0,0,0,0.2)",
                          "backgroundColor": "white", "maxWidth": "400px", "margin": "auto", "textAlign": "center"})
            ], width=12, className="d-flex justify-content-center align-items-center vh-100")
        ])
    ], fluid=True)

    # Reset Password Page Layout
    reset_password_layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("Reset Password", className="text-center mb-4", style={"color": BLOOD_RED}),
                    dbc.Input(id="new-password", type="password", placeholder="Enter New Password", className="mb-3"),
                    dbc.Input(id="confirm-password", type="password", placeholder="Confirm New Password", className="mb-3"),
                    dbc.Button("Reset Password", id="reset-btn", color="success", className="w-100"),
                    html.Div(id="reset-output", className="mt-3 text-center", style={"color": "green", "fontWeight": "bold"}),
                    dbc.Button("Back to Login", href="/bblogin/", color="link", className="w-100 mt-2"),
                ], style={"padding": "30px", "borderRadius": "10px", "boxShadow": "0px 4px 8px rgba(0,0,0,0.2)",
                          "backgroundColor": "white", "maxWidth": "400px", "margin": "auto", "textAlign": "center"})
            ], width=12, className="d-flex justify-content-center align-items-center vh-100")
        ])
    ], fluid=True)

    @app.callback(Output("page-content", "children"), Input("url", "pathname"))
    def display_page(pathname):
        if pathname == "/bblogin/forgot-password":
            return forgot_password_layout
        elif pathname == "/bblogin/reset-password":
            return reset_password_layout
        return login_layout

    # Function to validate login and get bloodbank_id
    def validate_login(username, password):
        conn = None
        cursor = None
        try:
            # Ensure connection is established before proceeding
            conn = mysql.connector.connect(**db_config)
            if conn is None:
                print("Failed to establish database connection")
                return None
                
            cursor = conn.cursor(dictionary=True)
            query = "SELECT bloodbank_id FROM BloodBanks WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            return result["bloodbank_id"] if result else None
        except mysql.connector.Error as e:
            print(f"Database Error in validate_login: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in validate_login: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Function to validate username and Email and get bloodbank_id
    def validate_user(username, email):
        conn = None
        cursor = None
        try:
            # Ensure connection is established before proceeding
            conn = mysql.connector.connect(**db_config)
            if conn is None:
                print("Failed to establish database connection")
                return None
                
            cursor = conn.cursor(dictionary=True)
            query = "SELECT bloodbank_id FROM BloodBanks WHERE username = %s AND email = %s"
            cursor.execute(query, (username, email))
            result = cursor.fetchone()
            return result["bloodbank_id"] if result else None
        except mysql.connector.Error as e:
            print(f"Database Error in validate_user: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in validate_user: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # Function to update password
    def update_password(username, new_password):
        conn = None
        cursor = None
        try:
            # Ensure connection is established before proceeding
            conn = mysql.connector.connect(**db_config)
            if conn is None:
                print("Failed to establish database connection")
                return False
                
            cursor = conn.cursor()
            query = "UPDATE bloodbanks SET password = %s WHERE username = %s"
            print(f"Executing query: {query} with params: ({new_password}, {username})") 
            cursor.execute(query, (new_password, username))
            conn.commit()
            affected_rows = cursor.rowcount 
            print(f"Affected rows: {affected_rows}")  # Check if any rows were updated
            return affected_rows > 0  # Return True if at least one row was updated
        except mysql.connector.Error as e:
            print(f"Database Error in update_password: {e}")
            if conn:
                conn.rollback()  # Rollback transaction on error
            return False
        except Exception as e:
            print(f"Unexpected error in update_password: {e}")
            if conn:
                conn.rollback()  # Rollback transaction on error
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @app.callback(
        Output("login-output", "children"),
        Output("stored-bloodbank-id", "data"),
        Input("login-btn", "n_clicks"),
        State("username", "value"),
        State("password", "value"),
        prevent_initial_call=True
    )
    def check_login(n_clicks, username, password):
        if not username or not password:
            return "⚠ Please enter both Username and Password!", None
        
        bloodbank_id = validate_login(username, password)
        if bloodbank_id:
            # Store both username and bloodbank_id in Flask session
            session["username"] = username
            session["bloodbank_id"] = bloodbank_id
            # Redirect to dashboard
            return dcc.Location(href="/dashboard/", id="redirect"), bloodbank_id
        return "❌ Invalid Username or Password!", None

    @app.callback(
        Output("verify-output", "children"),
        Output("stored-username", "data"),
        Output("url", "pathname"),
        Input("verify-btn", "n_clicks"),
        State("forgot-username", "value"),
        State("forgot-email", "value"),
        prevent_initial_call=True
    )
    def verify_credentials(n_clicks, username, email):
        if not username or not email:
            return ["⚠ Please enter all details!", None, dash.no_update]
        
        bloodbank_id = validate_user(username, email)
        if bloodbank_id:
            return ["✅ Verified! Redirecting...", username, "/bblogin/reset-password"]
        return ["❌ Invalid details!", None, dash.no_update]

    @app.callback(
        Output("reset-output", "children"),
        Input("reset-btn", "n_clicks"),
        State("new-password", "value"),
        State("confirm-password", "value"),
        State("stored-username", "data"),
        prevent_initial_call=True
    )
    def reset_password_callback(n_clicks, new_password, confirm_password, username):
        if not username:
         return "⚠ Session expired. Please start the password reset process again."
        if not new_password or not confirm_password:
            return "⚠ Please enter and confirm your new password!"
        if new_password != confirm_password:
            return "❌ Passwords do not match!"
        if update_password(username, new_password):
            return html.Div([
            "✅ Password updated successfully!",
            dcc.Location(href="/bblogin/", id="redirect-to-login")
        ])
            # # After successful password reset, get the bloodbank_id
            # bloodbank_id = validate_user(username, None)  # We can modify this to fetch just by username
            # if bloodbank_id:
            #     session["username"] = username
            #     session["bloodbank_id"] = bloodbank_id
            #     return dcc.Location(href="/dashboard/", id="redirect-success")
        return "❌ Error updating password."

    return app

def init_dashboard_app(server):
    # Initialize Dash app for dashboard
    app = dash.Dash(
        __name__,
        server=server,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        url_base_pathname='/dashboard/',
        suppress_callback_exceptions=True
    )
    app.title = "Blood Bank System - Dashboard"

    # Custom styling
    BLOOD_RED = "#b30000"

    app.layout = html.Div([
        dcc.Location(id='url-dashboard', refresh=False),
        html.Div(id='dashboard-content')
    ])

    # Dashboard layout
    dashboard_layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H2("Blood Bank Dashboard", className="text-center mb-4", style={"color": BLOOD_RED}),
                    html.Hr(),
                    html.Div(id='welcome-message', className="mb-4"),
                    dbc.Button("Logout", href="/logout", color="danger", className="mb-4"),
                    # Add your dashboard components here
                    dbc.Card([
                        dbc.CardHeader("Blood Bank Information"),
                        dbc.CardBody(id='bloodbank-info')
                    ]),
                    html.Br(),
                    dbc.Card([
                        dbc.CardHeader("Blood Inventory"),
                        dbc.CardBody(id='blood-inventory')
                    ])
                ], style={"padding": "30px", "borderRadius": "10px", 
                          "backgroundColor": "white", "margin": "auto"})
            ], width=12)
        ])
    ], fluid=True)

    @app.callback(
        Output('dashboard-content', 'children'),
        Input('url-dashboard', 'pathname')
    )
    def display_dashboard(pathname):
        if 'bloodbank_id' not in session:
            return dcc.Location(href="/bblogin/", id="redirect-login")
        return dashboard_layout

    @app.callback(
        Output('welcome-message', 'children'),
        Output('bloodbank-info', 'children'),
        Input('dashboard-content', 'children')
    )
    def update_dashboard_content(_):
        if 'bloodbank_id' not in session:
            return "", ""
        
        bloodbank_id = session['bloodbank_id']
        username = session.get('username', 'User')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            # Get BloodBank info
            cursor.execute("SELECT * FROM BloodBanks WHERE bloodbank_id = %s", (bloodbank_id,))
            bloodbank_info = cursor.fetchone()
            
            # Get Blood Inventory
            cursor.execute("SELECT * FROM BloodInventory WHERE bloodbank_id = %s", (bloodbank_id,))
            blood_inventory = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Create welcome message
            welcome_msg = html.H3(f"Welcome, {username} (Blood Bank ID: {bloodbank_id})", style={"color": BLOOD_RED})
            
            # Create BloodBank info display
            if bloodbank_info:
                info_content = [
                    html.P(f"Name: {bloodbank_info.get('name', 'N/A')}"),
                    html.P(f"Location: {bloodbank_info.get('location', 'N/A')}"),
                    html.P(f"Contact: {bloodbank_info.get('contact', 'N/A')}"),
                    html.P(f"Email: {bloodbank_info.get('email', 'N/A')}")
                ]
            else:
                info_content = html.P("No information found for this Blood Bank.")
            
            # Create Blood Inventory display
            if blood_inventory:
                inventory_table = dbc.Table([
                    html.Thead(html.Tr([
                        html.Th("Blood Type"),
                        html.Th("Quantity"),
                        html.Th("Last Updated")
                    ])),
                    html.Tbody([
                        html.Tr([
                            html.Td(item['blood_type']),
                            html.Td(item['quantity']),
                            html.Td(str(item['last_updated']))
                        ]) for item in blood_inventory
                    ])
                ], striped=True, bordered=True, hover=True)
            else:
                inventory_table = html.P("No inventory records found.")
            
            return welcome_msg, [info_content, inventory_table]
            
        except mysql.connector.Error as e:
            print(f"Database Error: {e}")
            return html.H3("Welcome!"), html.P("Error loading data. Please try again later.")

    return app

# Initialize apps
login_app = init_login_app(server)
dashboard_app = init_dashboard_app(server)

@server.route('/')
def index():
    if 'bloodbank_id' in session:
        return redirect('/dashboard/')
    return redirect('/bblogin/')

@server.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('bloodbank_id', None)
    return redirect('/bblogin/')

if __name__ == '__main__':
    server.run(debug=True, port=8051)