import psycopg2
import pymysql
import boto3
import uuid
from flask import jsonify

from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import NoCredentialsError 

class DatabaseManager:
    def __init__(self):
        self.databases = [
            {'type': 'postgresql', 'connection_str': 'dbname=chatbot_db user=postgres password=david1234 host=localhost port=5432'}, 
        ]

    def connect(self, db_type):
        db = next((db for db in self.databases if db['type'] == db_type), None)
        if db is None:
            print(f"No database of type {db_type} found")
            return None

        if db_type == 'postgresql':
            print('postgresql')
            return psycopg2.connect(db['connection_str'])
            
    def disconnect(self, db_type, conn):
        print('disconnect')
        if db_type == 'postgresql' or db_type == 'mysql' or db_type == 'mssql':
            conn.close()
        else:
            pass

    def consulta_productos(self, db_type, conn):
        if db_type == 'postgresql' or db_type == 'mysql':
            cur = conn.cursor()
            query = "SELECT nombre_producto, cantidad_producto, descrip_producto, precio_producto FROM productos"
            cur.execute(query)
            resultados = cur.fetchall()
            cur.close()
            if resultados:
                return resultados
            else:
                print(f"No se encontraron productos en {db_type}.")
                return None
    
    def consulta_productos_con_promociones(self, db_type, conn):
        if db_type == 'postgresql' or db_type == 'mysql':
            cur = conn.cursor()
            query = """
            SELECT 
                p.Nombre_Producto,
                p.Descrip_Producto,
                prm.Porcen_Descuent,
                prm.Fecha_Ini,
                prm.Fecha_Fin
            FROM 
                Productos p
            JOIN 
                Promocion_Producto pp ON p.Id_Producto = pp.Id_Producto
            JOIN 
                Promociones prm ON pp.Id_Prom = prm.Id_Prom
            WHERE
                prm.estado_Promocion = TRUE;
            """
            cur.execute(query)
            resultados = cur.fetchall()
            cur.close()
            if resultados:
                return resultados
            else:
                print(f"No se encontraron productos con promociones activas en {db_type}.")
                return None

    def consulta_productos_con_descuentos(self, db_type, conn):
        if db_type == 'postgresql':
            cur = conn.cursor()
            query = """
            SELECT 
                p.Nombre_Producto,
                prm.Porcen_Descuent,
                ROUND(p.Precio_Producto, 2) AS Precio_Original,
                ROUND((p.Precio_Producto - (p.Precio_Producto * (prm.Porcen_Descuent / 100))), 2) AS Precio_Con_Descuento,
                prm.Fecha_Fin
            FROM 
                Productos p
            JOIN 
                Promocion_Producto pp ON p.Id_Producto = pp.Id_Producto
            JOIN 
                Promociones prm ON pp.Id_Prom = prm.Id_Prom
            WHERE
                prm.estado_promocion = TRUE
            """
            cur.execute(query)
            resultados = cur.fetchall()
            cur.close()
            return resultados


    def consulta_promociones_descuentos(self, db_type, conn,nombre):
        if db_type == 'postgresql':
            cur = conn.cursor()
            query = """
                SELECT nomprom, descrip_prom, TO_CHAR(fecha_fin, 'FMDay FMDD "de" FMMonth YYYY') AS fecha_formateada
                FROM public.promociones
                WHERE estado_promocion = 'True' AND nomprom = %s
            """
            cur.execute(query, (nombre,))
            resultados = cur.fetchall()
            # Formatear
            res = 'Promociones y descuentos\n'
            for promocion in resultados:  
                fecha_formateada = promocion[2].replace('Monday', 'Lunes') \
                                             .replace('Tuesday', 'Martes') \
                                             .replace('Wednesday', 'Miércoles') \
                                             .replace('Thursday', 'Jueves') \
                                             .replace('Friday', 'Viernes') \
                                             .replace('Saturday', 'Sábado') \
                                             .replace('Sunday', 'Domingo') \
                                             .replace('January', 'Enero') \
                                             .replace('February', 'Febrero') \
                                             .replace('March', 'Marzo') \
                                             .replace('April', 'Abril') \
                                             .replace('May', 'Mayo') \
                                             .replace('June', 'Junio') \
                                             .replace('July', 'Julio') \
                                             .replace('August', 'Agosto') \
                                             .replace('September', 'Septiembre') \
                                             .replace('October', 'Octubre') \
                                             .replace('November', 'Noviembre') \
                                             .replace('December', 'Diciembre')  
                res += (
                    f"\n\n"
                    f"✨ *Promoción:* {promocion[0]}\n\n"
                    f"📝 *Descripción:* {promocion[1]}\n\n"
                    f"📅 *Válido Hasta:* {fecha_formateada}"
                )

            # Formatear las fechas en español
    
            cur.close()
            return res   
        
    def consulta_promo_desc_json(self, db_type, conn):
        if db_type == 'postgresql':
            cur = conn.cursor()
            query = """
            SELECT nomprom, descrip_prom, TO_CHAR(fecha_fin, 'FMDay FMDD "de" FMMonth YYYY') AS fecha_formateada
            FROM public.promociones
            """
            cur.execute(query)
            resultados = cur.fetchall()
            cur.close()
            return jsonify(resultados)
        
    def envio_masivos_numeros(self, db_type, conn):
        if db_type == 'postgresql':
            cur = conn.cursor()
            query = "SELECT telefono_cliente FROM clientes LIMIT 2"
            #query = "SELECT telefono_cliente FROM clientes"
            cur.execute(query)
            resultados = cur.fetchall()
            cur.close()
            return resultados
        
    def recordatorios_pagos(self, db_type, conn):
        if db_type == 'postgresql':
            cur= conn.cursor()
            query = "SELECT c.telefono_cliente, c.nombre_cliente, p.monto_pendientep, p.fecha_vencimientop FROM pagos_pendientes p JOIN clientes c ON p.cliente_cedula = c.cedula_cliente WHERE p.fecha_vencimientop BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '10 days'"
            cur.execute(query)
            resultados=cur.fetchall()
            cur.close()
            return resultados
    
    def obtener_numeros_pagos(self, db_type, conn):
        if db_type == 'postgresql':
            cur= conn.cursor()
            query = "SELECT c.telefono_cliente FROM pagos_pendientes p JOIN clientes c ON p.cliente_cedula = c.cedula_cliente WHERE p.fecha_vencimientop BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '10 days'"
            cur.execute(query)
            resultados=cur.fetchall()
            cur.close()
            return resultados


