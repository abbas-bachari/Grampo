class GrampoOptions:
    def __init__(self,
                 sessions_path:str      ='sessions.ses',
                 lang_code:str          ='en',
                 system_lang_code:str   ='en'
                 ) -> None:
        
        self.sessions_path      = sessions_path
        self.lang_code          = lang_code
        self.system_lang_code   = system_lang_code

