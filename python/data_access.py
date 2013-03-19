from pymongo import MongoClient

def connectionection_handler(f):
  def connectionect(self):
    try:
      connection = MongoClient('192.168.0.13', 27017)
      print 'database connection object issued'
      f(self, connection)
    except RuntimeError as e:
        print "Error occured while issuing connection \
        to database({0}): {1}".format(e.errno, e.strerror)
  return connectionect
  
'''
NOTE: Obtain and maintain database connection throughout the 
entirety of this object.

@author: bdason
'''
class DataAccess(object):
  @connectionection_handler
  def __init__(self, connection):
      self.connection = connection;
      self.db = self.connection['navrongo']

  # TODO: add param to fetch by id or argument   
  def fetch(self):
    if(self.connection is not None):
      print 'DataAccess.fetch called', self.connection
      # TODO: connection fetch routine

  # TODO: add param to insert by object
  def insert(self):
    print 'DataAccess insert called'
    if(self.connection is not None) and (self.db is not None):
      try:
        id = self.db.network.insert({
         'ip_addr': "192.168.0.1",
          'is_gateway': True,
          'mac_addr' : 'ad:3c:0c:h7:4f'
          })
        print 'network with id ->', id, 'inserted into database'
      except RuntimeError as e:
         print "Error Occured while performing insert({0}): {1}\
         ".format(e.errno, e.strerror)
    
b = DataAccess()
b.fetch()
b.insert();
