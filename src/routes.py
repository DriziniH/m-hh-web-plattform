import os
from os.path import join, dirname, realpath
import traceback

from flask import render_template, url_for, flash, redirect, request, Flask, render_template_string, session, send_file, send_from_directory

from src.forms import LoginForm
from src.index import app


@app.route("/")
@app.route("/home/")
def home():
    return render_template('home.html')


@app.route("/browser/")
def browser():
    return render_template('browser.html')


@app.route("/analytics/")
def analytics():
    return render_template('analytics.html')


@app.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit(): #TODO Login logik
        return redirect(next_page or url_for('home'))
    return render_template('login.html', title='Login', form=form)
