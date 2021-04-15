
from flask import Flask
from pymongo import MongoClient
from src.conf import properties_mongo as pm
from flask_session import Session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt

app = Flask(__name__)

# session data is encryptedly safed on the server -> secret key
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SESSION_TYPE'] = 'filesystem'

app.config.from_object(__name__)
Session(app)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"]
)
csrf = CSRFProtect(app)
bcrypt = Bcrypt(app)

mongo_connection = pm.db_con_usa
mongo_client = MongoClient(mongo_connection)
mongo_db = mongo_client["M-HH"]
analytics_col = mongo_db["analysis"]
dm_col = mongo_db["dm_config"]
dp_col = mongo_db["dp_config"]
users_col = mongo_db["users"]

print("Successfully connected to MongoDB")

from src import routes