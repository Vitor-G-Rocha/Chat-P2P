#XQDL CHAT BIBLIOTECAS
import pymysql.cursors  #Mysql

def center(toplevel):
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w/2 - size[0]/2
    y = h/2 - size[1]/2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

def quit(root, statusCheck, userCheck, connection):
    if(connection == ''):
        root.destroy()
    else:
        root.destroy()
        with connection.cursor() as cursor:
            sqlQuery = "UPDATE `user` SET `status`=%s WHERE `user_nome`=%s"
            cursor.execute(sqlQuery, (statusCheck ,userCheck))
            connection.commit()