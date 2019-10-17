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


def send_email(receiver_email, message, subject):
    success = True
    port = 465  # For SSL
    sender_email = "mail@jaaga.in"
    password = "mail@jaaga"
    dev_email = "labs@jaaga.in"
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg.set_content(message)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        if success:
            msg['To'] = receiver_email
            server.send_message(msg)
        else:
            msg['To'] = receiver_email + ',' + dev_email
            server.send_message(msg)


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

        graphqlClient.execute(user_insert_mutation, {
            'objects': list(users)})

    except:
        return {"message": "Failed to create the user"}, 400

    subject = "Invitation to join open innovation platform"

    message = "Go to this link https://oip-dev.dev.jaagalabs.com/auth/forgot?email="+invitee_email

    send_email(invitee_email, message, subject)

    return {"message": "success"}, 201


@app.route("/user_approved", methods=['POST'])
def send_approval_confirmation():
    req = request.json
    receiver_email = req["email"]
    message = "You have been approved to join open innovation platform.Login at https://oip-dev.dev.jaagalabs.com/auth/login"
    subject = "User Approved"

    try:

        send_email(receiver_email, message, subject)
    except:
        return {"message": "could not send mail"}, 400

    return {"message": "Email successfully sent"}, 200


if __name__ == "__main__":

    serve(app, listen='*:{}'.format(str(PORT)))
