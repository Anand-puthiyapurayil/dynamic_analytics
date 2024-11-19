# Main Dash app entry point
from dash import Dash, html, dcc

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1("Welcome to Your Dash App!"),
    html.P("Customize this layout to fit your project needs."),
])

if __name__ == '__main__':
    app.run_server(debug=True)