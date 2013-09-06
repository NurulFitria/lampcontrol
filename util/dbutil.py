import wx
import MySQLdb

class MySQL(object):
    
    def __init__(self, host, user, password, dbname):
        """
        Mengambil data untuk koneksi ke database MySQL
        """
        self._host = host
        self._user = user
        self._pass = password
        self._name = dbname

    def _db_connect(self):
        conn = MySQLdb.connect(self._host, self._user, self._pass, self._name)
        return conn

    def commit_db(self, sql):
        """
        Melakukan perubahan pada database dengan INSERT
        atau UPDATE
        """
        conn = self._db_connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        cursor.close()
        conn.commit()
        
        conn.close()

    def fetch_one(self, sql):
        """
        Mengambil hanya satu record
        """
        conn = self._db_connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return result
    
    def fetch_all(self, sql):
        """
        Mengambil semua keluaran dari query
        return 2-dimensional tuple
        """
        conn = self._db_connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()

        return result 
    
    def fetch_field(self, sql):
        """
        Mengambil hanya satu field dan merubah menjadi list
        """
        result = self.fetch_all(sql)
        lst = []
        for x in result:
            lst.append(x[0])

        return tuple(lst)

    def fetch_single(self, sql):
        result = self.fetch_one(sql)
        
        return result[0]
        
    def delete_db(self,sql):
    	conn = self._db_connect()
        cursor = conn.cursor()
        try:
        	cursor.execute(sql)
        	conn.commit()
        except:
        	conn.rollback()
        conn.close()
        
    def update_db(self,sql):
    	conn = self._db_connect()
        cursor = conn.cursor()
        try:
        	cursor.execute(sql)
        	conn.commit()
        except:
        	conn.rollback()
        conn.close()
