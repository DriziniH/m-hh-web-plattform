from flask import Flask
from pymongo import MongoClient


app = Flask(__name__)

# session data is encryptedly safed on the server -> secret key
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'




mongo_connection = 'mongodb+srv://Hendrik:m-hh-mongo@eu-m-hh.fxa4u.mongodb.net/M-HH-analysis'
mongo_client = MongoClient(mongo_connection)
mongo_db = mongo_client["M-HH-analysis"]
regional_col = mongo_db["usa_analysis"]

print("Successfully connected to MongoDB")


from src import routes