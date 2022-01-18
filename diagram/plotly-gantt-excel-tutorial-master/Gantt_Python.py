from pathlib import Path
import pandas as pd
import plotly
import plotly.express as px
import datetime as dt

# import plotly.figure_factory as ff

EXCEL_FILE = Path.cwd() / "diagram/plotly-gantt-excel-tutorial-master/Tasks.xlsx"

# Read Dataframe from Excel file
df = pd.read_excel(EXCEL_FILE)

# Assign Columns to variables
tasks = df["Task"]
start = df["Start"]
reference = dt.datetime(2022,1,1,0,0)
datetime_series_s = start.astype('timedelta64[s]') + reference
time_series_s = pd.to_datetime(datetime_series_s, unit='s')


finish = df["Finish"]
datetime_series_e = finish.astype('timedelta64[s]') + reference
time_series_e = pd.to_datetime(datetime_series_e, unit='s')
complete = df["Complete in %"]

opacity = df ["Opacity"]
information = df["Information"]
# Create Gantt Chart
fig = px.timeline(
    df, x_start=time_series_s, x_end=time_series_e, y=tasks, color=complete, title="Task Overview", opacity = opacity, hover_name = information
)

# Upade/Change Layout
fig.update_yaxes(autorange="reversed")
fig.update_layout(title_font_size=42, font_size=18, title_font_family="Arial")

# Interactive Gantt
# fig = ff.create_gantt(df)

# Save Graph and Export to HTML
plotly.offline.plot(fig, filename="Task_Overview_Gantt.html")
