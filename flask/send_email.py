import smtplib
from email.mime.text import MIMEText

def send(to, subject, body):
    msg = MIMEText(body)
    me = "wellmonitor@larsendt.com"

    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = to

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('localhost')
    s.sendmail(me, to, msg.as_string())
    s.quit()

if __name__ == "__main__":
    send("3037253982@txt.att.net", "Well Monitor Test", "This is a test...")
