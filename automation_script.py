#from flask import Flask, requests, jsonify
import requests
from datetime import datetime
import json
import os
import time
#from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time, random, string
# imports ripped from p2 specs - a lot of them are useless for this script
# API endpoints
EC2_DNS = ''
url = f'http://{EC2_DNS}:5000'
metricsUrl="/metrics"
createUrl = "/api/items"
deleteUrl = "/api/items/{0}"#needs to be formatted
tokenUrl="/api/token"

#other stuff to track
userID="guest"
token="PLACEHOLDER"
temp_item_id=0 # have a list during actual automation

#print(url)

'''
TODO
    1.Obtain a Token: Use /api/token endpoint to obtain a token.
    2.Create and Delete Items: Automate item creation and deletion, using authentication.
    3.Handle Errors and Monitor Counts: Log errors and track request status codes (Can be to a local log OR a PSQL database!)
'''
# obtain a token
def tokenCall():
    userHeader = { # we can store this is a variable somewhere or pass it as a function parameter
    'User-ID': userID
    }
    print(url + tokenUrl)
    response = requests.post(url + tokenUrl, headers=userHeader)
    temp=response.json()
    token=temp.get('token')
    return [token, temp, response.status_code]

# item creation
def createCall():
    creationHeader={ # we can store this is a variable somewhere or pass it as a function parameter
    'User-ID': userID,
    'Token': token
    }
    response = requests.post(url + createUrl, headers=creationHeader) # returns {"status": "item created", "item_id": item_id}
    temp=response.json()
    temp_item_id=temp.get('item_id') # get item_id for future delete call

    return [temp_item_id, temp, response.status_code]

def deleteCall():
    deletionHeader={ # we can store this is a variable somewhere or pass it as a function parameter
    'User-ID': userID,
    'token': token
    }
    # process item id
    tempDeleteUrl = deleteUrl.format(temp_item_id)
    #actually make the api call
    response = requests.delete(url + tempDeleteUrl, headers=deletionHeader)
    # we don't need to store anything from it other than the response itself
    temp=response.json()
    code_return = -1
    status_return="failed function"
    print("entire delete response:",temp)
    if 'status' in temp:
        status_return=temp.get('status')
    elif 'error' in temp:
        status_return=temp.get('error')
    return [status_return,temp, response.status_code]

def log(inp, code, call):
    print("\nStart Log Test:\n",inp)
    for x in inp:
        print(x)
    print("Code:", code,"\n")
    # easiest solution: write to a json file
    dict = {}
    curr_time = datetime.now()
    form_curr_time = curr_time.strftime("%d/%b/%Y %H:%M:%S")
    dict['call'] = call
    dict['code'] = code
    if call != "token":
        dict['status'] = inp.get('status')
    else:
        dict['token'] = inp.get('token')
    if call == "create":
        dict["item_id"] = inp.get('item_id')
    if inp.get('error') != None:
        dict['error'] = inp.get('error')
    file_name = 'test.json'
    print("create file", code)
    if not os.path.exists(file_name):
    # Create if not exists
        default_data = {
            "25/Dec/1999 00:00:00": "TEST DATA"
        }
        with open(file_name, 'w') as json_file:
            json.dump(default_data, json_file)
    with open(file_name, 'r') as f:# open file in read
        #print("test",f)
        data = json.load(f)
    data.update({form_curr_time:dict})
    with open(file_name, 'w+') as f2:
        json.dump(data, f2,indent=4)


tokenRet = tokenCall()
token = tokenRet[0]
createRet = createCall()
temp_item_id = createRet[0]
deleteRet = deleteCall() # we don't really need to store anything for delete
log(tokenRet[1],tokenRet[2],"token")
time.sleep(1) # without this python kinda dies and doesn't do all the writes in time
log(createRet[1],createRet[2],"create")
time.sleep(1)
log(deleteRet[1],deleteRet[2],"delete")