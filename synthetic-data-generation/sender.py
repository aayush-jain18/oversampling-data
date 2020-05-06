import os
import smtplib
import sys
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mimetypes import guess_type

from tars.core import Connection


def get_email(email):
    if "<" in email:
        data = email.split("<")
        email = data[1].split(">")[0].strip()
    return email.strip()


class Email(object):
    def __init__(
        self,
        from_,
        recipients,
        subject,
        message,
        message_type="plain",
        attachments=None,
        cc=None,
        message_encoding="us-ascii",
    ):
        self.email = MIMEMultipart()
        self.email["From"] = from_
        self.email["To"] = ", ".join(recipients)
        self.email["Subject"] = subject
        if cc is not None:
            self.email["Cc"] = cc
        text = MIMEText(message, message_type, message_encoding)
        self.email.attach(text)
        if attachments is not None:
            for filename in attachments:
                mimetype, encoding = guess_type(filename)
                mimetype = mimetype.split("/", 1)
                fp = open(filename, "rb")
                attachment = MIMEBase(mimetype[0], mimetype[1])
                attachment.set_payload(fp.read())
                fp.close()
                encode_base64(attachment)
                attachment.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=os.path.basename(filename),
                )
                self.email.attach(attachment)

    def __str__(self):
        return self.email.as_string()


class EmailConnection(Connection):
    _connect_function = smtplib.SMTP
    _CONNECTION_STRING = "{host}:{port}"

    def __init__(self, context: str, params, via="url", **kwargs):
        super().__init__(context, params, via, **kwargs)

    @property
    def connection(self):
        self._connection = self._connect_function(
            self._CONNECTION_STRING.format(**self._conn_data, **self._conn_kwargs)
        )
        self._connection.ehlo()
        self._connection.starttls()
        self._connection.ehlo()
        self._connection.login(
            self._conn_data.get("username"), self._conn_data.get("password")
        )
        return self._connection

    def send(self, message, from_=None, to=None):
        if type(message) == str:
            if from_ is None or to is None:
                raise ValueError("You need to specify `from_` and `to`")
            else:
                from_ = get_email(from_)
                to = get_email(to)
        else:
            from_ = message.email["From"]
            if "Cc" not in message.email:
                message.email["Cc"] = ""
            to_emails = [message.email["To"]] + message.email["Cc"].split(",")
            to = [get_email(complete_email) for complete_email in to_emails]
            message = str(message)
        return self.connection.sendmail(from_, to, message)

    def close(self):
        self.connection.close()


if __name__ == "__main__":
    from allspark import constants
    from allspark.core.core import ParameterSetBuilder

    name = input(" - Your name: ")
    to_email = constants.NOTIFICATION_TO
    subject = "Sending mail with Python"
    message = "Hi,\n\nHere is your email.\n\nRegards,\nAayush Jain"
    attachments = [sys.argv[0]]
    params = ParameterSetBuilder(*constants.DriverProperties)
    params.setup()
    print("Connecting to server...")
    server = EmailConnection("GMAIL", params, "")
    print("Preparing the email...")
    email = Email(
        from_=params["GMAIL"].get("username"),  # you can pass only email
        recipients=to_email,
        subject=subject,
        message=message,
        attachments=attachments,
    )
    print("Sending...")
    server.send(email)
    print("Disconnecting...")
    server.close()
    print("Done!")
