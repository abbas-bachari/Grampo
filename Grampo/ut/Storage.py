
import sqlite3,json,re
from datetime import datetime , timedelta



class FetchType:
    FETCH_ONE    = "ONE"
    FETCH_MULTI  = "MUTI"
    FETCH_COUNT  = "COUNT"

def data_convertor(string:str):
    
    if type(string)==str:
        string=string.strip()
        if string.upper() in ["YES","NO"]:
            return True if string.upper()=="YES" else  False
        
        date_time = re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', string)
        if date_time:
            return datetime.fromisoformat(string) 
        
        
        timer = re.compile(r'^(\d{2})\s*:\s*(\d{2})\s*:\s*(\d{2})$').search(string)
        if timer:
            hour, minute, second = timer.groups()
            return timedelta(hours=int(hour),minutes=int(minute),seconds=int(second))
    
    
    return string           

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        
        if isinstance(obj, timedelta):
            hour=  obj.seconds // 3600
            minute=obj.seconds %  3600 // 60
            second=obj.seconds %  60
            if obj.days > 0:
                hour+=obj.days*24

            return f"{hour:0>2}:{minute:0>2}:{second:0>2}"
        return json.JSONEncoder.default(self, obj)


fild_list=["phone" ,"dc_id" ,"user_id","username","first_name","last_name","password","api_id","api_hash", "telethon","pyrogram" ,"device_model", "system_version" ,"app_version" ,"status",'is_bot']

class Session:
    phone:str =""
    dc_id:int =0    
    user_id:int =0
    username:str=""
    first_name:str=""
    last_name:str=""
    password :str=""
    api_id:int  =0 
    api_hash:str=""
    telethon:str=""
    pyrogram:str=""
    device_model:str=""
    system_version:str=""
    app_version:str=""
    status:str=""
    is_bot:bool=False
    

    def __init__(self, data:dict):
        self.has_data=False
        self.data_dict={}
        if data and type(data)==dict:
            for k,v in data.items():
                if k not in fild_list:continue
                cv=data_convertor(v)
                self.data_dict[k]=cv
                self.__dict__[k]=cv
            self.has_data=True

    def to_json_str(self):
        return json.dumps(self.data_dict,indent=4,ensure_ascii=False,cls=DateTimeEncoder)
        
    def __str__(self) -> str:
        return self.to_json_str()


