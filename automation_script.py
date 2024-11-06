from flask import Flask, request, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time, random, string
# imports ripped from p2 specs - a lot of them are useless for this script
# API endpoints
url = ""
metricsUrl="/metrics"
createUrl = "/api/items"
deleteUrl = "/api/items/{0}"#needs to be formatted
tokenUrl="'/api/token'"

#other stuff to track
userID="PLACEHOLDER"
token=""
temp_item_id=0 #maybe have a list of item ids???

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
    response = request.get(url + tokenUrl, headers=userHeader)
    temp=response.json()
    token=temp.get('token')

# item creation
def createCall():
    creationHeader={ # we can store this is a variable somewhere or pass it as a function parameter
    'User-ID': userID,
    'token': token
    }
    response = request.get(url + createUrl, headers=creationHeader) # returns {"status": "item created", "item_id": item_id}
    temp=response.json()
    #extract item_id
    temp=response.json()
    temp_item_id=temp.get('item_id')

def deleteCall():
    deletionHeader={ # we can store this is a variable somewhere or pass it as a function parameter
    'User-ID': userID,
    'token': token
    }
    # process item id
    tempDeleteUrl = deleteUrl.format(temp_item_id)
    #actually make the api call
    response = request.get(url + tempDeleteUrl, headers=deletionHeader)
    # we don't need to store anything from it other than the response itself

# Print the response - debug
# print(response.json())
# print(response.status_code)