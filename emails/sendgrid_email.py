# emails/sendgrid_email.py
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64

def send_email(subject, content, to_email, attachments=None):
    message = Mail(
        from_email=settings.SENDGRID_FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        plain_text_content=content,
    )

    if attachments:
        for attachment in attachments:
            # attachment should be dict with keys: content (bytes), filename, type (MIME type), disposition
            encoded_file = base64.b64encode(attachment['content']).decode()
            att = Attachment(
                FileContent(encoded_file),
                FileName(attachment['filename']),
                FileType(attachment['type']),
                Disposition(attachment.get('disposition', 'attachment')),
            )
            message.add_attachment(att)

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        return {
            "status": "success",
            "code": response.status_code,
            "body": response.body.decode() if response.body else ""
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

