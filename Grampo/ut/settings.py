import json
class settings:
    sessions_path:str='sessions.ses'
    lang_code:str='en'
    system_lang_code:str='en'
    def __init__(self) -> None:
        # options=['sessions_path','lang_code','system_lang_code']
        file_exist=False
        try:
            settings=json.load(open('settings.json',encoding='utf-8'))
            if isinstance(settings,dict):
                self.__dict__.update(settings)
                file_exist=True
        except :
            pass
        if not file_exist:
            with open('settings.json','w',encoding='utf-8') as save:
                settings_dict={
                        "sessions_path":'sessions.ses',
                        "lang_code":'en',
                        "system_lang_code":'en',
                        }
                json.dump(settings_dict,save,ensure_ascii=False,indent=4)
    
Settings=settings()
# print(x.sessions_path)