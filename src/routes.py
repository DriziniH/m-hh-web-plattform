import os
from os.path import join, dirname, realpath
import traceback
import json
from flask import render_template, url_for, flash, redirect, request, Flask, render_template_string, session, send_file, send_from_directory, session, Response
import boto3
from src.forms import LoginForm
from src.index import app, analytics_col, dm_col, dp_col
from src.utility import graph_tools, dict_tools, dp_fetcher
from src.utility.logger import logger
from flask_login import current_user, logout_user, login_required, login_user
from boto3.session import Session as BotoSession
import plotly as py
from werkzeug.utils import secure_filename
import uuid


@app.route("/")
@app.route("/home/")
def home():
    if "sts" not in session:
        return redirect(url_for('login'))

    return render_template('home.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == "json"


@app.route("/add-data-product/", methods=["GET", "POST"])
def add_dp():
    """
    Redirects to login page if user is not logged in
    Receives and validates a json file with the data product config 
    Json file is loaded and validated against data mesh specifications of the data product
    Configuration gets inserted to MongoDB if successfull
    """

    if "sts" not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':

        if 'file' not in request.files:
            flash_message('Request contains no file')
            return redirect(request.url)

        file = request.files['file']

        checked, message = check_file(file)
        if not checked:
            flash_message(message)
            return redirect(request.url)

        try:
            dp_config = json.load(file)
        except:
            flash_message("Invalid json document. Please try again.")
            return redirect(request.url)

        validated, message = validate_dp_config(dp_config)
        if not validated:
            flash_message(f"Error parsing document. {message}")
            return redirect(request.url)

        inserted = insert_config(dp_config)
        if not inserted:
            flash_message(f"Error adding data product.")
            return redirect(request.url)

        flash_message(
            f"Sucessfully added data product {dp_config['label']}!")

        return redirect(url_for('dps'))

    return render_template('add-dataproduct.html')

def check_file(file):
    if not file.filename:
        return False, 'No selected file'
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        return True
    else:
        return False, "File extension not allowed, please provide a json document"

def validate_dp_config(dp_config):
    """ Fetches dp specification config and all dps
    Checks if requested dps label is unique
    Recursivly validates the requested dp with the specification config

    Args:
        dp_config (dict): Data product config to be validated

    Returns:
        Tuple (Boolean, String): If validation succeeded and message
    """

    def resolve_subfield(dp_config, field, key):
        if field["mandatory"] is True:
            if "fields" in field:
                return resolve_subfields(dp_config, field["fields"], key)
            else:
                if key not in dp_config:
                    return False, f"Field {key} missing in config"
                else:
                    return True, ""
        else:
            return True, ""

    def resolve_subfields(dp_config, fields, key):
        for field in fields:
            if not key:
                new_key = field["field"]
            else:
                new_key = key + "."+field["field"]
            field_resolved, message = resolve_subfield(
                dp_config, field, new_key)
            if not field_resolved:
                return False, message
        return True, ""

    dp_specification = fetch_dp_specification()
    if not dp_specification:
        return False, "Data product specification could not be retrieved"
    dp_config_flatten = dict_tools.flatten_json(dp_config)

    existing_dps = list(dp_col.find({}))
    if check_label_existing(existing_dps, dp_config_flatten["label"]):
        return False, "Label is already existing."

    return resolve_subfields(dp_config_flatten, dp_specification, "")

def fetch_dp_specification():
    try:
        dm_col.find_one({}).get("specifications", "").get(
        "dataProductDescription", "").get("fields", "")
    except Exception as e:
        logger.error(f'Error fetching data product specification: {str(e)}')


def check_label_existing(dps, label):
    for dp in dps:
        if label == dp["label"]:
            return True
    return False


def insert_config(dp_config):
    dp_config["_id"] = str(uuid.uuid4())
    result = dp_col.insert_one(dp_config)
    return result.acknowledged


@app.route("/dashboard/")
def dashboard(methods=['GET']):
    
    if "sts" not in session:
        return redirect(url_for('login'))

    graphs = list(analytics_col.find({}, {'_id': False}))

    # Add images based on chart type
    for graph in graphs:
        graph.update({"img": chart_type.get(
            graph.get("data", "").get("type", ""), "")})

    plot = None
    analysis_type = request.args.get('analysis_type')
    if analysis_type:
        doc = analytics_col.find_one(
            {"_analysisType": analysis_type}, {'_id': False})
        # drop keys to make dict json graph parseable
        doc.pop("_analysisType")
        doc["data"] = [doc["data"]]

        plot = json.dumps(doc, cls=py.utils.PlotlyJSONEncoder)

    return render_template('dashboard.html', graphs=graphs, plot=plot)


chart_type = {
    "bar": "../static/img/bar-chart.png",
    "scatter": "../static/img/scatter-chart.png",
    "pie": "../static/img/pie-chart.png",
    "line": "../static/img/line-chart.png",
    "scattergeo": "../static/img/map.png",
    "log": "../static/img/log.png"
}


@app.route("/data-mesh/")
def dm(methods=['GET']):
    """Reads dm config and renders template with information
    """

    if "sts" not in session:
        return redirect(url_for('login'))

    dm = dm_col.find_one({}, {'_id': False})

    return render_template("datamesh.html", dm=dm)


@app.route("/data-products/")
def dps(dp_id=None, methods=['GET']):
    """ Reads data products and renders html template with dp information

    Params:
        dpid(String): DP id if dp is clicked by user

    Returns:
        data-products.html: Displays a sidebar with all dps and their config in json
    """

    if "sts" not in session:
        return redirect(url_for('login'))

    dps = list(dp_col.find({}))
    graphs = list(analytics_col.find({}))

    # get requested region or first
    dp_id = dp_id if dp_id else dps[0]["_id"]
    dp = None
    dp_files = []
    for dp in dps:
        if dp["_id"] == dp_id:
            dp_files = dp_fetcher.fetch_dl_files_formatted(dp["region"])
            break

    return render_template("dataproducts.html", dps=dps, dp=dp, dp_files=dp_files, dp_json=json.dumps(dp["interfaces"], indent=4))


@app.route('/download/<path:location>', methods=['GET', 'POST'])
def download_from_s3(location):
    download_link = dp_fetcher.create_download_link(location)
    return redirect(download_link)


@ app.route("/login/", methods=['GET', 'POST'])
def login():
    if "sts" in session:
        flash_message("Already logged in!")
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        if form.aws_access_key_id.data == "admin":  # TODO remove
            flash("Successfully logged in.")
            session["sts"] = True
            return redirect(url_for('home'))
        try:
            sess = BotoSession(aws_access_key_id=form.aws_access_key_id.data,
                               aws_secret_access_key=form.aws_secret_access_key.data, aws_session_token=None)
            sts = sess.client('sts')
            sts.get_caller_identity()
            session["sts"] = True

            return redirect(url_for('home'))
        except Exception as e:
            flash("Credentials are NOT valid.")
            print(e)

    return render_template('login.html', title='Login', form=form)


@app.route("/logout/")
def logout():
    session.pop("sts")
    flash_message("You have been successfully logged out!")
    return redirect(url_for('login'))


def flash_message(message):
    session.pop('_flashes', None)
    flash(message)
