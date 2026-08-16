import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input
from server import server  # Import the shared Flask instance

app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname='/homepage/',
    external_stylesheets=[dbc.themes.FLATLY]
)

# Navbar
navbar = dbc.Navbar(
    dbc.Container([
        html.Img(src=app.get_asset_url("logo.png"), height="40px", className="me-2"),
        dbc.NavbarBrand("BloodLink", className="fw-bold fs-4"),
        dbc.Nav([
            dbc.NavItem(dbc.NavLink("Requests For Blood", href="/dash/recipients", external_link=True)),
            dbc.NavItem(dbc.NavLink("Register", href="/bloodbank/register", external_link=True)),
            dbc.DropdownMenu(
                label="Login",
                children=[
                    dbc.DropdownMenuItem("Admin Login", href="/admin/login", external_link=True),
                    dbc.DropdownMenuItem("Blood Bank Login", href="/bblogin", external_link=True),
                    dbc.DropdownMenuItem("Donor Login", href="/login", external_link=True),
                ],
                nav=True, in_navbar=True
            ),
        ], className="ms-auto", navbar=True),
    ]),
    color="danger", dark=True, className="mb-4"
)

footer = html.Footer(
    dbc.Container(
        html.P("© 2025 Blood Link. All Rights Reserved.", className="text-white text-center"),
    ),
    className="footer-overlay"
)

homepage_layout = html.Div([
    navbar,
    html.Div(className="homepage-background"),
    footer
])

# Routing placeholder
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    return homepage_layout
