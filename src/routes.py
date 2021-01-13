import os
from os.path import join, dirname, realpath
import traceback

from flask import render_template, url_for, flash, redirect, request, Flask, render_template_string, session, send_file, send_from_directory

from src.forms import LoginForm
from src.index import app, regional_col
from src.plots import create_plot


@app.route("/")
@app.route("/home/")
def home():
    return render_template('home.html')


@app.route("/browser/")
def browser():
    return render_template('browser.html')


@app.route("/analytics/")
def analytics():
    doc_cursor = regional_col.find({})
    curr_analysis = {}
    for document in doc_cursor:
        curr_analysis.update({document["_type"]: document["data"]})

    bar = create_plot(curr_analysis["models"], "Modelle fahrender Autos")
    print(bar)
    return render_template('analytics.html', plot=bar)


@app.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():  # TODO Login logik
        return redirect(next_page or url_for('home'))
    return render_template('login.html', title='Login', form=form)
