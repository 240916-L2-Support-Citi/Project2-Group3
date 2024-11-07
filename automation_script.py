from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time, random, string, logging
import requests
import psycopg 
# imports ripped from p2 specs - a lot of them are useless for this script
# API endpoints
EC2_DNS = ''
url = f'http://{EC2_DNS}.compute-1.amazonaws.com:5000'
metricsUrl="/metrics"
createUrl = "/api/items"
deleteUrl = "/api/items/{0}"#needs to be formatted
tokenUrl="/api/token"

#other stuff to track
userID="guest"
token="PLACEHOLDER"
temp_item_id=0 #maybe have a list of item ids???

'''
TODO
    1.Obtain a Token: Use /api/token endpoint to obtain a token.
    2.Create and Delete Items: Automate item creation and deletion, using authentication.
    3.Handle Errors and Monitor Counts: Log errors and track request status codes (Can be to a local log OR a PSQL database!)
'''
# obtain a token
def db_logger(log_level, status_code, message):
    try:
        conn = psycopg.connect("dbname=api_logs user=")
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS api_logs (
                id SERIAL PRIMARY KEY,
                log_level VARCHAR(10),
                status_code INT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute(
            "INSERT INTO api_logs(log_level, status_code, message) VALUES(%s, %s, %s)",
            (log_level, status_code, message)
        )
        conn.commit()
    except Exception as e:
        print(f"Unsucessful log to database: {e}")

def tokenCall():
    userHeader = { # we can store this is a variable somewhere or pass it as a function parameter
        'User-ID': userID
    }
    try:
        response = requests.post(url + tokenUrl, headers=userHeader)
        temp=response.json()
        token=temp.get('token')
        status_code = response.status_code
        db_logger('INFO', status_code, f"Success: Token obtained: {token}")
        return [token, temp, response.status_code]
    except Exception as e:
        db_logger('ERROR', status_code, f"Failed to obtain token: {e}")
    

# item creation
def createCall():
    creationHeader={ # we can store this is a variable somewhere or pass it as a function parameter
    'User-ID': userID,
    'token': token
    }
    try:
        response = requests.post(url + createUrl, headers=creationHeader) # returns {"status": "item created", "item_id": item_id}
        temp=response.json()
        #extract item_id
        status_code = response.status_code
        temp_item_id=temp.get('item_id')
        print(temp)
        db_logger('INFO', status_code, f"Item created successfully: {temp_item_id}")
        return [temp_item_id, temp, response.status_code]
    except Exception as e:
        db_logger('ERROR', status_code, f"Failed to create item: {e}")

def deleteCall():
    deletionHeader={ # we can store this is a variable somewhere or pass it as a function parameter
    'User-ID': userID,
    'token': token
    }

    try:  
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
        #code_return = response.status_code
        #print("in delete",[status_return,code_return])
        status_code = response.status_code
        print(response)
        db_logger('INFO', status_code, f"Item deleted successfully: {temp_item_id}")
        return [status_return,temp, response.status_code]
    except Exception as e:
        db_logger('ERROR', status_code, f"Failed to delete item {temp_item_id}: {e}")

# Print the response - debug
# print(response.json())
# print(response.status_code)

tokenRet = tokenCall()
token = tokenRet[0]
createRet = createCall()
temp_item_id = createRet[0]
deleteRet = deleteCall()
