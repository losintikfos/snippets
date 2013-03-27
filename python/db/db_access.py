
import MySQLdb

def connection_handler(fn):
    def connect(self):
        try:
            database = MySQLdb.connect(host="10.100.1.251",
                user="alan_admin", passwd="66ashtar",
                db="_stargate_simulation")
            fn(self, database)
        except RuntimeError as e:
            print("Error occured while connecting to database\
            :{0} {1}", e.errno, e.strerror)
    return connect

class DataAccess(object):
    
    @connection_handler
    def __init__(self, database):
        self.database = database
        self.cursor = self.database.cursor()
        self.database.autocommit(True)
 
    def select(self, command):
        resultset = None
        
        def fetch():
            return self.cursor.execute(command)
        
        if(self.cursor is not None) and (command is not None):
            resultset = fetch().fetchall()
        return resultset
    
    def commit(self, command, bulk=False):
        print("++++ Inserting values to catalog")
        def upsert():
            if bulk:
                print("+++++ Bulk insert found")
                # single loop scan
                for k, v in command.items():
                    self.cursor.executemany(k, v)
            else:
                self.cursor.execute(command)
            self.database.commit()
            print("------- commit executed successfully\n")
            
        if(self.cursor is not None) and (command is not None):
            upsert()