class Sessions:
    
    def __init__(self,db_name):
        self._db_name=db_name
        self._tb_name='sessions'
        

       
    
    def __quary(self,quary_string:str,values:str='',fetch_type:FetchType=FetchType.FETCH_COUNT,execute_many:bool=False):
        def dict_factory(cursor, row):
            sqd = {}
            for idx, col in enumerate(cursor.description):
                sqd[col[0]] = row[idx]
            return sqd
        
        conn=sqlite3.connect(self._db_name)
        conn.row_factory =dict_factory
        cursor= conn.cursor()
        
        cursor.executemany(quary_string,values) if execute_many else cursor.execute(quary_string,values)
        
        if fetch_type==FetchType.FETCH_MULTI:
            data=cursor.fetchall()
        elif fetch_type==FetchType.FETCH_ONE:
            data=cursor.fetchone()
        else:
            data=cursor.rowcount
        
            

        conn.commit()
        cursor.close()
        conn.close()

        return  data 
        


    def insert_one(self,jsondata:dict)->int:
        keys=','.join(list(jsondata.keys()))
        values=list(jsondata.values())
        pram=','.join((f'? '*len(values)).split())
        data=self.__quary(f"INSERT OR IGNORE INTO {self._tb_name} ({keys}) VALUES({pram})",values)
        return data
        
    
    
    def insert_many(self,data:list[dict])->int:
        keys=list(data[0].keys())
        values=[ list(d.values()) for d  in data]
        data=self.__quary(f"INSERT OR IGNORE INTO {self._tb_name} ({','.join(keys)}) VALUES({('?,'*len(keys))[:-1]})",values,execute_many=True)
        return data
    
    def get_one(self,random:bool=False,condition="",**kwargs) -> Session :
        
        randoming="ORDER BY RANDOM()" if random else ""

        if kwargs or condition:
            condition=f"{condition} AND " if (kwargs and condition) else condition
            if  kwargs: 
                
                keys=" AND ".join([f"{i}=?" for i in kwargs])
                values=list(kwargs.values())
                data=self.__quary(f"SELECT * FROM {self._tb_name} WHERE {condition} {keys} {randoming};",values= values,fetch_type=FetchType.FETCH_ONE)
            
            else:
                data=self.__quary(f"SELECT * FROM {self._tb_name} WHERE {condition} {randoming};",fetch_type=FetchType.FETCH_ONE)


        else:
            data=self.__quary(f"SELECT * FROM {self._tb_name} {randoming};",fetch_type=FetchType.FETCH_ONE)
            

        return Session(data)
    
    def get_many(self,limit=0,condition="",**kwargs)->list[Session]:
        lmt=f"LIMIT {limit}" if limit else ''
        if kwargs or condition:
            condition=f"{condition} AND " if (kwargs and condition) else condition
            if kwargs:
                keys=" AND ".join([f"{i}=?" for i in kwargs])
                values=list(kwargs.values())
                data=self.__quary(f"SELECT * FROM {self._tb_name} WHERE {condition} {keys} {lmt};",values= values,fetch_type=FetchType.FETCH_MULTI)
            else:
                data=self.__quary(f"SELECT * FROM {self._tb_name} WHERE {condition} {lmt};",fetch_type=FetchType.FETCH_MULTI)
            
        else:
            data=self.__quary(f"SELECT * FROM {self._tb_name} {lmt};",fetch_type=FetchType.FETCH_MULTI)
        
        
        return [Session(i) for i in data] if data else []
   



    def delete(self,delete_all=False,condition="",**kwargs)->int:
        if delete_all:
            return self.__quary(f"DELETE FROM {self._tb_name};")

        if kwargs or condition:
            condition=f"{condition} AND " if (kwargs and condition) else condition

            if kwargs:
                keys=" AND ".join([f"{i}=?" for i in list(kwargs.keys())])
                values=list(kwargs.values())
                return self.__quary(f"DELETE FROM {self._tb_name}  WHERE {condition} {keys}",values=values)
            else:
                return self.__quary(f"DELETE FROM {self._tb_name}  WHERE {condition}")
        
    
    
    
    def update(self,UpdateData:dict,condition="",**kwargs)->int:
        keys=",".join([f"{i}=?" for i in list(UpdateData.keys())])
        values=list(UpdateData.values())
        if kwargs or condition:
            condition=f"{condition} AND " if (kwargs and condition) else condition
            if kwargs:
                wkeys=" AND ".join([f"{i}=?" for i in list(kwargs.keys())])
                values.extend(list(kwargs.values()))
                data=self.__quary(f"UPDATE {self._tb_name}  SET {keys} WHERE {condition} {wkeys}",values=values)
            else:
                data=self.__quary(f"UPDATE {self._tb_name}  SET {keys} WHERE {condition} {wkeys}",values=values)
        else:
            data=self.__quary(f"UPDATE {self._tb_name}  SET {keys}",values=values)
        
        return data

    
    def create_table(self):
        table_data='''
                    phone           TEXT   PRIMARY KEY NOT NULL,
                    dc_id           INT    DEFAULT 1,
                    user_id         BIGINT     ,
                    username        TEXT   DEFAULT "",
                    first_name      TEXT   DEFAULT "",
                    last_name       TEXT   DEFAULT "",
                    password        TEXT   DEFAULT "",
                    api_id          INT    ,
                    api_hash        TEXT   ,
                    telethon        TEXT   DEFAULT "",
                    pyrogram        TEXT   DEFAULT "",
                    device_model    TEXT   DEFAULT 'Samsung Galaxy S20 Ultra 5G',
                    system_version  TEXT   DEFAULT '7.1 N MR1 (25)',
                    app_version     TEXT   DEFAULT '5',
                    status          TEXT   DEFAULT 'ACTIVE',
                    is_bot          BOOL   DEFAULT (FALSE)
                    
                    '''
        
        self.__quary(f'CREATE TABLE IF NOT EXISTS {self._tb_name} ({table_data});')
       
        return self

    def check_exist_table(self,tbname)->bool:
        data=self.__quary(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tbname}';",fetch_type=FetchType.FETCH_ONE)
        return True if data else False
    
    def get_count(self,condition="") -> dict:
        if condition:
            result=self.__quary(f"SELECT COUNT(*) FROM [{self._tb_name}] WHERE {condition};",fetch_type=FetchType.FETCH_ONE)
        else:
            result=self.__quary(f"SELECT COUNT(*) FROM [{self._tb_name}];",fetch_type=FetchType.FETCH_ONE)
            
        
        return  result.get('COUNT(*)',0) if result else 0
   
   