#NUEVAS CONSULTAS WEBHOOK#
    def disconnect(self, db_type, conn):
        print('disconnect')
        if db_type == 'postgresql' or db_type == 'mysql' or db_type == 'mssql':
            conn.close()
        else:
            pass

    def consulta_productos2(self, db_type, conn):
        if db_type == 'postgresql' or db_type == 'mysql':
            cur = conn.cursor()
            query = "SELECT nombre_producto, cantidad_producto, precio_producto FROM productos"
            cur.execute(query)
            
            resultados = cur.fetchall()
            productos=resultados
            #Formatear
            res='Lista de productos\n'
            for producto in resultados:
                res+=(f"\n\n"
                        f"✨ *Producto:* {producto[0]}\n"
                        f"📦 *Cantidad:* {producto[1]}\n"
                        f"💵 *Precio:* {producto[2]}")
            cur.close()
            if res:
                return res
            else:
                print(f"No se encontraron productos en {db_type}.")
                return None
    
    def consulta_productos_con_descuentos2(self, db_type, conn):
        if db_type == 'postgresql':
            cur = conn.cursor()
            query = """
            SELECT 
                p.Nombre_Producto,
                prm.Porcen_Descuent,
                ROUND(p.Precio_Producto, 2) AS Precio_Original,
                ROUND((p.Precio_Producto - (p.Precio_Producto * (prm.Porcen_Descuent / 100))), 2) AS Precio_Con_Descuento,
                TO_CHAR(prm.Fecha_Fin, 'FMDay FMDD "de" FMMonth YYYY') AS Fecha_Formateada
            FROM 
                Productos p
            JOIN 
                Promocion_Producto pp ON p.Id_Producto = pp.Id_Producto
            JOIN 
                Promociones prm ON pp.Id_Prom = prm.Id_Prom
            WHERE
                prm.estado_promocion = TRUE
            """
            cur.execute(query)
            resultados = cur.fetchall()

            # Formatear
            res = 'Lista de productos con descuento\n'
            for producto in resultados:
                fecha_formateada = producto[4].replace('Monday', 'Lunes') \
                                             .replace('Tuesday', 'Martes') \
                                             .replace('Wednesday', 'Miércoles') \
                                             .replace('Thursday', 'Jueves') \
                                             .replace('Friday', 'Viernes') \
                                             .replace('Saturday', 'Sábado') \
                                             .replace('Sunday', 'Domingo') \
                                             .replace('January', 'Enero') \
                                             .replace('February', 'Febrero') \
                                             .replace('March', 'Marzo') \
                                             .replace('April', 'Abril') \
                                             .replace('May', 'Mayo') \
                                             .replace('June', 'Junio') \
                                             .replace('July', 'Julio') \
                                             .replace('August', 'Agosto') \
                                             .replace('September', 'Septiembre') \
                                             .replace('October', 'Octubre') \
                                             .replace('November', 'Noviembre') \
                                             .replace('December', 'Diciembre')  
                res += (
                    f"\n\n"
                    f"✨ *Producto:* {producto[0]}\n"
                    f"🔖 *Descuento:* {producto[1]}%\n"
                    f"💵 *Precio Original:* {producto[2]}\n"
                    f"💲 *Precio con Descuento:* {producto[3]}\n"
                    f"📅 *Valido Hasta:* {fecha_formateada}"
                )

            cur.close()
            return res


    def consulta_promociones_descuentos2(self, db_type, conn):
        if db_type == 'postgresql':
            cur = conn.cursor()
            query = """
            SELECT nomprom, descrip_prom, TO_CHAR(fecha_fin, 'FMDay FMDD "de" FMMonth YYYY') AS fecha_formateada
            FROM public.promociones where estado_promocion='True'
            """
            cur.execute(query)
            resultados = cur.fetchall()
            # Formatear
            res = 'Lista de promociones y descuentos\n'
            for promocion in resultados:  
                fecha_formateada = promocion[2].replace('Monday', 'Lunes') \
                                             .replace('Tuesday', 'Martes') \
                                             .replace('Wednesday', 'Miércoles') \
                                             .replace('Thursday', 'Jueves') \
                                             .replace('Friday', 'Viernes') \
                                             .replace('Saturday', 'Sábado') \
                                             .replace('Sunday', 'Domingo') \
                                             .replace('January', 'Enero') \
                                             .replace('February', 'Febrero') \
                                             .replace('March', 'Marzo') \
                                             .replace('April', 'Abril') \
                                             .replace('May', 'Mayo') \
                                             .replace('June', 'Junio') \
                                             .replace('July', 'Julio') \
                                             .replace('August', 'Agosto') \
                                             .replace('September', 'Septiembre') \
                                             .replace('October', 'Octubre') \
                                             .replace('November', 'Noviembre') \
                                             .replace('December', 'Diciembre')  
                res += (
                    f"\n\n"
                    f"✨ *Promoción:* {promocion[0]}\n"
                    f"📝 *Descripción:* {promocion[1]}\n"
                    f"📅 *Válido Hasta:* {fecha_formateada}"
                )

            # Formatear las fechas en español
    
            cur.close()
            return res   

    def create_solicitud_compra2(self, db_type, conn, solicitud_id, status, fecha_at, number, name, description):
        if db_type == 'postgresql' or db_type == 'mysql':
            cur = conn.cursor()
            query = f"INSERT INTO public.solicitudes_compras(solicitud_id, status, fecha_at, numero, name, description) VALUES ('{solicitud_id}', '{status}', '{fecha_at}', '{number}', '{name}','{description}')"
            cur.execute(query)
            conn.commit()
            cur.close()
      

    def generate_siguiente_solicitud_id2(self, db_type, conn):
        last_ticket_id = ''
        if db_type == 'postgresql' or db_type == 'mysql':
            cur = conn.cursor()
            query = "SELECT solicitud_id FROM solicitudes_compras ORDER BY solicitud_id DESC LIMIT 1"
            cur.execute(query)
            result = cur.fetchone()
            last_ticket_id = result[0] if result else "SLC000"
            cur.close()
        # Extraer el número y generar el próximo ID incrementando el número
        last_number = int(last_ticket_id[3:])
        next_number = last_number + 1
        next_ticket_id = f"SLC{next_number:03d}"
        return  next_ticket_id       