import os
import functools
import yagmail as yagmail
import uuid

from werkzeug.utils import redirect
from flask import Flask, request, jsonify, url_for, g, session, flash
from flask.templating import render_template
from models import plato
from form import FormLogin, FormPedido, FormRegistro, FormPlatos, FormEditarPerfil, FormEditarUsuarioAdmin, FormEditarUsuarioSuperAdmin

from models import usuario, pedido
import db
app = Flask(__name__)

app.config['SECRET_KEY'] = "05c3df8ca33b704ab69a0fe9bae452909ebe3a7534558577e1b3a0a66356432d" #os.urandom(32)

#Decorador para verificar que el usuario es autenticado
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect( url_for('login') )

        return view(**kwargs)

    return wrapped_view

@app.before_request
def cargar_usuario_autenticado():
    nombre_usuario = session.get('nombre_usuario')
    if nombre_usuario is None:
        g.user = None
    else:
        g.user = usuario.cargar(nombre_usuario)


"""
    Método registro de nuevo usuario
"""
@app.route('/registro', methods=["GET","POST"])
def registro(): 
    if request.method == "GET":
        formulario = FormRegistro()
        return render_template('registro.html', form=formulario)
    else:
        formulario = FormRegistro(request.form)
        if formulario.validate_on_submit():
            obj_usuario = usuario(formulario.nombre.data, formulario.usuario.data,formulario.correo.data, formulario.contrasena.data, 'cliente') #verificar
            if obj_usuario.insertar():                
                return render_template('registro.html', mensaje="Se registró el usuario exitosamente.", form=FormRegistro())

        return render_template('registro.html', mensaje="Todos los datos son obligatorios.", form=formulario)


@app.route("/logout/")
@login_required
def logout():
    session.clear()
    return redirect( url_for('login') )


"""
    Método Inicio 
"""
@app.route('/inicio', methods = ["GET"])
@login_required
def inicio(): 
    if session.get('rol') == "Administrador" or session.get('rol') == "Super Administrador":
        return redirect( url_for('dashboard_admin'))
    else:
        return redirect( url_for('get_listado_platos'))


"""
    Método para login
"""
@app.route('/', methods = ["GET", "POST"])
def login(): 
    if request.method=="GET":
        formulario = FormLogin()
        return render_template('login.html', form=formulario)
    
    else:
        formulario = FormLogin(request.form)

        usr = formulario.usuario.data.replace("'","")
        pwd = formulario.contrasena.data.replace("'","")
                
        obj_usuario = usuario('',usr,'',pwd,'')
        if obj_usuario.autenticar():            
            r = usuario.cargar(usr)
            session.clear()
            session["rol"] = r.rol
            if r.rol == "Administrador" or r.rol == "Super Administrador":                
                session["nombre_usuario"] = usr
                return redirect( url_for('dashboard_admin'))
            else:
                session["nombre_usuario"] = usr
                lastId = pedido.last_user_id(r.usuario)
                if len(lastId) != 0:
                    if pedido.check_cart(lastId[0]["idpedido"]):
                        session["id_pedido"] = lastId[0]["idpedido"]
                    else:
                        session["id_pedido"] = uuid.uuid1()
                else:
                    session["id_pedido"] = uuid.uuid1()
                print("idpedido:",str(session.get("id_pedido")))
                return redirect( url_for('get_listado_platos'))
        
        return render_template('login.html', mensaje="Nombre de usuario o contraseña incorrecta.", 
        form=formulario)


"""
    Método para editar el perfil de usuario
"""
@app.route('/editar-perfil', methods=["GET","POST"])
@login_required
def editar_perfil():
    objeto_usuario = usuario.cargar(g.user.usuario)

    if request.method == "GET":    
        formulario= FormEditarPerfil()        
        return render_template('editar-perfil.html',form=formulario, item=objeto_usuario)

    else:
        
        formulario = FormEditarPerfil(request.form)
        if formulario.validate_on_submit():
            obj_user = usuario(formulario.nombre.data, objeto_usuario.usuario, objeto_usuario.correo,formulario.contrasena.data, objeto_usuario.rol)
            if obj_user.editar_perfil(obj_user.usuario):
                obj_usuario = usuario.cargar(obj_user.usuario)
                return render_template('editar-perfil.html', item=obj_usuario,mensaje = "Se han actualizado sus datos correctamente",form=formulario)    
        
        return render_template('editar-perfil.html', item=objeto_usuario, mensaje="Todos los datos son obligatorios.", form=formulario)


"""
    Método para listar los usuarios
"""
@app.route('/lista-usuarios', methods=["GET"])
@login_required
def usuarios(): 
    if session.get('rol') == "Administrador" or session.get('rol') =="Super Administrador":
        return render_template('usuarios.html', lista=usuario.listado())

    return redirect( url_for('logout') )

