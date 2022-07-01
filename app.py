from flask import Flask, render_template, request, jsonify
from bson.objectid import ObjectId
from flask_cors import CORS
from healthcheck import HealthCheck, EnvironmentDump
from company import company_bp
from stock import stock_bp
from flasgger import Swagger, LazyString, LazyJSONEncoder,swag_from


from pymongo import MongoClient
import yaml
import logging




app = Flask(__name__)
app.register_blueprint(company_bp,url_prefix="/api/v1.0/market/company")
app.register_blueprint(stock_bp,url_prefix="/api/v1.0/market/stock")
with open(r'database.yaml') as file:
    config = yaml.load(file,Loader=yaml.FullLoader)
client = MongoClient(config['uri'])
# db = client.lin_flask
db = client['knf-dev']

logging.basicConfig(filename = 'python-flask-app.log', level=logging.DEBUG, format ='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')


CORS(app)

@swag_from("hello.yml")
@app.route('/')
def index():
    return "Hello World!!!"

@app.route('/users', methods=['POST', 'GET'])
def data():
    
    # POST a data to database
    if request.method == 'POST':
        body = request.json
        firstName = body['firstName']
        lastName = body['lastName']
        emailId = body['emailId'] 
        # db.users.insert_one({
        db['users'].insert_one({
            "firstName": firstName,
            "lastName": lastName,
            "emailId":emailId
        })
        return jsonify({
            'status': 'Data is posted to MongoDB!',
            'firstName': firstName,
            'lastName': lastName,
            'emailId':emailId
        })
    
    # GET all data from database
    if request.method == 'GET':
        allData = db['users'].find()
        dataJson = []
        for data in allData:
            id = data['_id']
            firstName = data['firstName']
            lastName = data['lastName']
            emailId = data['emailId']
            dataDict = {
                'id': str(id),
                'firstName': firstName,
                'lastName': lastName,
                'emailId': emailId
            }
            dataJson.append(dataDict)
        print(dataJson)
        return jsonify(dataJson)

@app.route('/users/<string:id>', methods=['GET', 'DELETE', 'PUT'])
def onedata(id):

    # GET a specific data by id
    if request.method == 'GET':
        data = db['users'].find_one({'_id': ObjectId(id)})
        id = data['_id']
        firstName = data['firstName']
        lastName = data['lastName']
        emailId = data['emailId']
        dataDict = {
            'id': str(id),
            'firstName': firstName,
            'lastName': lastName,
            'emailId':emailId
        }
        print(dataDict)
        return jsonify(dataDict)
        
    # DELETE a data
    if request.method == 'DELETE':
        db['users'].delete_many({'_id': ObjectId(id)})
        print('\n # Deletion successful # \n')
        return jsonify({'status': 'Data id: ' + id + ' is deleted!'})

    # UPDATE a data by id
    if request.method == 'PUT':
        body = request.json
        firstName = body['firstName']
        lastName = body['lastName']
        emailId = body['emailId']

        db['users'].update_one(
            {'_id': ObjectId(id)},
            {
                "$set": {
                    "firstName":firstName,
                    "lastName":lastName,
                    "emailId": emailId
                }
            }
        )

        print('\n # Update successful # \n')
        return jsonify({'status': 'Data id: ' + id + ' is updated!'})

health = HealthCheck()
envdump = EnvironmentDump()


# add your own check function to the healthcheck
"""
def redis_available():
    client = _redis_client()
    info = client.info()
    return True, "redis ok"

health.add_check(redis_available)
"""

# add your own data to the environment dump
def application_data():
    return {"maintainer": "Saravanan",
            "git_repo": "py-healthcheck"}

envdump.add_section("application", application_data)
app.json_encoder = LazyJSONEncoder

swagger_template = dict(
info = {
    'title': LazyString(lambda: 'My first Swagger UI document'),
    'version': LazyString(lambda: '0.1'),
    'description': LazyString(lambda: 'This document depicts a      sample Swagger UI document and implements Hello World functionality after executing GET.'),
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'hello',
            "route": '/hello.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger/"
}

swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)



 # Add a flask route to expose information
app.add_url_rule("/healthcheck", "healthcheck", view_func=lambda: health.run())
app.add_url_rule("/environment", "environment", view_func=lambda: envdump.run())
if __name__ == "__main__":
    app.run(debug=True)