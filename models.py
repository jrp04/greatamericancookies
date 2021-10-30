import db

from werkzeug.security import generate_password_hash, check_password_hash

#Clase para manejar los usuarios
class usuario():
    nombre=''
    usuario=''
    correo=''
    contrasena=''
    rol=''

    def __init__(self, pnombre, pusuario, pcorreo, pcontrasena,prol):
        self.nombre = pnombre
        self.usuario = pusuario
        self.correo = pcorreo
        self.contrasena = pcontrasena
        self.rol = prol
    
    #Classmethod para crear instancias de usuario desde la bd.
    @classmethod
    def cargar(cls, p_usuario):
        sql = "SELECT usuario, nombre, correo, rol FROM usuarios WHERE usuario = ?;" 
        obj = db.ejecutar_select(sql, [p_usuario])
        if obj:
            if len(obj)>0:
                return cls(obj[0]["nombre"], obj[0]["usuario"], obj[0]["correo"], '******', obj[0]["rol"])

        return None

    @classmethod
    def cargarid(cls, p_id):
        sql = "SELECT usuario, nombre, correo, rol FROM usuarios WHERE id = ?;" 
        obj = db.ejecutar_select(sql, [p_id])
        if obj:
            if len(obj)>0:
                return cls(obj[0]["nombre"], obj[0]["usuario"], obj[0]["correo"], '******', obj[0]["rol"])

        return None
        
    #Metodo para insertar el usuario en la base de datos
    def insertar(self):
        sql = "INSERT INTO usuarios (usuario, nombre, correo, contrasena, rol) VALUES (?, ?, ?, ?, ?);"
        
        #generate_password_hash crea un hash seguro para almacenar la contraseña del usuario en la bd 
        hashed_pwd = generate_password_hash(self.contrasena, method='pbkdf2:sha256', salt_length=32)
        afectadas = db.ejecutar_insert(sql, [self.usuario, self.nombre, self.correo, hashed_pwd, self.rol]) 
        return (afectadas>0)

    #Metodo para verificar el usuario contra la base de datos
    def autenticar(self):
        sql = "SELECT * FROM usuarios WHERE usuario = ?;"
        obj = db.ejecutar_select(sql, [ self.usuario ])
        if obj:
            if len(obj) >0:
                #Agregamos la invocación al metodo check_password_hash
                #para verificar el password digitado contra el hash seguro almacenado en bd.
                if check_password_hash(obj[0]["contrasena"], self.contrasena):
                    return True
        
        return False

    @staticmethod
    def listado():
        sql = "SELECT * FROM usuarios ORDER BY id;"
        return db.ejecutar_select(sql, None)    

    def editar_perfil(self,p_usuario):
        sql = "UPDATE usuarios SET nombre=(?), contrasena=(?), rol=(?) WHERE usuario = ?;"
        hashed_pwd = generate_password_hash(self.contrasena, method='pbkdf2:sha256', salt_length=32)
        afectadas = db.ejecutar_insert(sql, [self.nombre, hashed_pwd, self.rol, p_usuario]) 
        return (afectadas>0)

    def editar_usuario(self,p_usuario):
        sql = "UPDATE usuarios SET nombre=(?), correo=(?), rol=(?) WHERE usuario = ?;"
        afectadas = db.ejecutar_insert(sql, [self.nombre, self.correo, self.rol, p_usuario]) 
        return (afectadas>0)
    
    def eliminar(p_id):
        sql = "DELETE FROM usuarios WHERE id = ?;"
        afectadas = db.ejecutar_insert(sql, [p_id]) 
        return (afectadas>0)

    @staticmethod
    def count_sql():
        sql = "SELECT COUNT(*) FROM usuarios WHERE rol = 'cliente';"
        return db.ejecutar_select(sql, [])[0]["COUNT(*)"]


class plato():
    nombre=''
    descripcion=''
    precio=''
    calificacion=''
    id=''
    disponible=''
    idlocation=''

    def __init__(self, pid, pnombre, pdescripcion,pprecio,pcalificacion,pdisponible, pidlocation):
        self.id=pid
        self.nombre = pnombre
        self.descripcion = pdescripcion
        self.precio = pprecio
        self.calificacion = pcalificacion
        self.disponible=pdisponible
        self.idlocation=pidlocation

    @classmethod
    def cargarid(cls, p_id):
        sql = "SELECT nombre, descripcion, precio, disponible FROM platos WHERE id = ?;" 
        obj = db.ejecutar_select(sql, [p_id])
        if obj:
            if len(obj)>0:
                return cls(p_id ,obj[0]["nombre"], obj[0]["descripcion"], obj[0]["precio"],"",obj[0]["disponible"], "")

        return None
        
    #Metodo para insertar el plato en la base de datos
    def insertar(self):
        sql = "INSERT INTO platos (nombre, descripcion, precio) VALUES (?, ?, ?);"
        
        afectadas = db.ejecutar_insert(sql, [self.nombre, self.descripcion, self.precio]) 
        return (afectadas>0)

    @staticmethod
    def listado():
        sql = "SELECT * FROM platos ORDER BY id;"
        return db.ejecutar_select(sql, None)

    def eliminar(p_id):
        sql = "UPDATE platos SET disponible='N' WHERE id = ?;"
        afectadas = db.ejecutar_insert(sql, [p_id]) 
        return (afectadas>0)

    def editar_plato(self,p_id):
        sql = "UPDATE platos SET nombre=(?), descripcion=(?), precio=(?) WHERE id = ?;"
        afectadas = db.ejecutar_insert(sql, [self.nombre, self.descripcion, self.precio, p_id]) 
        return (afectadas>0)

    def insertar_lista_deseos(self,usuario):
        sql = "INSERT INTO listadeseos (usuario, idplato) VALUES (?, ?);"
        
        afectadas = db.ejecutar_insert(sql, [usuario, self.id]) 
        return (afectadas>0)
    
    @staticmethod
    def delete_lista_deseos(id):
        sql = "DELETE FROM listadeseos WHERE id = (?);"
        
        afectadas = db.ejecutar_insert(sql, [id]) 
        return (afectadas>0)

    @staticmethod
    def delete_lista_deseos_usuario(usuario):
        sql = "DELETE FROM listadeseos WHERE usuario = (?);"
        afectadas = db.ejecutar_insert(sql, [usuario]) 
        return (afectadas>0)

    @staticmethod
    def count_sql():
        sql = "SELECT COUNT(*) FROM platos;"
        return db.ejecutar_select(sql,[])[0]["COUNT(*)"]

