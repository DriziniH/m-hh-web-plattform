import plotly as py
import pandas as pd
import numpy as np
import json
import plotly.graph_objs as go
import plotly.express as px


# def create_plot(data=[], label="plot", label_x="x", label_y="y"):

#     x = []
#     y = []

#     for row in data:
#         y.append(row["numActiveCars"])
#         x.append(row["timestamp"])

#     df = pd.DataFrame({label_x: x, label_y: y})
#     df[label_x] = pd.to_datetime(df[label_x], unit='ms').tolist()

#     layout = go.Layout(title=label)

#     fig = px.line(df, x=label_x, y=label_y)

#     graphJSON = json.dumps(fig, cls=py.utils.PlotlyJSONEncoder)
#     #graphJSON = construct_json_graph(x, y, "timestamp", "cars", "scatter", {
#                                     #  "title": "Number of active cars"})
#     #print(graphJSON)
#     return graphJSON


def create_json_graph(title, x, y, label_x="x", label_y="y", chart_type="bar", layout={}):
    return json.dumps({
        "data": [{
            "title":title,
            "x": x,
            "xaxis": label_x,
            "y": y,
            "yaxis": label_y,
            "type": chart_type,
            "layout": layout
        }]
    })
