from flask import Flask, request, jsonify
import json
from waitress import serve
from datetime import timedelta
import os
import smtplib
import ssl
from email.message import EmailMessage


from flask_cors import CORS


app = Flask(__name__)
CORS(app)


PORT = 8080


@app.route("/")
def test():
    return "working"


@app.route("/invite_user", methods=['POST'])
def user_invite():
    req = request.json

    receiver_email = req["receiver_email"]
    subject = req["subject"]
    message = req["message"]

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
            msg['To'] = receiver_email
            server.send_message(msg)
        else:
            msg['To'] = receiver_email + ',' + dev_email
            server.send_message(msg)

    # return jsonify(result)

    return "work"


if __name__ == "__main__":
    # app.run(debug=True)
    serve(app, listen='*:{}'.format(str(PORT)))
