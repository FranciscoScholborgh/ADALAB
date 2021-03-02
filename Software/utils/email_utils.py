from django.core.mail import EmailMessage
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from .str_utils import generate_randomstr

#you can replace this with other method to send email
class EmailUtils():

    def login():
        pass

    def logout():
        pass

    def send_email(subject, message, recievers, attachments=None):
        send_to = [recievers] if not isinstance(recievers, list) else recievers
        email = EmailMessage(subject, message, to=send_to)
        if attachments is not None:
            for attachment in attachments:
                filename = attachment["filename"]
                to_attach = attachment["to_attach"]
                file_type = attachment["file_type"]
                email.attach(filename, to_attach.getvalue(), file_type)
                """obj = MIMEBase('application','octet-stream')
                filename = attachment["filename"]
                to_attach = attachment["to_attach"]
                obj.set_payload((to_attach).read())
                encoders.encode_base64(obj)
                obj.add_header('Content-Disposition',f"attachment; filename= {filename}")
                email.attach(obj) """ 
        email.send()