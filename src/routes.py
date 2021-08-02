import os
from os.path import join, dirname, realpath
import traceback
import json
from flask import render_template, url_for, flash, redirect, request, Flask, render_template_string, session, send_file, send_from_directory, session, Response
import boto3
from src.forms import LoginForm
from src.index import app, bcrypt, analytics_col, dm_col, dp_col, users_col
from src.utility import dict_tools, dp_fetcher, graphql
from src.utility.logger import logger
from flask_login import current_user, logout_user, login_required, login_user
from boto3.session import Session as BotoSession
import plotly as py
from werkzeug.utils import secure_filename
import uuid
import plotly.graph_objects as go

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

    if "login" not in session:
        return redirect(url_for('login'))
    if session["login"] == "driver":
        return redirect(url_for('dashboard'))

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
        return True, ""
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
        return dm_col.find_one({}).get("specifications", "").get(
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

@app.route("/")
@app.route("/dashboard/")
def dashboard(methods=['GET']):

    if "login" not in session:
        return redirect(url_for('login'))

    if(session["login"] == "iam"):
        #fetch every call for real time data
        session["graphs"] = fetch_selected_iam_graphs_from_dp()
        session["graphs"].extend(fetch_graphs_iam())
    elif(session["login"] == "driver"):
        #fetch only once to reduce network traffic
        if "graphs" not in session:
            session["graphs"] = fetch_graphs_driver()

    return render_template('dashboard.html', graphs= session["graphs"], list=list, enumerate=enumerate)


def fetch_graphs_iam():
    docs = list(analytics_col.find({}, {'_id': False}))
    return create_graphs(docs, True)


def fetch_graphs_driver():
    """Fetches region graphs from mongodb with car vin, adds image based on graph type and formats graph object to plotly json

    Returns:
        graphs(list): List of graphs as plotly json strings
    """
    user = session["driver"]
    dp_conf = dp_col.find_one({"_id": user["dp"]})
    graphs = graphql.fetch_dp_charts_driver(dp_conf["interfaces"]["graphql"], user["_vin"])
    return create_graphs(graphs, False)

def fetch_selected_iam_graphs_from_dp():
    graphs = graphql.fetch_dp_charts("/eu")
    selected_graphs = []
    for graph in graphs:
        if graph.get("title","") == "Consumption per model" or graph.get("title","") == "Emission per model":
            selected_graphs.append(graph)
    return create_graphs(selected_graphs, False)
 
def create_graphs(graphs, plotlyJSONEncode):
    for graph in graphs:
            graph_type = graph.get("chartType", "")

            if "map" in graph_type:
                plot = json.loads(graph["graph"])
                fig = go.Figure(plot)
                graph["graph"] = json.dumps(fig, cls=py.utils.PlotlyJSONEncoder)
            elif "log" in graph_type:
                continue
            else:
                if plotlyJSONEncode:
                    graph["graph"] = json.dumps(graph["graph"], cls=py.utils.PlotlyJSONEncoder)
    return graphs

@ app.route("/data-mesh/")
def dm(methods=['GET']):
    """Reads dm config and renders template with information
    """
    if "login" not in session:
        return redirect(url_for('login'))
    if session["login"] == "driver":
        return redirect(url_for('dashboard'))

    dm = dm_col.find_one({}, {'_id': False})

    return render_template("datamesh.html", dm=dm)


@ app.route("/data-products/")
def dps(dp_id=None, methods=['GET']):
    """ Reads data products and renders html template with dp information

    Params:
        dpid(String): DP id if dp is clicked by user

    Returns:
        data-products.html: Displays a sidebar with all dps and their config in json
    """

    if "login" not in session:
        return redirect(url_for('login'))
    if session["login"] == "driver":
        return redirect(url_for('dashboard'))

    dps = list(dp_col.find({}))

    # get requested dp or first
    dp = dps[int(request.args.get('dp_index'))] if 'dp_index' in request.args else dps[0]

    graphs = graphql.fetch_dp_charts(dp["interfaces"]["graphql"])
    dp_files = dp_fetcher.fetch_dl_files_formatted(dp["region"])

    return render_template("dataproducts.html", dps=dps, dp=dp, graphs=graphs, dp_files=dp_files, dp_json=json.dumps(dp["interfaces"], indent=4), enumerate=enumerate)

@ app.route('/download/<path:location>', methods=['GET', 'POST'])
def download_from_s3(location):
    region = request.args.get("region")
    download_link = dp_fetcher.create_download_link(location, region)
    return redirect(download_link)


@ app.route("/login/", methods=['GET', 'POST'])
def login():
    if "login" in session:
        flash_message("Already logged in!")
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        if form.data["submit_iam"] and login_iam(form):
            return redirect(url_for('dashboard'))
        elif form.data["submit_driver"] and login_driver(form):
            return redirect(url_for('dashboard'))

    return render_template('login.html', form=form)


def login_iam(form):
    try:
        sess = BotoSession(aws_access_key_id=form.id_field.data,
                           aws_secret_access_key=form.password_field.data, aws_session_token=None)
        sts = sess.client('sts')
        sts.get_caller_identity()
        session["login"] = "iam"

        return True
    except Exception as e:
        flash("IAM Credentials are NOT valid.")
        print(e)
        return False


def login_driver(form):
    user = users_col.find_one({"_username": form.id_field.data})
    if not user:
        flash_message("Please enter a valid user.")
        return False
    if not bcrypt.check_password_hash(user["pwd"], form.password_field.data):
        flash_message("Incorrect password. Please try again.")
        return False

    session["login"] = "driver"
    session["driver"] = user
    return True


@ app.route("/logout/")
def logout():
    session.clear()
    flash_message("You have been successfully logged out!")
    return redirect(url_for('login'))


def flash_message(message):
    session.pop('_flashes', None)
    flash(message)
