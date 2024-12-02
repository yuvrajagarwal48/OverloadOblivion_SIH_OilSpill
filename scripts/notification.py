import requests
import json
from google.oauth2 import service_account
import google.auth.transport.requests
from google.cloud import firestore

# Initialize Firestore
# service_account_file = './spill-sentinel-firebase-adminsdk-tdawx-9b03a5a598.json'
service_account_file='/home/yuvraj/Coding/sih_main/scripts/spill-sentinel-firebase-adminsdk-tdawx-9b03a5a598.json'
credentials = service_account.Credentials.from_service_account_file(
    service_account_file, scopes=['https://www.googleapis.com/auth/firebase.messaging','https://www.googleapis.com/auth/datastore']
)
firestore_client = firestore.Client(credentials=credentials)

def get_access_token():
    request = google.auth.transport.requests.Request()
    credentials.refresh(request)
    return credentials.token

def get_tokens_from_firestore():
    tokens = []
    users_ref = firestore_client.collection('users')  # Firestore collection name
    docs = users_ref.stream()

    for doc in docs:
        data = doc.to_dict()
        if 'token' in data:  # Ensure the token field exists
            tokens.append(data['token'])

    return tokens

def send_push_notification(tokens, title, body):
    url = 'https://fcm.googleapis.com/v1/projects/spill-sentinel/messages:send'
    headers = {
        'Authorization': 'Bearer ' + get_access_token(),
        'Content-Type': 'application/json; UTF-8'
    }

    message = {
        "message": {
            "notification": {
                "title": title,
                "body": body
            },
            "token": None,  # This will be set for each token individually
        }
    }

    for token in tokens:
        message["message"]["token"] = token  # Set the individual token
        response = requests.post(url, headers=headers, data=json.dumps(message))

        if response.status_code == 200:
            print(f'Notification sent to {token} successfully')
        else:
            print(f'Failed to send notification to {token}: {response.text}')

# # Fetch tokens from Firestore and send notifications
# tokens = get_tokens_from_firestore()
# if tokens:
#     send_push_notification(tokens, 'Hello', 'This is a test notification')
# else:
#     print('No tokens found in Firestore.')
