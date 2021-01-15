import os
from os.path import join, dirname, realpath
import traceback

from flask import render_template, url_for, flash, redirect, request, Flask, render_template_string, session, send_file, send_from_directory

from src.forms import LoginForm
from src.index import app, regional_col
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
    
    title = json_graph.get("title", "")
    x = json_graph.get("x", [])
    y = json_graph.get("y", [])
    label_x = json_graph.get("labelX", "")
    label_y = json_graph.get("labelY", "")
    chart_type = json_graph.get("chart_type", "bar")
    layout = json_graph.get("layout", {})

    return title, x, y, label_x, label_y, chart_type, layout

    # TODO Parse validity?


@app.route("/analytics/")
def analytics():
    doc_cursor = regional_col.find({})
    curr_analysis = {}
    plots = []

    for doc in doc_cursor:
        plots.append(create_json_graph(*get_graph_params(doc["jsonGraph"])))

    return render_template('analytics.html', plot=plots[2])


@app.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # TODO Login logik
        return redirect(next_page or url_for('home'))
    return render_template('login.html', title='Login', form=form)