class pedido():
    id=0
    usuario=''
    estado=''
    idpedido=''
    idplato=''
    cantidad=''
    precio=''
    
    def __init__(self, pid, pusuario,pestado, pidpedido, pidplato, pcantidad, pprecio):
        self.id = pid
        self.usuario = pusuario
        self.estado = pestado
        self.idpedido = pidpedido
        self.idplato = pidplato
        self.cantidad = pcantidad
        self.precio = pprecio

    @classmethod
    def cargarid(cls, p_id):
        sql = "SELECT id, usuario, estado, idpedido, totalpedido FROM pedidos WHERE id = ?;" 
        obj = db.ejecutar_select(sql, [p_id])
        if obj:
            if len(obj)>0:
                return cls(obj[0]["id"], obj[0]["usuario"], obj[0]["estado"], obj[0]["idpedido"], ""
                , "", obj[0]["totalpedido"])

        return None
        
    @staticmethod
    def finalizarpedido(usuario, idpedido, totalpedido):
        sql = "INSERT INTO pedidos (usuario, estado, idpedido, totalpedido) VALUES (?, ?, ?, ?);"
        
        afectadas = db.ejecutar_insert(sql, [usuario, 'S', idpedido, totalpedido]) 
        return (afectadas>0)

    #Metodo para insertar el plato en la tabla inicial de pedido
    def insertarpedido(self):
        sql = "INSERT INTO detallepedido (idpedido, idplato, cantidad, precio, usuario) VALUES (?, ?, ?, ?, ?);"
        
        afectadas = db.ejecutar_insert(sql, [self.idpedido, self.idplato, self.cantidad, self.precio, self.usuario]) 
        return (afectadas>0)
    
    @staticmethod
    def listado():
        sql = "SELECT * FROM pedidos ORDER BY id;"
        return db.ejecutar_select(sql, None)
    
    @staticmethod
    def listado_id_detalle(idpedido):
        sql = "SELECT * FROM detallepedido WHERE idpedido = ?;"
        return db.ejecutar_select(sql, [idpedido])

    @staticmethod
    def count_id_detalle(idpedido):
        sql = "SELECT COUNT(*) FROM detallepedido WHERE idpedido = ?;"
        return db.ejecutar_select(sql, [idpedido])
    
    def count_usuario_deseos(usuario):
        sql = "SELECT COUNT(*) FROM listadeseos WHERE usuario = ?;"
        return db.ejecutar_select(sql, [usuario])

    def listado_usuario_deseos(usuario):
        sql = "SELECT * FROM listadeseos WHERE usuario = ?;"
        return db.ejecutar_select(sql, [usuario])

    @staticmethod
    def last_user_id(usuario):
        sql = "SELECT * from detallepedido WHERE id = (select MAX(id) FROM detallepedido WHERE usuario = ?);"
        return db.ejecutar_select(sql, [usuario])

    def eliminar(p_id):
        sql = "DELETE FROM pedidos WHERE id = ?;"
        afectadas = db.ejecutar_insert(sql, [p_id]) 
        return (afectadas>0)

    def editar_plato(self,p_id):
        sql = "UPDATE platos SET nombre=(?), descripcion=(?), precio=(?), calificacion=(?) WHERE id = ?;"
        afectadas = db.ejecutar_insert(sql, [self.nombre, self.descripcion, self.precio, self.calificacion, p_id]) 
        return (afectadas>0)
    
    @staticmethod
    def check_cart(idpedido):
        sql = "SELECT COUNT(*) FROM pedidos WHERE idpedido = ?;"
        return db.ejecutar_select(sql, [idpedido])[0]["COUNT(*)"] == 0
    
    @staticmethod
    def descartar_plato(idpedido, id):
        sql = "DELETE FROM detallepedido WHERE (idpedido = ? AND id = ?);"
        afectadas = db.ejecutar_insert(sql, [idpedido, id]) 
        return (afectadas>0)

    @staticmethod
    def eliminar_usuario_detallepedido(usuario):
        sql = "DELETE FROM detallepedido WHERE usuario = (?);"
        afectadas = db.ejecutar_insert(sql, [usuario]) 
        return (afectadas>0)

    @staticmethod
    def eliminar_usuario_pedidos(usuario):
        sql = "DELETE FROM pedidos WHERE usuario = (?);"
        afectadas = db.ejecutar_insert(sql, [usuario]) 
        return (afectadas>0)