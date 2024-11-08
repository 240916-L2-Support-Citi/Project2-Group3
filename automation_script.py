from flask import Flask, jsonify
#from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time, random#, string, logging
import requests
import psycopg 
# imports ripped from p2 specs - a lot of them are useless for this script
# API endpoints
EC2_DNS = '' #TODO put in the ec2dns here
url = f'http://{EC2_DNS}:5000'
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
        conn = psycopg.connect("dbname=api_logs user=PLACEHOLDER") #TODO put in the database name and user here
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
        status_code = response.status_code
        if status_code == 200:
            temp = response.json()
            token = temp.get('token')
            db_logger('INFO', status_code, f"Success: Token obtained: {token}")
            return [token, temp, status_code]
        else:
            db_logger('ERROR', status_code, f"Failed to obtain token. Status code: {status_code}")
            return [None, None, status_code]
    except Exception as e:
        db_logger('ERROR', status_code, f"Failed to obtain token: {e}")
    

# item creation
def createCall():
    creationHeader={ # we can store this is a variable somewhere or pass it as a function parameter
    'User-ID': userID,
    'token': token
    }
    try:
        response = requests.post(url + createUrl, headers=creationHeader,json={'test':'THIS IS A BODY FOR USER REQUEST SIZE'}) # returns {"status": "item created", "item_id": item_id}
        status_code = response.status_code
        if status_code == 201:
            temp = response.json()
            temp_item_id = temp.get('item_id')
            db_logger('INFO', status_code, f"Item created successfully: {temp_item_id}")
            return [temp_item_id, temp, status_code]
        else:
            db_logger('ERROR', status_code, f"Failed to create item. Status code: {status_code}")
            return [None, None, status_code]
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
        status_code = response.status_code
        #print(response)
        if status_code == 200:
            temp = response.json()
            status_return = temp.get('status', 'Unknown status')
            db_logger('INFO', status_code, f"Item deleted successfully: {temp_item_id}")
            return [status_return, temp, status_code]
        else:
            db_logger('ERROR', status_code, f"Failed to delete item. Status code: {status_code}")
            return ["failed", None, status_code]
    except Exception as e:
        db_logger('ERROR', status_code, f"Failed to delete item {temp_item_id}: {e}")

# Print the response - debug
# print(response.json())
# print(response.status_code)

if __name__ == "__main__":
    while True:
        sleepTime = 5
        ranErr = random.randint(0, 5) #0 = create error, 1 = delete error, 2=both error, else ok
        print("Start cycle")
        #obtain token - no errors possible
        tokenRet = tokenCall()
        token = tokenRet[0] # set for create
        
        # create item; error possible
        if ranErr == 0:
            token=""
            print("Simulating only Create Error")
        elif ranErr == 2:
            token=""
            print("Simulating Create and Delete Error")
        createRet = createCall()
        temp_item_id = createRet[0]# set for delete

        #delete item; error possible
        if ranErr == 0:
            print("Delete Skipped")
            continue
        elif ranErr == 1 or ranErr == 2:
            temp_item_id = None
            print("Simulating Delete Error")
        deleteRet = deleteCall()

        print(f"Sleep for {sleepTime}")
        time.sleep(sleepTime)
