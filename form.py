from flask_wtf import FlaskForm
from wtforms import validators
from wtforms.fields.core import SelectField, StringField
from wtforms.fields.simple import PasswordField, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.widgets.core import TextArea


class FormLogin(FlaskForm):
    usuario = StringField('Nombre de usuario', validators=[validators.required(), validators.length(max=100)]) 
    contrasena = PasswordField('Contraseña', validators=[validators.required(), validators.length(max=50)])
    iniciar_sesion = SubmitField('Iniciar Sesión')


class FormRegistro(FlaskForm):
    nombre = StringField('Nombre', validators=[validators.required(), validators.length(max=100)]) 
    usuario = StringField('Nombre de usuario', validators=[validators.required(), validators.length(max=150)]) 
    correo = EmailField('Correo Electrónico', validators=[validators.required(), validators.length(max=150)])
    contrasena = PasswordField('Contraseña', validators=[validators.required(), validators.length(max=50)])
    enviar = SubmitField('Registrarme')

class FormEditarPerfil(FlaskForm):
    nombre = StringField('Nombre', validators=[validators.required(), validators.length(max=100)]) 
    correo = EmailField('Correo Electrónico', validators=[validators.required(), validators.length(max=150)])
    contrasena = PasswordField('Contraseña', validators=[validators.required(), validators.length(max=50), validators.EqualTo('confirmarcontrasena',message="Las contraseñas deben coincidir")])
    confirmarcontrasena = PasswordField('Confirmar Contraseña', validators=[validators.required(), validators.length(max=50)])
    enviar = SubmitField('Guardar')

class FormEditarUsuarioAdmin(FlaskForm):
    nombre = StringField('Nombre', validators=[validators.required(), validators.length(max=100)]) 
    correo = EmailField('Correo Electrónico', validators=[validators.required(), validators.length(max=150)])
    enviar = SubmitField('Guardar')

class FormEditarUsuarioSuperAdmin(FlaskForm):
    nombre = StringField('Nombre', validators=[validators.required(), validators.length(max=100)]) 
    correo = EmailField('Correo Electrónico', validators=[validators.required(), validators.length(max=150)])
    rol = SelectField('Rol', choices=[('Super Administrador', 'Super Administrador'), ('Administrador', 'Administrador'), ('cliente', 'Cliente')], validators=[validators.length(max=100)]) 
    enviar = SubmitField('Guardar')
class FormPlatos(FlaskForm):
    nombre = StringField('Plato', validators=[validators.required(), validators.length(max=100)]) 
    descripcion = StringField('Descripción', widget=TextArea(), validators=[validators.required(), validators.length(max=150)])
    calificacion = StringField('Calificacion')
    precio = StringField('Precio', validators=[validators.required()])
    enviar = SubmitField('Agregar plato')
    editar = SubmitField('Guardar cambios')

class FormPedido(FlaskForm):
    finalizarpedido = SubmitField('Finalizar Pedido')
