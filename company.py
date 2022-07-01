from flask import Flask, render_template, request, jsonify,Blueprint
from bson.objectid import ObjectId
from flask_cors import CORS
import yaml
from flasgger import Swagger, LazyString, LazyJSONEncoder,swag_from
from datetime import datetime

from flask import current_app
from pymongo import MongoClient
import yaml



company_bp=Blueprint('company',__name__)
with open(r'database.yaml') as file:
    config = yaml.load(file,Loader=yaml.FullLoader)
client = MongoClient(config['uri'])
# db = client.lin_flask
db = client['hackerrank']

@swag_from("company.yml", methods=['POST'])
@company_bp.route('/register', methods=['POST'])
def post_company():
    # POST a data to database
        body = request.json
        current_app.logger.info('req:{}',body)
        companyCode = body['companyCode']
        companyName = body['companyName']
        companyCEO=body['companyCEO']
        fromDate = body['fromDate'] + " 00:00:00"
        print("fromDate--->",fromDate)
        toDate = body['toDate']+" 23:59:59"
        print("toDate--->",toDate)
        status="1"
        companyTurnover=body['companyTurnover']
        companyWebSite=body['companyWebSite']
        # db.users.insert_one({
        
        data = db['company'].find_one({'companyCode': companyCode})
        
        if data is None:
                print("Inserting.......")
                db['company'].insert_one({
                    "companyCode": companyCode,
                    "companyName": companyName,
                    "companyCEO":companyCEO,
                    "companyTurnover":companyTurnover,
                    "companyWebSite":companyWebSite,
                    "fromDate":datetime.strptime(fromDate, '%d/%m/%Y %H:%M:%S'), 
                    "toDate":datetime.strptime(toDate, '%d/%m/%Y %H:%M:%S'),
                    "status":status
            })
        else:
            print("Existing data.......")
            companyCode = data['companyCode']
            companyName = data['companyName']
            companyCEO=data['companyCEO']
            companyWebSite=data['companyWebSite']
            companyTurnover=data['companyTurnover']
            fromDate = data['fromDate'].strftime("%m/%d/%Y, %H:%M:%S")
            toDate=data['toDate'].strftime("%m/%d/%Y, %H:%M:%S")
            status=data['status']
        return jsonify({
            'result': 'Data is posted to MongoDB!',
            "companyCode": companyCode,
            "companyName": companyName,
            "fromDate":fromDate,
            "toDate":toDate,
            "status":status
        })
        
        
@company_bp.route('/info/<string:companycode>', methods=['GET'])
def get_company_by_company_code(companycode):
   data = db['company'].find_one({'companyCode': companycode})
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
@company_bp.route('/getall', methods=['GET'])
def get_all_company_data():
        allData = db['company'].find()
        dataJson = []
        for data in allData:
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
            dataJson.append(dataDict)
        print(dataJson)
        return jsonify(dataJson)

@company_bp.route('/disable/<string:companycode>', methods=['GET'])    
def disable_company(companycode):
       data = db['company'].find_one({'companyCode': companycode})
       print(data)
       id = data['_id']
       companyCode = data['companyCode']
       db['company'].update_one(
            {'_id': ObjectId(id)},
            {
                "$set": {
                    "status":0
                }
            }
        )
       dataDict = {
                'id': str(id),
                'companyCode': companyCode,
                'result':"Company disabled"
            }
       print(dataDict)
       return jsonify(dataDict)

@company_bp.route('/delete/<string:companycode>', methods=['DELETE'])    
def delete_company(companycode):
    db['company'].delete_many({'companyCode': companycode})
    print('\n # Deletion successful # \n')
    return jsonify({'status': 'Data Company: ' + companycode + ' is deleted!'})