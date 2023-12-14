import json
from flask import Flask, request

from services.mail import MailService
from services.ftp import FtpService

from http_status_code.common import format
from http_status_code.success import OK
from http_status_code.fail import BAD_REQUEST, INTERNAL_ERROR


app = Flask(__name__)


@app.route("/api/ftp/upload", methods=["POST"])
def upload():
    try:
        data = json.loads(request.data)
        filename = data.get("filename")
        filecontent = data.get("filecontent")
    except Exception as e:
        print(e)
        return BAD_REQUEST
    
    response = FtpService.upload(filename, filecontent)
    if not response:
        return INTERNAL_ERROR
    
    return format(OK, "File uploaded")

@app.route("/api/email/auth", methods=["POST"])
def auth():
    try:
        data = json.loads(request.data)
        sender = data.get("sender")
        password = data.get("password")
    except Exception as e:
        print(e)
        return BAD_REQUEST

    response = MailService.auth(sender, password)
    if not response:
        return INTERNAL_ERROR 

    return format(OK, "Authentication passed")


@app.route("/api/email", methods=["POST"])
def send_email():
    try:
        data = json.loads(request.data)
        sender = data.get("sender")
        receiver = data.get("receiver")
        subject = data.get("subject")
        content = f"{data.get("content")} \n\n {FtpService.link}"
    except:
        return BAD_REQUEST

    response = MailService.send_mail(sender, receiver, subject, content)
    if not response:
        return INTERNAL_ERROR

    return format(OK, "E-mail was sent")


if "__main__" == __name__:
    app.run(host="0.0.0.0", port=6969)
