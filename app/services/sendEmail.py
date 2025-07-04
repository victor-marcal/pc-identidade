import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

server = 'smtp.gmail.com'
port = 587
sender_email = 'joaopedrovr91@gmail.com'
password = 'nmfi fekq qvob jgnv'

receiver_email = 'joaopedro.vieira@tecprime.com.br'
subject = 'Test Email'
body = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Teste</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f2f2f2;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f2f2f2;">
        <tr>
            <td align="center">
                <table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff;">
                    <tr>
                        <td align="center" style="padding: 40px 0;">
                            <img src="https://img.freepik.com/fotos-gratis/paisagem-de-nevoeiro-matinal-e-montanhas-com-baloes-de-ar-quente-ao-nascer-do-sol_335224-794.jpg" alt="Paisagem" width="400" style="display: block; margin: 0 auto;">
                            <p style="margin-top: 20px; text-align: center;">Olá,</p>
                            <p style="text-align: center;">Este é um e-mail de teste com uma imagem anexada.</p>
                            <p style="text-align: center;">Agradecemos por ter recebido este e-mail de teste.</p>
                            <p style="text-align: center;">Este e-mail foi enviado apenas para fins de demonstração e teste.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

message = MIMEMultipart()
message['From'] = sender_email
message['To'] = receiver_email
message['Subject'] = subject
message.attach(MIMEText(body, 'html'))

try:
    server = smtplib.SMTP(server, port)
    server.starttls()

    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
finally:
    server.quit()