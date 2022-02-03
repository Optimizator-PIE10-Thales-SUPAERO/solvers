import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd

def FormatInTask(dict_res):
    res = []
    for task in dict_res:
        for element in dict_res[task]:
            if element['end'] == element['start']:
                continue
            else:
                res.append(dict(Task=task,Start=element['start'],Finish=element['end'],Resource=element['antenne']))
    return res

def GanttForTask(dict_res):
    data = FormatInTask(dict_res)
    df = pd.DataFrame(data)
    # df['delta'] = df['Finish'] - df['Start']

    fig = ff.create_gantt(df,index_col='Resource', show_colorbar=True,group_tasks=True)
    fig.update_layout(xaxis_type='linear')
    fig.show()

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