""" Método para eliminar usuario por id
"""

@app.route('/usuarios/listado/eliminar/<id>', methods=["GET","POST"])
@login_required
def eliminar_usuario(id):
    user=usuario.cargarid(id)
    if usuario.eliminar(id):
        pedido.eliminar_usuario_detallepedido(user.usuario)
        pedido.eliminar_usuario_pedidos(user.usuario)
        plato.delete_lista_deseos_usuario(user.usuario)
        return redirect(url_for('usuarios'))

"""
    Método para ver detalles de un usuario
"""
@app.route('/detalle-usuario/<id>', methods=["GET", "POST"])
@login_required
def detalle_usuario(id):
    objeto_usuario = usuario.cargarid(id)
    if request.method =="GET":
        if g.user.rol =="Super Administrador":
            formulario=FormEditarUsuarioSuperAdmin()
        elif g.user.rol =="Administrador":
            formulario=FormEditarUsuarioAdmin()
        return render_template('detalle-usuario.html', id_usuario=id, item=objeto_usuario, form=formulario)
    else:
        if g.user.rol =="Super Administrador":
            formulario=FormEditarUsuarioSuperAdmin(request.form)
        elif g.user.rol =="Administrador":
            formulario=FormEditarUsuarioAdmin(request.form)
        if formulario.validate_on_submit():
            obj_user=usuario("","","","","")
            if g.user.rol == "Super Administrador":
                obj_user = usuario(formulario.nombre.data, objeto_usuario.usuario, formulario.correo.data, objeto_usuario.contrasena, formulario.rol.data)
            elif g.user.rol == "Administrador":
                obj_user = usuario(formulario.nombre.data, objeto_usuario.usuario, formulario.correo.data, objeto_usuario.contrasena, objeto_usuario.rol)
            if obj_user.editar_usuario(obj_user.usuario):
                obj_usuario = usuario.cargar(obj_user.usuario)
                return render_template('detalle-usuario.html', id_usuario=id, item=obj_usuario,mensaje = "Se han actualizado los datos correctamente",form=formulario)
            else:
                return render_template('detalle-usuario.html', id_usuario=id, item=obj_user, mensaje="No fue posible realizar los cambios", form=formulario)
        else:
            return render_template('detalle-usuario.html', id_usuario=id, item=objeto_usuario, mensaje="Todos los campos son obligatorios", form=formulario)





"""*********************PLATOS*************************"""

"""
    Método para agregar platos
"""
@app.route('/agregar-plato', methods=["GET","POST"])
@login_required
def agregarplato(): 
    if g.user.rol == "Administrador" or g.user.rol == "Super Administrador":
        if request.method == "GET":
            formulario = FormPlatos()
            return render_template('agregar-plato.html', form=formulario)
        else:
            formulario = FormPlatos(request.form)
            if formulario.validate_on_submit():
                obj_plato = plato('', formulario.nombre.data, formulario.descripcion.data,formulario.precio.data, '', '', '') #verificar
                if obj_plato.insertar():                
                    # return render_template('agregar-plato.html', mensaje="Se agregó el plato exitosamente.", form=FormPlatos())
                    return render_template('lista-platos.html', mensaje="Se agregó el plato exitosamente.", lista=plato.listado())

            return render_template('agregar-plato.html', mensaje="Todos los datos son obligatorios.", form=formulario)
    
    return redirect( url_for('logout') )


"""
    Método para listar los platos
"""
@app.route('/platos/listado', methods=["GET"])
@login_required
def get_listado_platos():
        cart_elements = pedido.count_id_detalle(str(session.get("id_pedido")))
        deseos_elements = pedido.count_usuario_deseos(g.user.usuario)
        return render_template('lista-platos.html', lista=plato.listado(), cart=cart_elements[0]["COUNT(*)"], deseos=deseos_elements[0]["COUNT(*)"])

"""
    Método para eliminar platos
"""
@app.route('/platos/listado/eliminar/<id>', methods=["GET","POST"])
@login_required
def eliminar_plato(id):
    if plato.eliminar(id):    
        return render_template('lista-platos.html', lista=plato.listado(),mensaje = "Se ha eliminado el plato correctamente")
    
"""
    Método para editar un plato por ID 
"""
@app.route('/platos/editar/<id_plato>', methods=["GET", "POST"])
@login_required
def detail_plato(id_plato):
    objeto_plato = plato.cargarid(id_plato)

    if request.method == "GET":    
        formulario = FormPlatos()    
        return render_template('editar-plato.html',id=id_plato,form=formulario, item=objeto_plato)

    else:        
        formulario = FormPlatos(request.form)
        if formulario.validate_on_submit():
            objeto_plato = plato('', formulario.nombre.data, formulario.descripcion.data, formulario.precio.data, "", "", "")
            if objeto_plato.editar_plato(id_plato):
                obj_dish = plato.cargarid(id_plato)
                return render_template('editar-plato.html', id=id_plato, item=obj_dish,mensaje = "Se han actualizado los datos correctamente",form=formulario)    
        
        return render_template('editar-plato.html', id=id_plato, item=objeto_plato, mensaje="Todos los datos son obligatorios.", form=formulario)



