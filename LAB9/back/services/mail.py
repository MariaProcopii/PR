from smtplib import SMTP_SSL as SMTP


class MailService:

    # some_pass = "lqgx zckt wufj apcy"

    _port = 465
    _smtp_server = "smtp.gmail.com"

    _conn = None

    @staticmethod
    def auth(username, password):
        try:
            MailService._conn = SMTP(MailService._smtp_server)
            response = MailService._conn.login(username, password)
            if len(response) > 1 and b'Accepted' in response[1]:
                return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def send_mail(sender, receiver, subject, content):
        try:
            message = f"From: {sender}\nTo: {receiver}\nSubject: {subject}\n\n{content}"
            MailService._conn.sendmail(sender, receiver, message)
            return True
        except Exception as e:
            print(e)
            return False
