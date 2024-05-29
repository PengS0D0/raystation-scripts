# encoding: utf8

# A class for interacting with the Mosaiq database.
#
# Authors:
# Christoffer Lervåg
# Helse Møre og Romsdal HF
#
#raystation 11B is only support ODBC,

import pyodbc 

class Database:
  
  # The Mosaiq SQL server address:
  server = open(r'C:\temp\raystation-scripts\mosaiq\database.txt', "r").read()
  # The username to be used for access to the Mosaiq database:
  user = open(r'C:\temp\raystation-scripts\mosaiq\user.txt', "r").read()
  # The password to be used for access to the Mosaiq database:
  password = open(r'C:\temp\raystation-scripts\mosaiq\password.txt', "r").read()
  
  # Returns all rows matching the given query text (or an empty list if no match).
  @staticmethod
  def fetch_all(text):
    conn =  pyodbc.connect(driver='{SQL Server}',
                                              host=server,
                                              user=user, 
                                              password=password, 
                                              trusted_connection='no', #yes for Windows authenticationn 
                                              database='MOSAIQ')
    cursor = conn.cursor(as_dict=True)
    if parameters:
      # print(text)
      cursor.execute(text,parameters)
    else:
      cursor.execute(text)    
    columns = [column[0] for column in cursor.description]
    rows = list()
    for row in cursor:
      rows.append(dict(zip(columns,row)))
    conn.close()
    return rows
  
  # Returns a single row matching the given query text (or None if no match).
  @staticmethod
  def fetch_one(text):
    conn = pyodbc.connect(driver='{SQL Server}',
                                              host=server,
                                              user=user, 
                                              password=password, 
                                              trusted_connection='no', #yes for Windows authenticationn 
                                              database='MOSAIQ')
    cursor = conn.cursor()
    if parameters:
      try:
        cursor.execute(text,parameters)#return self._cursor.execute(query,parameters)
        row = cursor.fetchone()
      except:
        row = None
    else:
      try:
        cursor.execute(text)
        row = cursor.fetchone()
      except:
        row = None #print(str(row))
    conn.close()
    columns = [column[0] for column in cursor.description]#get column header
    row = dict(zip(columns,row))
    return row

#root = Tk()
#root.withdraw()
#title = ""
#text = ""
#messagebox.showinfo(title, text)
#root.destroy()
