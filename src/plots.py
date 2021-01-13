import plotly as py
import pandas as pd
import numpy as np
import json
import plotly.graph_objs as go

def create_plot(data = {}, label ="", label_x ="", label_y = ""):
    x = []
    y = []

    for key, value in data.items():
        y.append(value)
        x.append(key)

    df = pd.DataFrame({'x': x, 'y': y})


    layout = go.Layout(title=label, xaxis=dict(title=label_x),
                    yaxis=dict(title=label_y), )

    data = [
        go.Bar(
            x=df['x'],
            y=df['y']
        ),
        layout
    ]

    graphJSON = json.dumps(data, cls=py.utils.PlotlyJSONEncoder)

    return graphJSON