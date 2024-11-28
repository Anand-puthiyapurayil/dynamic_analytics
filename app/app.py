import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, dash_table
import plotly.express as px
import pandas as pd
import base64
import io
from geopy.geocoders import Nominatim
from functools import lru_cache

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# Helper function to preprocess uploaded data
def preprocess_csv(contents):
    """
    Preprocess the uploaded CSV file and clean the data while retaining original data types.
    """
    # Decode file contents
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string).decode("utf-8")

    # Load the CSV into a DataFrame
    data = pd.read_csv(io.StringIO(decoded))

    # Handle missing values
    data.fillna("N/A", inplace=True)

    return data

# Helper function to get latitude and longitude for city names
@lru_cache(maxsize=100)
def get_coordinates(city):
    """
    Fetch latitude and longitude for a given city name using Nominatim.
    Uses caching to avoid repeated API calls for the same city.
    """
    try:
        geolocator = Nominatim(user_agent="geoapiExercises")
        location = geolocator.geocode(city)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Error fetching coordinates for {city}: {e}")
    return None, None

# Layout of the app
app.layout = dbc.Container(
    fluid=True,
    children=[
        dcc.Store(id="data-store"),  # Store for uploaded data
        dcc.Store(id="chart-store", data=[]),  # Store for charts
        dbc.NavbarSimple(
            brand="Advanced Data Analytics Dashboard",
            brand_href="#",
            color="primary",
            dark=True,
        ),
        dbc.Row(
            dbc.Col(html.H1("Upload and Explore Data", className="text-center text-primary mt-3"), width=12),
        ),
        dbc.Row(
            [
                # Sidebar for Upload and Options
                dbc.Col(
                    dbc.Card(
                        [
                            html.H3("Upload CSV File", className="text-center text-white"),
                            dcc.Upload(
                                id="upload-data",
                                children=dbc.Button("Upload File", color="primary", className="w-100"),
                                multiple=False,
                            ),
                            html.Div(id="upload-status", className="mt-3"),
                            html.Hr(),
                            html.H4("Scoping Filters", className="text-white"),
                            dcc.Dropdown(
                                id="filter-column",
                                placeholder="Select Column to Filter By",
                                style={"color": "black"},
                            ),
                            dcc.Checklist(
                                id="filter-values",
                                style={"color": "white"},
                            ),
                            html.Hr(),
                            html.H4("Chart Options", className="text-white"),
                            dcc.Dropdown(
                                id="x-axis-feature",
                                placeholder="Select X-axis",
                                style={"color": "black"},
                            ),
                            dcc.Dropdown(
                                id="y-axis-feature",
                                placeholder="Select Y-axis",
                                style={"color": "black"},
                            ),
                            dcc.Dropdown(
                                id="color-feature",
                                placeholder="Select Color-Coding Column",
                                style={"color": "black"},
                            ),
                            dcc.Dropdown(
                                id="chart-type",
                                options=[
                                    {"label": "Scatter Plot", "value": "scatter"},
                                    {"label": "Bar Chart", "value": "bar"},
                                    {"label": "Line Chart", "value": "line"},
                                    {"label": "Pie Chart", "value": "pie"},
                                    {"label": "Map (Geo)", "value": "map"},
                                    {"label": "Histogram", "value": "histogram"},
                                    {"label": "Box Plot", "value": "box"},
                                ],
                                placeholder="Select Chart Type",
                                style={"color": "black"},
                            ),
                            html.Hr(),
                            html.H4("Customization", className="text-white"),
                            dcc.Dropdown(
                                id="chart-template",
                                options=[
                                    {"label": "Plotly", "value": "plotly"},
                                    {"label": "Plotly Dark", "value": "plotly_dark"},
                                    {"label": "Seaborn", "value": "seaborn"},
                                    {"label": "Simple White", "value": "simple_white"},
                                ],
                                placeholder="Select Chart Template",
                                style={"color": "black"},
                            ),
                            dbc.Button(
                                "Generate Chart", id="generate-chart", color="success", className="mt-3 w-100"
                            ),
                        ],
                        body=True,
                        style={"backgroundColor": "#343a40"},
                    ),
                    width=3,
                ),
                # Main content for data preview, charts, and analytics
                dbc.Col(
                    [
                        dbc.Card(id="data-preview", body=True, className="mt-3"),
                        dbc.Card(
                            [
                                html.H4("Analytics Summary", className="text-white"),
                                html.Div(id="analytics-summary", style={"color": "white"}),
                            ],
                            body=True,
                            style={"backgroundColor": "#3c4043"},
                        ),
                        dbc.Row(id="chart-output", className="mt-3"),
                    ],
                    width=9,
                ),
            ]
        ),
    ],
)

