import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

import os 

smtp_server = 'smtp.gmail.com'  # Cambia esto al servidor SMTP que estés utilizando
smtp_port = 587  # Cambia esto al puerto adecuado
sender_email = 'alelplm17@gmail.com'
#sender_password = open('token.txt').read().strip()
sender_password = 'wwsu nuzq wwjp zhnm'

# Detalles del correo electrónico
receiver_email = 'p.m.alejandro.2015@gmail.com' # 'p.m.alejandro.2015@gmail.com'  'alejandro.pariona2@unmsm.edu.pe' 'alepharim@gmail.com'
subject = 'Re-envio Reporte Reactiva por regiones'
body = 'Adjunto lo solicitado y los archivos py, ipynb y excel'

# Crear el objeto MIMEMultipart
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))


# Adjuntar archivo
file_paths = ['Problema1.ipynb', 'Problema2.ipynb', 'procesamiento.py', 't5_inversion_AMAZONAS.xlsx']  # Cambia la ruta al archivo que quieras adjuntar
for file_path in file_paths:
    with open(file_path, 'rb') as file:
        attachment = MIMEApplication(file.read(), _subtype="csv")
        attachment.add_header('Content-Disposition', 'attachment', filename=file_path)
        msg.attach(attachment)
    
# Iniciar la conexión con el servidor SMTP
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()  # Iniciar el modo seguro
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())

print('Correo enviado exitosamente')