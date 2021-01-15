from flask import Flask
from pymongo import MongoClient
from src.conf import properties_mongo as pm


app = Flask(__name__)

# session data is encryptedly safed on the server -> secret key
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'




mongo_connection = pm.db_con_usa
mongo_client = MongoClient(mongo_connection)
mongo_db = mongo_client["M-HH-USA"]
regional_col = mongo_db["analysis"]

print("Successfully connected to MongoDB")


from src import routes