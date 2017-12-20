import smtplib

class SMTP(object):

    def __init__(self):
        self.__session = None

    def open(self, host, port=25, username=None, password=None):
        self.__session = smtplib.SMTP(host, port)
        if username is not None and password is not None:
            self.session.starttls()
            try:
                self.session.login(self.username, self.password)
            except Exception as e:
                raise

    def send(self, to, content, subject=False):
        if subject:
            headers = "\r\n".join(["from: " + self.username,
                "subject: " + subject,
                "to: " + to,
                "mime-version: 1.0",
                "content-type: text/html"])
            content = headers + "\r\n\r\n" + content
        self.__session.sendmail(self.__from, to, content)
