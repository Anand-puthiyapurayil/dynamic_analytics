import os

def create_dash_project_structure():
    print("\n🚀 Welcome to the Dash Project Template Creator! 🚀\n")
    
    # Prompt for project name
    project_name = input("Enter the name of your Dash project: ").strip()
    if not project_name:
        print("Project name cannot be empty. Please try again.")
        return

    print(f"\n🔧 Setting up your Dash project: '{project_name}' in the current directory...\n")

    # Define the folder structure
    folders = {
        "app": "Contains the main Dash app files.",
        "scripts": "Scripts for data ingestion, transformation, and analytics.",
        "data/raw": "Store raw data files here.",
        "data/processed": "Store processed/cleaned data here.",
        "notebooks": "For Jupyter notebooks or exploratory analysis (optional).",
        "visualizations": "Store generated plots, reports, or assets.",
        "logs": "Store logs for debugging and tracking pipeline runs."
    }

    # Define the files to create
    files = {
        "app/app.py": """
# Main Dash app entry point
from dash import Dash, html, dcc

app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1("Welcome to Your Dash App!"),
    html.P("Customize this layout to fit your project needs."),
])

if __name__ == '__main__':
    app.run_server(debug=True)
""",
        "scripts/data_ingestion.py": """
# Script for data ingestion

def ingest_data():
    print("🚜 Ingesting data...")
    pass
""",
        "scripts/data_cleaning_pipeline.py": """
# Script for data cleaning

def clean_data(data):
    print("🧹 Cleaning data...")
    pass
""",
        "scripts/data_analytics_pipeline.py": """
# Script for data analytics

def analyze_data(data):
    print("📊 Analyzing data...")
    pass
""",
        "data/README.md": "📂 This folder contains raw and processed datasets.\n",
        "notebooks/README.md": "📓 Use this folder for Jupyter notebooks or experiments.\n",
        "visualizations/README.md": "🖼️ Store your plots, charts, and reports here.\n",
        "logs/README.md": "🗂️ Use this folder to store logs for debugging pipeline runs.\n",
        "requirements.txt": "# Add your project dependencies here (e.g., dash, pandas, plotly, etc.)\n",
        "README.md": f"# {project_name.capitalize()} Project\n\nThis project is built using Dash.\n\n## Folder Structure\n" +
                    "\n".join([f"- `{key}`: {desc}" for key, desc in folders.items()]) +
                    "\n\n## How to Run\n1. Install dependencies: `pip install -r requirements.txt`\n2. Run the app: `python app/app.py`\n"
    }

    # Create folders
    for folder, desc in folders.items():
        os.makedirs(folder, exist_ok=True)
        print(f"📁 Created folder: {folder} ({desc})")

    # Create files
    for file, content in files.items():
        with open(file, "w", encoding="utf-8") as f:  # Use utf-8 encoding
            f.write(content.strip())
        print(f"📄 Created file: {file}")

    print(f"\n🎉 Project '{project_name}' has been set up successfully!")
    print("📜 Next Steps:\n1. Install dependencies: `pip install -r requirements.txt`\n2. Start building your app in `app/app.py`.\n")

if __name__ == "__main__":
    create_dash_project_structure()