# Callback to handle data upload and dynamically generate dropdown options
@app.callback(
    [
        Output("data-store", "data"),
        Output("upload-status", "children"),
        Output("data-preview", "children"),
        Output("filter-column", "options"),
        Output("x-axis-feature", "options"),
        Output("y-axis-feature", "options"),
        Output("color-feature", "options"),
        Output("analytics-summary", "children"),
    ],
    [Input("upload-data", "contents")],
    [State("upload-data", "filename")],
)
def handle_data(contents, filename):
    if contents:
        try:
            # Preprocess the uploaded file
            data = preprocess_csv(contents)

            # Generate dropdown options dynamically
            column_options = [{"label": col, "value": col} for col in data.columns]
            numeric_options = [{"label": col, "value": col} for col in data.select_dtypes(include=["number"]).columns]

            # Generate analytics summary
            summary = f"""
            Total Rows: {len(data)} | Total Columns: {len(data.columns)} | Missing Values: {data.isnull().sum().sum()}
            """
            analytics_summary = html.Div(summary)

            # Preview table
            preview_table = dash_table.DataTable(
                data=data.to_dict("records"),
                columns=[{"name": col, "id": col} for col in data.columns],
                style_table={"overflowX": "auto"},
                page_size=10,
            )
            return (
                data.to_dict("records"),
                dbc.Alert("File uploaded successfully!", color="success"),
                preview_table,
                column_options,
                column_options,
                numeric_options,
                column_options,
                analytics_summary,
            )

        except Exception as e:
            return None, dbc.Alert(f"Error processing file: {e}", color="danger"), None, [], [], [], [], ""

    return None, dbc.Alert("No file uploaded.", color="warning"), None, [], [], [], [], ""

# Callback to update filter values dynamically based on the selected column
@app.callback(
    Output("filter-values", "options"),
    Input("filter-column", "value"),
    State("data-store", "data"),
)
def update_filter_values(filter_column, data):
    if data and filter_column:
        df = pd.DataFrame(data)
        unique_values = df[filter_column].unique()
        return [{"label": str(val), "value": str(val)} for val in unique_values]
    return []

# Callback for generating charts dynamically and stacking them
@app.callback(
    Output("chart-store", "data"),
    [
        Input("generate-chart", "n_clicks"),
        State("filter-column", "value"),
        State("filter-values", "value"),
        State("x-axis-feature", "value"),
        State("y-axis-feature", "value"),
        State("color-feature", "value"),
        State("chart-template", "value"),
        State("chart-type", "value"),
        State("data-store", "data"),
        State("chart-store", "data"),
    ],
    prevent_initial_call=True,
)
def generate_chart(
    n_clicks,
    filter_column,
    filter_values,
    x_feature,
    y_feature,
    color_feature,
    template,
    chart_type,
    data,
    existing_charts,
):
    if not data:
        return existing_charts

    df = pd.DataFrame(data)

    # Apply scoping filters
    if filter_column and filter_values:
        df = df[df[filter_column].isin(filter_values)]

    try:
        if chart_type == "map":
            # Add latitude and longitude for cities
            df[["lat", "lon"]] = df["City"].apply(
                lambda city: pd.Series(get_coordinates(city))
            )
            df = df.dropna(subset=["lat", "lon"])  # Drop rows with missing coordinates

            if df.empty:
                print("No valid coordinates found for the selected data.")
                return existing_charts  # Return without adding a new chart

            # Create map chart
            fig = px.scatter_geo(
                df,
                lat="lat",
                lon="lon",
                size=y_feature,
                color=color_feature,
                template=template or "plotly_dark",
                title="Map Visualization",
            )
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_feature, y=y_feature, color=color_feature, template=template or "plotly_dark")
        elif chart_type == "bar":
            fig = px.bar(df, x=x_feature, y=y_feature, color=color_feature, template=template or "plotly_dark")
        elif chart_type == "line":
            fig = px.line(df, x=x_feature, y=y_feature, color=color_feature, template=template or "plotly_dark")
        elif chart_type == "pie":
            fig = px.pie(df, names=x_feature, values=y_feature, template=template or "plotly_dark")
        elif chart_type == "histogram":
            fig = px.histogram(df, x=x_feature, color=color_feature, template=template or "plotly_dark")
        elif chart_type == "box":
            fig = px.box(df, x=x_feature, y=y_feature, color=color_feature, template=template or "plotly_dark")
        else:
            return existing_charts

        # Append the new chart to existing charts
        existing_charts.append(dcc.Graph(figure=fig))
        return existing_charts

    except Exception as e:
        print(f"Error generating chart: {e}")
        return existing_charts

# Callback to update the chart output with stacked charts
@app.callback(
    Output("chart-output", "children"),
    Input("chart-store", "data"),
)
def update_chart_output(charts):
    return charts

if __name__ == "__main__":
    app.run_server(debug=True)