"""
    Método para renderizar el dashboard 
"""
@app.route('/dashboard-admin', methods=["GET"])
@login_required
def dashboard_admin():
    if g.user.rol == "Administrador" or g.user.rol == "Super Administrador":
        clientes=usuario.count_sql()
        platos=plato.count_sql()

        return render_template('dashboard-admin.html', usuarios=clientes, menu=platos)
    
    return redirect( url_for('logout') )


"""****PEDIDOS****"""

"""
    Método crear pedidos
"""
@app.route('/platos/agregar/<id>/<idlocation>')
@app.route('/platos/agregar/<id>', methods=["GET","POST"])
@login_required
def agregar_pedido(id,idlocation=""):
    obj_plato = plato.cargarid(id)
    obj_pedido = pedido(0, g.user.usuario, 'S', str(session.get("id_pedido")), id, '1',obj_plato.precio)
    if request.referrer == url_for('finalizar_pedido',_external=True):
        plato.delete_lista_deseos(idlocation)
        print(idlocation)
    if obj_pedido.insertarpedido():
        return redirect(request.referrer)
        #return render_template('lista-platos.html', lista=plato.listado(),mensaje = "Se ha agregado el plato correctamente")

"""
    Método para listar todos los pedidos
"""
@app.route('/lista-pedidos', methods=["GET"])
@login_required
def list_pedidos():
    if g.user.rol == "Administrador" or g.user.rol == "Super Administrador":
        return render_template('lista-pedidos.html',content= pedido.listado())

    return redirect( url_for('logout') )


"""
    Método para ver los detalles de de un pedido seleccionado
"""
@app.route('/lista-pedidos/detalle/<id>', methods=["GET"])
def detail_pedido(id):
       
    obj_pedido = pedido.cargarid(id)
    idp = obj_pedido.idpedido
    finalizar_pedido= pedido.listado_id_detalle(idp)
    listaplatos=[]
    valor_pedido = obj_pedido.precio
    for item in finalizar_pedido:
        dish = plato.cargarid(item["idplato"])
        listaplatos.append(dish)
    
    return render_template('detalles-pedido.html',lista = listaplatos, usu=obj_pedido, idpedido=id, valor =valor_pedido)


@app.route('/pedidos/listado/eliminar/<id>', methods=["GET","POST"])
@login_required
def eliminar_pedido(id):
    if pedido.eliminar(id):
        return render_template('lista-pedidos.html', content=pedido.listado(),mensaje = "Se ha eliminado el pedido correctamente")


@app.route('/finalizar-pedido', methods=["GET", "POST"])
@login_required
def finalizar_pedido():
    idpedido = str(session.get("id_pedido"))
    finalizar_pedido= pedido.listado_id_detalle(idpedido)
    listaplatos=[]
    valor_pedido = 0
    for item in finalizar_pedido:
        dish = plato.cargarid(item["idplato"])
        valor_pedido = int(dish.precio) + valor_pedido
        dish.id=item["id"]
        listaplatos.append(dish)
    listado_deseos= pedido.listado_usuario_deseos(g.user.usuario)
    lista_deseos=[]
    i=0
    for item in listado_deseos:
        dish = plato.cargarid(item["idplato"])
        dish.idlocation=item["id"]
        lista_deseos.append(dish)
    formulario = FormPedido()
    if request.method == "GET":
        return render_template('finalizar-pedido.html', lista = listaplatos, form=formulario, valor=valor_pedido, listadeseos=lista_deseos)
    else:
        if pedido.finalizarpedido(g.user.usuario, idpedido, valor_pedido):
            session["id_pedido"] = uuid.uuid1()
            return redirect(request.referrer)
        return redirect(request.referrer)


@app.route('/pedidos/descartar-plato/<id>', methods=["GET","POST"])
@login_required
def eliminar_plato_pedido(id):
    idpedido = str(session.get("id_pedido"))
    if pedido.descartar_plato(idpedido, id):
        return redirect( url_for('finalizar_pedido'))







"""*************************LISTA DESEOS*******************"""


""" Métdodo para ver lista de deseos
"""
@app.route('/agregar-deseos/<id>', methods=["GET","POST"])
@login_required
def lista_deseos(id):
    obj_plato = plato.cargarid(id)
    if obj_plato.insertar_lista_deseos(g.user.usuario):    
        return redirect(url_for('get_listado_platos'))

if __name__ == "__main__":
    app.run(debug = True)