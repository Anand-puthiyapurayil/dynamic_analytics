import streamlit as st
import pandas as pd
import json
import altair as alt

# Title of the Streamlit app
st.title("Dynamic Data Visualization with Multi-Level Drill-Down and Optional Features")

# File uploader for CSV data
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the uploaded CSV file
    df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully!")

    # Display the dataset
    st.header("Uploaded Dataset")
    st.dataframe(df)

    # Scoping: Allow users to optionally select columns
    if st.sidebar.checkbox("Enable Scoping"):
        st.sidebar.header("Scoping Options")
        scoped_columns = st.sidebar.multiselect(
            "Select Columns to Include in Visualizations",
            options=df.columns,
            default=df.columns.tolist()  # Default: include all columns
        )
        scoped_data = df[scoped_columns]
    else:
        scoped_data = df
        scoped_columns = df.columns.tolist()

    st.subheader("Scoped Data")
    st.dataframe(scoped_data)

    # Filtering: Add optional filtering options
    if st.sidebar.checkbox("Enable Filtering"):
        st.sidebar.header("Filtering Options")
        filtered_data = scoped_data.copy()

        for col in scoped_columns:
            if pd.api.types.is_numeric_dtype(scoped_data[col]):
                min_val, max_val = st.sidebar.slider(
                    f"Filter {col}",
                    min_value=float(scoped_data[col].min()),
                    max_value=float(scoped_data[col].max()),
                    value=(float(scoped_data[col].min()), float(scoped_data[col].max()))
                )
                filtered_data = filtered_data[(filtered_data[col] >= min_val) & (filtered_data[col] <= max_val)]
            else:
                unique_values = scoped_data[col].dropna().unique()
                selected_values = st.sidebar.multiselect(
                    f"Filter {col}",
                    options=unique_values,
                    default=unique_values.tolist()
                )
                filtered_data = filtered_data[filtered_data[col].isin(selected_values)]
    else:
        filtered_data = scoped_data

    st.subheader("Filtered Data")
    st.dataframe(filtered_data)

    # Group By: Add optional grouping and aggregation
    if st.sidebar.checkbox("Enable Group By"):
        st.sidebar.header("Group By Options")
        group_by_column = st.sidebar.selectbox(
            "Select a Column to Group By",
            options=scoped_columns,
            index=0  # Default to the first column
        )
        aggregation_method = st.sidebar.selectbox(
            "Select Aggregation Method",
            options=["Sum", "Mean", "Count", "Max", "Min"],
            index=0  # Default to 'Sum'
        )

        if group_by_column:
            if aggregation_method == "Sum":
                grouped_data = filtered_data.groupby(group_by_column).sum().reset_index()
            elif aggregation_method == "Mean":
                grouped_data = filtered_data.groupby(group_by_column).mean().reset_index()
            elif aggregation_method == "Count":
                grouped_data = filtered_data.groupby(group_by_column).size().reset_index(name='Count')
            elif aggregation_method == "Max":
                grouped_data = filtered_data.groupby(group_by_column).max().reset_index()
            elif aggregation_method == "Min":
                grouped_data = filtered_data.groupby(group_by_column).min().reset_index()

            st.subheader(f"Grouped Data by {group_by_column} ({aggregation_method})")
            st.dataframe(grouped_data)
        else:
            grouped_data = filtered_data
    else:
        grouped_data = filtered_data

    # Visualization: Allow users to visualize data
    if st.sidebar.checkbox("Enable Visualization"):
        st.sidebar.header("Visualization Options")
        chart_type = st.sidebar.selectbox(
            "Select Chart Type",
            options=["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart"]
        )
        x_axis = st.sidebar.selectbox("Select X-Axis", options=grouped_data.columns)
        y_axis = st.sidebar.selectbox(
            "Select Y-Axis (for numerical columns)",
            options=grouped_data.select_dtypes(include='number').columns
        )

        # Generate the selected chart
        st.subheader(f"{chart_type}")
        if chart_type == "Bar Chart":
            chart = alt.Chart(grouped_data).mark_bar().encode(
                x=alt.X(x_axis, title=x_axis),
                y=alt.Y(y_axis, title=y_axis),
                tooltip=[x_axis, y_axis]
            )
            st.altair_chart(chart, use_container_width=True)

        elif chart_type == "Line Chart":
            chart = alt.Chart(grouped_data).mark_line().encode(
                x=alt.X(x_axis, title=x_axis),
                y=alt.Y(y_axis, title=y_axis),
                tooltip=[x_axis, y_axis]
            )
            st.altair_chart(chart, use_container_width=True)

        elif chart_type == "Scatter Plot":
            chart = alt.Chart(grouped_data).mark_circle(size=60).encode(
                x=alt.X(x_axis, title=x_axis),
                y=alt.Y(y_axis, title=y_axis),
                tooltip=[x_axis, y_axis]
            )
            st.altair_chart(chart, use_container_width=True)

        elif chart_type == "Pie Chart":
            pie_chart = alt.Chart(grouped_data).mark_arc().encode(
                theta=alt.Theta(field=y_axis, type="quantitative"),
                color=alt.Color(field=x_axis, type="nominal"),
                tooltip=[x_axis, y_axis]
            )
            st.altair_chart(pie_chart, use_container_width=True)

    # Drill-Down: Add drill-down functionality
    st.sidebar.header("Define Drill-Down Hierarchy")
    drill_columns = st.sidebar.multiselect(
        "Select Drill-Down Hierarchy (e.g., Region → Country → City)",
        options=scoped_columns,
        default=scoped_columns[:3]  # Default: first three columns
    )

    numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
    if not numeric_columns:
        st.error("The dataset does not contain numeric columns for aggregation.")
    else:
        aggregation_column = st.sidebar.selectbox(
            "Select Column for Aggregation",
            options=numeric_columns
        )

        if len(drill_columns) < 2:
            st.warning("Please select at least two columns for the drill-down hierarchy.")
        else:
            # Function to dynamically generate the drill-down JSON
            def transform_data_for_drilldown(df, drill_columns, aggregation_column):
                result = {
                    "top_level": [],
                    "drilldown": []
                }
                for i, column in enumerate(drill_columns):
                    if i == 0:
                        grouped_data = df.groupby(column)[aggregation_column].sum().reset_index()
                        for _, row in grouped_data.iterrows():
                            drilldown_id = f"{column}_{row[column]}".replace(" ", "_")
                            result["top_level"].append({
                                "name": str(row[column]),
                                "y": float(row[aggregation_column]),
                                "drilldown": drilldown_id
                            })
                    else:
                        prev_columns = drill_columns[:i]
                        grouped_data = df.groupby(prev_columns + [column])[aggregation_column].sum().reset_index()
                        for _, row in grouped_data.iterrows():
                            prev_drilldown_id = "_".join([f"{col}_{row[col]}" for col in prev_columns]).replace(" ", "_")
                            current_drilldown_id = f"{prev_drilldown_id}_{column}_{row[column]}".replace(" ", "_")
                            drilldown_entry = next(
                                (entry for entry in result["drilldown"] if entry["id"] == prev_drilldown_id), None
                            )
                            if not drilldown_entry:
                                drilldown_entry = {"id": prev_drilldown_id, "data": []}
                                result["drilldown"].append(drilldown_entry)
                            drilldown_entry["data"].append({
                                "name": str(row[column]),
                                "y": float(row[aggregation_column]),
                                "drilldown": current_drilldown_id if i < len(drill_columns) - 1 else None
                            })
                return result

            # Generate drill-down chart data
            drilldown_data = transform_data_for_drilldown(filtered_data, drill_columns, aggregation_column)
            top_level = drilldown_data["top_level"]
            drilldown = drilldown_data["drilldown"]

            # Chart selection
            chart_type = st.sidebar.radio("Select Drill-Down Chart Type", ["Column Chart", "Pie Chart"])
            if chart_type == "Column Chart":
                highchart_config = f"""
                Highcharts.chart('container', {{
                    chart: {{ type: 'column' }},
                    title: {{ text: 'Drill-Down Column Chart' }},
                    xAxis: {{ type: 'category' }},
                    series: [{{ name: '{drill_columns[0]}', data: {json.dumps(top_level)} }}],
                    drilldown: {{ series: {json.dumps(drilldown)} }}
                }});"""
            else:
                highchart_config = f"""
                Highcharts.chart('container', {{
                    chart: {{ type: 'pie' }},
                    title: {{ text: 'Drill-Down Pie Chart' }},
                    series: [{{ name: '{drill_columns[0]}', data: {json.dumps(top_level)} }}],
                    drilldown: {{ series: {json.dumps(drilldown)} }}
                }});"""

            st.components.v1.html(
                f"""
                <html>
                <head>
                    <script src="https://code.highcharts.com/highcharts.js"></script>
                    <script src="https://code.highcharts.com/modules/drilldown.js"></script>
                </head>
                <body>
                    <div id="container"></div>
                    <script>{highchart_config}</script>
                </body>
                </html>
                """,
                height=600,
            )
else:
    st.warning("Please upload a CSV file to get started.")
