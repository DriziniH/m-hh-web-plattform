import os
from os.path import join, dirname, realpath
import traceback
import json
from flask import render_template, url_for, flash, redirect, request, Flask, render_template_string, session, send_file, send_from_directory

from src.forms import LoginForm
from src.index import app, regional_col, units_col, schemas_col
from src.utility import graph_tools


@app.route("/")
@app.route("/home/")
def home():
    return render_template('home.html')


@app.route("/browser/")
def browser():
    plots = {}

    units = list(units_col.find({}))

    # call requested region or first
    unit_id = request.args.get("region") if "region" in request.args else units[0]
    for unit in units:
        if unit["_id"] == unit_id:
            break

    img = None
    if "path" in request.args:
        img = "../static/img/glue-catalog.jpg"

    return render_template('browser.html', units=units, unit=unit, img=img)


chart_type = {
    "bar": "../static/img/bar-chart.png",
    "scatter": "../static/img/scatter-chart.png",
    "pie": "../static/img/pie-chart.png",
    "line": "../static/img/line-chart.png",
    "scattergeo": "../static/img/map.png"
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

        graph_params = graph_tools.get_graph_params(doc["jsonGraph"])

        graph = {"title": graph_params[3]["title"],
                 "img": chart_type[doc["jsonGraph"]["type"]],
                 "type": doc.get("_type", ""),
                 "jsonGraph":  graph_tools.create_json_graph(*graph_params)}

        if "graphs" in plots[doc["_unit"]]:
            plots[doc["_unit"]]["graphs"].append(graph)
        else:
            plots[doc["_unit"]]["graphs"] = [graph]

    # call requested region or first
    unit_id = request.args.get("region") if "region" in request.args else next(
        iter(plots.values()))["unit_id"]

    plot = None
    if "type" in request.args:
        for graph in plots.get(unit_id, "")["graphs"]:
            if graph["type"] == request.args.get("type"):
                plot = graph["jsonGraph"]

    return render_template('analytics.html', plots=plots, unit_id=unit_id, plot=plot)


@app.route("/regions/")
def regions():
    """ Reads units and renders template for regions

    Params:
        region(String): Unit id if region is clicked by user

    Returns:
        regions.html: Displays a sidebar with all regions and their config in json
    """
    units = list(units_col.find({}))

    # call requested region of first
    unit_id = request.args.get(
        "region") if "region" in request.args else units[0]["_id"]

    unit = units_col.find_one({"_id": unit_id})

    return render_template("regions.html", units=units, unit=unit, unit_json_pretty=json.dumps(unit, indent=4))


@app.route("/schemas/")
def schemas():
    """ Reads schemas and renders template

    Params:
        schema (String): Schema id if schema is clicked by user

    Returns:
        schemas.html: Displays a sidebar with all schemas and their fields
    """
    schemas = list(schemas_col.find({}))

    # call requested region of first
    schema_id = request.args.get(
        "schema") if "schema" in request.args else schemas[0]["_id"]

    schema = schemas_col.find_one({"_id": schema_id})

    return render_template("schemas.html", schemas=schemas, schema=schema, unit_json_pretty=json.dumps(schema, indent=4))


@ app.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # TODO Login logic
        return redirect(next_page or url_for('home'))
    return render_template('login.html', title='Login', form=form)
