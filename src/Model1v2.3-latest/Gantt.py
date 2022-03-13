import plotly
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import random

from pathlib import Path
import datetime as dt

# the keys is used for the colors / cataglories
keys_in_task = []

keys_in_ant = []

def FormatInTask(dict_res):
    res = []
    for task in dict_res:
        for element in dict_res[task]:
            # print(element['antenne'])
            if element['end'] == element['start']:
                continue
            else:
                keys_in_task.append(element['antenne'])
                res.append(dict(Task=task,Start=element['start'],Finish=element['end'],Resource=element['antenne']))
    return res

def FormatInAnt(dict_res,dict_req):
    res = []
    for task_id in dict_req['Satellite']:
        task = dict_req['Task number'][task_id]
        satellite = dict_req['Satellite'][task_id]
        keys_in_ant.append(satellite)
        for element in dict_res[task]:
            if element['end'] == element['start']:
                continue
            else:
                res.append(dict(Task=element['antenne'],Start=element['start'],Finish=element['end'],Resource=satellite))
    return res
   


colors = {
    'ANT1': 'rgb(220, 0, 0)',
    'ANT2': 'rgb(255, 79, 0)',
    'ANT3': 'rgb(203, 79, 168)',
    'ANT4': 'rgb(235, 207, 168)',
    'ANT5': 'rgb(25, 207, 168)',
    'ANT6': 'rgb(171, 207, 168)',
    'ANT7': 'rgb(122, 207, 168)',
    'ANT8': 'rgb(122, 136, 168)',
    'ANT9': 'rgb(122, 136, 237)',
    'ANT10': 'rgb(193, 79, 252)',
    'ANT11': 'rgb(234, 79, 160)',
    'ANT12': 'rgb(189, 208, 192)',
    'ANT13': 'rgb(222, 208, 192)',
    'ANT14': 'rgb(220, 123, 2)',
    'ANT15': 'rgb(220, 40, 224)',
    'ANT16': 'rgb(20, 12, 190)'
}


def constructColors(targets_as_list):
    dict_colors = {}
    for target in targets_as_list:
        r = random.randint(0,255)
        g = random.randint(0,255)
        b = random.randint(0,255)
        color = 'rgb('+str(r)+', '+str(g)+', '+str(b)+')'
        dict_colors[target] = color
    return dict_colors

def GanttForTask(dict_res,fig_name):

    part_colors = {}

    data = FormatInTask(dict_res)
    # another to create color table is to use the constructColors() function
    for key in keys_in_task:
        if key not in part_colors:
            part_colors[key] = colors[key]
    
    df = pd.DataFrame(data)
    # df['delta'] = df['Finish'] - df['Start']

    fig = ff.create_gantt(df,index_col='Resource', colors = part_colors, show_colorbar=True,group_tasks=True)
    fig.update_layout(xaxis_type='linear')
    fig.show()
    fig.write_image(fig_name)

    """
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Resource")
    fig.update_yaxes(autorange="reversed")
    fig.layout.xaxis.type = 'linear' # to make sure the xaxis integer
    # fig.data[0].x = df.delta.tolist()
    fig.show()
    """

'''
dict_req is the dictionary of requirements, an example of its structure is like:
    {'Task number': {0: 'TASK0', 1: 'TASK4', 2: 'TASK8', 3: 'TASK12', 4: 'TASK16', 5: 'TASK20', 6: 'TASK24', 7: 'TASK28', 8: 'TASK32', 9: 'TASK36'}, 
     'Satellite': {0: 'SAT15', 1: 'SAT12', 2: 'SAT21', 3: 'SAT17', 4: 'SAT07', 5: 'SAT09', 6: 'SAT22', 7: 'SAT11', 8: 'SAT18', 9: 'SAT03'}, 
     'Priority': {0: 8, 1: 8, 2: 8, 3: 8, 4: 8, 5: 8, 6: 8, 7: 8, 8: 8, 9: 8}, 
     'Duration': {0: 1851, 1: 1980, 2: 1810, 3: 2227, 4: 1983, 5: 2185, 6: 2328, 7: 2275, 8: 1934, 9: 1999}, 
     'Earliest': {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}, 
     'Latest': {0: 1207749, 1: 1207620, 2: 1207790, 3: 1207373, 4: 1207617, 5: 1207415, 6: 1207272, 7: 1207325, 8: 1207666, 9: 1207601}, 
     'Repetitive': {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1}, 
     'Number occ': {0: -1, 1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1, 8: -1, 9: -1}, 
     'Min time lag': {0: 25200, 1: 25200, 2: 25200, 3: 25200, 4: 25200, 5: 25200, 6: 25200, 7: 25200, 8: 25200, 9: 25200}, 
     'Max time lag': {0: 43200, 1: 43200, 2: 43200, 3: 43200, 4: 43200, 5: 43200, 6: 43200, 7: 43200, 8: 43200, 9: 43200}
    }
'''
def GanttForAntenne(dict_res,dict_req,fig_name):
    part_colors = {}

    data = FormatInAnt(dict_res,dict_req)
    
    part_colors = constructColors(keys_in_ant)
    # print(part_colors)
 
    df = pd.DataFrame(data)
    # df['delta'] = df['Finish'] - df['Start']

    fig = ff.create_gantt(df,index_col='Resource', colors = part_colors, show_colorbar=True,group_tasks=True)
    fig.update_layout(xaxis_type='linear')
    fig.show()
    fig.write_image(fig_name)

    return 0



def GanttPlan(input_path):
    EXCEL_FILE = Path.cwd() / input_path
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
    color = df["Color"]
    opacity = df ["Opacity"]
    information = df["Name"]
    # Create Gantt Chart
    fig = px.timeline(
        df, x_start=time_series_s, x_end=time_series_e, y=tasks, color=color, title="Task Overview", opacity = opacity, hover_name = information
    )
    # Upade/Change Layout
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(title_font_size=42, font_size=18, title_font_family="Arial")

    # Interactive Gantt
    # fig = ff.create_gantt(df)
    # Save Graph and Export to HTML
    plotly.offline.plot(fig, filename="Task_Overview_Gantt.html")


