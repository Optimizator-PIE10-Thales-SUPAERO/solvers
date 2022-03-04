import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd


keys = []

def FormatInTask(dict_res):
    res = []
    for task in dict_res:
        for element in dict_res[task]:
            # print(element['antenne'])
            if element['end'] == element['start']:
                continue
            else:
                keys.append(element['antenne'])
                res.append(dict(Task=task,Start=element['start'],Finish=element['end'],Resource=element['antenne']))
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

def GanttForTask(dict_res,fig_name):

    part_colors = {}

    data = FormatInTask(dict_res)
    
    for key in keys:
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

def GanttForAntenne(dict_res):
    return 0


"""
df = pd.DataFrame([
    dict(Task="Job A", Start='2009-01-01', Finish='2009-02-28', Resource="Alex"),
    dict(Task="Job B", Start='2009-03-05', Finish='2009-04-15', Resource="Alex"),
    dict(Task="Job C", Start='2009-02-20', Finish='2009-05-30', Resource="Max")
])

fig = px.timeline(df, x_start="Start", x_end="Finish", y="Resource", color="Resource")
fig.show()
"""

"""
df = [dict(Task="Job-1", Start='2017-01-01', Finish='2017-02-02', Resource='Complete'),
      dict(Task="Job-1", Start='2017-02-15', Finish='2017-03-15', Resource='Incomplete'),
      dict(Task="Job-2", Start='2017-01-17', Finish='2017-02-17', Resource='Not Started'),
      dict(Task="Job-2", Start='2017-01-17', Finish='2017-02-17', Resource='Complete'),
      dict(Task="Job-3", Start='2017-03-10', Finish='2017-03-20', Resource='Not Started'),
      dict(Task="Job-3", Start='2017-04-01', Finish='2017-04-20', Resource='Not Started'),
      dict(Task="Job-3", Start='2017-05-18', Finish='2017-06-18', Resource='Not Started'),
      dict(Task="Job-4", Start='2017-01-14', Finish='2017-03-14', Resource='Complete')]

colors = {'Not Started': 'rgb(220, 0, 0)',
          'Incomplete': (1, 0.9, 0.16),
          'Complete': 'rgb(0, 255, 100)'}

fig = ff.create_gantt(df, colors=colors, index_col='Resource', show_colorbar=True,
                      group_tasks=True)
fig.show()
"""
