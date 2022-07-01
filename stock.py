from flask import Flask, render_template, request, jsonify,Blueprint
from bson.objectid import ObjectId
from flask_cors import CORS
import yaml
from flasgger import Swagger, LazyString, LazyJSONEncoder,swag_from
from datetime import datetime
from gridfs import GridFS
from flask import current_app,make_response
from pymongo import MongoClient
import yaml
import json
from flask.json import jsonify


stock_bp=Blueprint('stock',__name__)
with open(r'database.yaml') as file:
    config = yaml.load(file,Loader=yaml.FullLoader)
client = MongoClient(config['uri'])
# db = client.lin_flask
db = client['hackerrank']
grid_fs = GridFS(db)



@stock_bp.route('/add/<string:companycode>', methods=['POST'])    
def add_stock(companycode):
       body = request.json
       stockName=body['stockName']
       stockPrice=body['stockPrice']
       db['company'].find_one_and_update(
            {'companyCode': companycode},
            {
                "$set": {
                   "stockExchange": body
                   }
            }
        )
       dataDict = {
                'companyCode': companycode,
                'result':"Stock Added"
            }
       print(dataDict)
       return jsonify(dataDict)


@stock_bp.route('/get/<string:companycode>/<string:startdate>/<string:enddate>', methods=['GET'])
def get_company_by_company_code(companycode,startdate,enddate):
   data = db['company'].find_one({'companyCode': companycode,})
   id = data['_id']
   companyCode = data['companyCode']
   companyName = data['companyName']
   fromDate = data['fromDate'].strftime("%m/%d/%Y, %H:%M:%S")
   toDate=data['toDate'].strftime("%m/%d/%Y, %H:%M:%S")
   dataDict = {
            'id': str(id),
            'companyCode': companyCode,
            'companyName': companyName,
            'fromDate':fromDate,
            'toDate':toDate
        }
   print(dataDict)
   return jsonify(dataDict)


@stock_bp.route('/upload/<file_name>', methods=['PUT'])
def upload(file_name):
    with grid_fs.new_file(filename=file_name) as fp:
        fp.write(request.data)
        file_id = fp._id

    if grid_fs.find_one(file_id) is not None:
        return json.dumps({'status': 'File saved successfully'}), 200
    else:
        return json.dumps({'status': 'Error occurred while saving file.'}), 500


@stock_bp.route('/download/<file_name>')
def index(file_name):
    grid_fs_file = grid_fs.find_one({'filename': file_name})
    response = make_response(grid_fs_file.read())
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers["Content-Disposition"] = "attachment; filename={}".format(file_name)
    return response
