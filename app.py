from flask import Flask, request, jsonify
import json
from waitress import serve
from datetime import timedelta
import os
import smtplib
import ssl
from email.message import EmailMessage
from graphqlclient import GraphQLClient


from flask_cors import CORS


app = Flask(__name__)
CORS(app)


PORT = 8080


graphqlClient = GraphQLClient(os.environ['HASURA_GRAPHQL_URL'])
graphqlClient.inject_token(
    os.environ['HASURA_GRAPHQL_ADMIN_SECRET'], 'x-hasura-admin-secret')


user_insert_mutation = '''
mutation insert_users($objects: [users_insert_input!]! ) {
    insert_users(
        objects:$objects
    ) {
        returning {
            id
            
            
        }
    }
}
'''


@app.route("/")
def test():
    return "working"


@app.route("/invite_user", methods=['POST'])
def user_invite():
    users = []
    req = request.json
    invitee_email = req["email"]
    is_admin = req["is_admin"]
    user = {
        "email": invitee_email,
        "is_approved": True,
        "is_verified": True,
        "password": "password",
        "token": "token"
    }
    users.append(user)

    try:
        result = graphqlClient.execute(user_insert_mutation, {
            'objects': list(users)})

    except:
        return "not work"

    success = True
    result = {"status": "worked"}
    # req = request.json

    # receiver_email = req["receiver_email"]
    subject = "Invitation to join open innovation platform"

    message = "Go to this link https://app.socialalpha.jaagalabs.com/auth/forgot?email="+invitee_email

    port = 465  # For SSL
    sender_email = "mail@jaaga.in"
    password = "mail@jaaga"
    dev_email = "labs@jaaga.in"
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg.set_content(message)
    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        if success:
            msg['To'] = invitee_email
            server.send_message(msg)
        else:
            msg['To'] = invitee_email + ',' + dev_email
            server.send_message(msg)

    # return jsonify(result)

    return jsonify(result)


if __name__ == "__main__":
    # app.run(debug=True)
    serve(app, listen='*:{}'.format(str(PORT)))
