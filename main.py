from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import qrcode
from PIL import Image
import tempfile
from email.mime.image import MIMEImage
import os

# Configuración básica de la aplicación Flask
app = Flask(__name__)
app.secret_key = 'clave_secreta'  # Clave secreta para la gestión de sesiones en Flask

# Configuración del formulario utilizando Flask-WTF
class EmailForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar código QR ')

# Ruta principal para mostrar el formulario
@app.route('/', methods=['GET', 'POST'])
def index():
    form = EmailForm()
    qr_code_path = None
    qr_data = None
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data

        # Generar código QR y obtener la ruta del archivo y los datos
        qr_code_path, qr_data = generate_qr(f'Nombre: {name}\nEmail: {email}')

        # Enviar correo electrónico con el código QR adjunto
        send_email(name, email, qr_code_path, qr_data)

        flash('Correo enviado', 'success')
        return redirect(url_for('index'))
    return render_template('index.html', form=form, qr_code_path=qr_code_path, qr_data=qr_data)


# Función para enviar el correo electrónico
# Función para enviar el correo electrónico con el código QR adjunto
def send_email(name, email, qr_file_path, qr_data):
    # Configurar el servidor SMTP
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Puerto SMTP (puedes cambiarlo según tu servidor)
    smtp_username = 'blaskocuenta@gmail.com'
    smtp_password = 'duns zraz qptx rkds'

    # Crear el objeto mensaje
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = email
    msg['Subject'] = 'Prueba de correo electrónico con código QR'

    # Cuerpo del mensaje
    message = f'Hola {name},\n\n Código QR adjunto.'
    msg.attach(MIMEText(message, 'plain'))

    # Adjuntar el código QR al correo electrónico
    with open(qr_file_path, 'rb') as qr_file:
        qr_image = MIMEImage(qr_file.read(), name=os.path.basename(qr_file_path))
    msg.attach(qr_image)

    # Iniciar conexión SMTP y enviar el correo
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f'Error al enviar el correo: {e}')


# Función para generar el código QR
# Función para generar el código QR y devolver la ruta del archivo y los datos
def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white")

    temp_img = tempfile.NamedTemporaryFile(delete=False)
    qr_img.save(temp_img.name)

    return temp_img.name, data


if __name__ == '__main__':
    app.run(debug=True)
