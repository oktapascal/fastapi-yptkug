from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from datetime import datetime
import time
import os
import pandas
import pyodbc
from dotenv import load_dotenv
from database import database

load_dotenv()

def connect_dbdevyptkug():
  engine = database.Database(os.getenv('DB_USER'),os.getenv('DB_PASSWORD'),os.getenv('DB_HOST'),os.getenv('DB_NAME'))
  
  dbdevyptkug_engine = engine.connect()
  
  return dbdevyptkug_engine

app = FastAPI()

@app.get("/")
def read_root():
    return {'status': 'OK', 'message': 'Hello From Fastapi-YPTKUG'}
  
@app.get('/test-db')
def test_db():
  try:
    dbdevyptkug = connect_dbdevyptkug()
    print("{c} is working".format(c=dbdevyptkug))
    dbdevyptkug.close()
    
    return {'status': 'OK', 'message': 'Success Connect Database'}
  except pyodbc.Error as ex:
    print("{c} is not working".format(c=dbdevyptkug))
    
@app.get('/api/export/excel/lokasi')
def export_excel_lokasi(background_task: BackgroundTasks):
  columns = ["kode_lokasi","nama","alamat","kota", "kodepos","no_telp","no_fax","flag_konsol","logo","email","website","npwp","pic","kode_lokkonsol",
            "tgl_pkp","flag_pusat","flag_aktif","skode","flag_sak"]
  
  try:
    dbdevyptkug = connect_dbdevyptkug()
    cursor = dbdevyptkug.cursor()
    
    sql_statement = f"""
    select a.*
    from lokasi a
    """
    cursor.execute(sql_statement)
    
    dataframe = pandas.DataFrame.from_records(cursor.fetchall(), columns=columns)
    
    today = datetime.today()
    unique_id = today.strftime('%Y%m%d%H%M%S')
    
    file_name = f'DATA_LOKASI_{unique_id}.xlsx'
    
    writer = pandas.ExcelWriter(file_name)
    
    dataframe.to_excel(writer,index=False)
    
    writer.close()
    cursor.close()
    dbdevyptkug.close()
    
    headerResponse = {
      'Content-Disposition': 'attachment; filename="'+file_name+'"'
    }
    
    background_task.add_task(os.remove, file_name)
    
    del dataframe
    
    return FileResponse(path=file_name, headers=headerResponse, filename=file_name)
  except Exception as ex:
    return {"status": False, "message": str(ex)}