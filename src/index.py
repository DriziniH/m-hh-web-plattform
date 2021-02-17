from flask import Flask
from pymongo import MongoClient
from src.conf import properties_mongo as pm
from flask_session import Session

app = Flask(__name__)

# session data is encryptedly safed on the server -> secret key
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SESSION_TYPE'] = 'filesystem'

app.config.from_object(__name__)
Session(app)

mongo_connection = pm.db_con_usa
mongo_client = MongoClient(mongo_connection)
mongo_db = mongo_client["M-HH"]
analytics_col = mongo_db["analysis"]
units_col = mongo_db["units"]
schemas_col = mongo_db["schemas"]

print("Successfully connected to MongoDB")


from src import routes