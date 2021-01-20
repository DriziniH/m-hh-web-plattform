import os
from os.path import join, dirname, realpath
import traceback

from flask import render_template, url_for, flash, redirect, request, Flask, render_template_string, session, send_file, send_from_directory

from src.forms import LoginForm
from src.index import app, regional_col, units_col
from src.plots import create_json_graph


@app.route("/")
@app.route("/home/")
def home():
    return render_template('home.html')


@app.route("/browser/")
def browser():
    return render_template('browser.html')


def get_graph_params(json_graph):
    """Reads params from json graph

    Args:
        json_graph (dict): graph information

    Returns:
        params
    """

    x = json_graph.get("x", [])
    y = json_graph.get("y", [])
    chart_type = json_graph.get("type", "bar")
    layout = json_graph.get("layout", {})

    return  x, y, chart_type, layout

    # TODO Parse validity?


chart_type = {
    "bar": "../static/img/bar-chart.png",
    "scatter": "../static/img/scatter-chart.png",
    "pie": "../static/img/pie-chart.png",
    "line": "../static/img/line-chart.png",
    "scattergeo" : "../static/img/map.png"
}


@app.route("/analytics/")
def analytics():
    plots = {}

    doc_cursor = regional_col.find({})

    for doc in doc_cursor:
        unit = units_col.find_one({"_id": doc["_unit"]})

        if not unit:
            break

        if doc["_unit"] not in plots:
            plots[doc["_unit"]] = {
                "unit_id": doc["_unit"],
                "unit_label": unit["label"]
            }

        graph_params = get_graph_params(doc["jsonGraph"])
        
        graph = {"title": graph_params[3]["title"],
                 "img": chart_type[doc["jsonGraph"]["type"]],
                 "type" : doc.get("_type", ""),
                 "jsonGraph":  create_json_graph(*graph_params)}

        if "graphs" in plots[doc["_unit"]]:
            plots[doc["_unit"]]["graphs"].append(graph)
        else:
            plots[doc["_unit"]]["graphs"] = [graph]

    #call requested region of first
    unit_id = request.args.get("region") if "region" in request.args else next(iter(plots.values()))["unit_id"]

    plot = None
    if "type" in request.args:
        for graph in plots.get(unit_id, "")["graphs"]:
            if graph["type"] == request.args.get("type"):
                plot = graph["jsonGraph"]

                print(f'Plot: {plot}')

    return render_template('analytics.html', plots=plots, unit_id=unit_id, plot = plot)


@ app.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # TODO Login logik
        return redirect(next_page or url_for('home'))
    return render_template('login.html', title='Login', form=form)
