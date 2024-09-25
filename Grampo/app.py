import sys,re,typing
from .ut.Storage import Sessions
from telethon import errors,events
from .td import TDesktop
from .tl import TelegramClient
from .tl.telethon import types,functions,utils
from .ut.api import API, CreateNewSession, UseCurrentSession
from .tl.configs import StringSession
from .config import  GrampoOptions
import base64,struct
import shutil,os,asyncio
from telethon.tl.functions.messages import RequestWebViewRequest,RequestAppWebViewRequest
from telethon.tl.types import (
    InputUser,
    Message,
    InputBotAppShortName,
    InputUser,
    )

class TelegramApp(TelegramClient):
    def __init__(self,phone:str,proxy:dict|list|None=None,options:GrampoOptions|None=None):
        self.phone=phone
        self.proxy=proxy
        self.session_password:str=''
        self.is_online=False
        self.options =options if options else GrampoOptions()
        self.SESSIONS=Sessions(self.options.sessions_path).create_table()
       
        
    
    
    def __call_password(self)-> str:
        return input('Please enter your password: ')
    
    
    def __call_phone(self,phone:str=None )-> str:
        return phone or self.phone or  input('Please enter your phone (or bot): ')
       
    
    def __call_code(self)-> str:
        return input('Please enter the code you received: ')
    
    
    
    def __call_first_name(first_name:str=None):
        first_name=first_name or input('Please enter your first name: ')
        while not first_name:
            first_name=input('Please enter your first name: ')
        
        return first_name
    
    
    def __call_last_name(last_name:str=None):
        return last_name if last_name is not None else input('Please enter your last name: ')
        


    async def start_telegram(self,phone:str=None, first_name:str=None, last_name:str=None, max_attempts=5):
        conn=await self.connect_telegram(phone)
        if not conn:
            conn=await self.new_register(phone, first_name, last_name,max_attempts)

        if conn:
            return conn
    
    
    async def __save_session(self,api_info:API.TelegramAndroid):
        me=await self.get_me()
        self.phone=f"+{me.phone}" if me.phone else f"BOT-{me.id}"
        telethon_session=StringSession.save(self.session)
        account_data={
                    "phone":self.phone,
                    "dc_id":self.session.dc_id or 1  ,
                    "user_id":me.id,
                    "username":(me.username or ""),
                    "first_name":me.first_name,
                    "last_name":(me.last_name or "") ,
                    "password" :self.session_password,
                    "api_id":self.api_id,
                    "api_hash":self.api_hash,
                    "telethon":telethon_session,
                    "pyrogram":self.pyrogram_string_session(self,me.id),
                    "device_model":api_info.device_model,
                    "system_version":api_info.system_version,
                    "app_version":api_info.app_version,
                    "status":"ACTIVE",
                    "is_bot": me.bot
                    }
        self.SESSIONS.delete(phone=self.phone)
        self.SESSIONS.insert_one(account_data)
        signed, name = 'Signed in successfully as ', utils.get_display_name(me)
        try:
            print(signed, name)
        except UnicodeEncodeError:
            print(signed, name.encode('utf-8', errors='ignore').decode('ascii', errors='ignore'))
        self.is_online=True
    
    async def new_register(self,phone:str=None, first_name:str=None, last_name:str=None, max_attempts=5):
        
        if self.is_online:
            return True

        android_api= API.TelegramAndroid.Generate()
        android_api.lang_code=self.options.lang_code
        android_api.system_lang_code=self.options.system_lang_code
        super().__init__(None, api=android_api,proxy=self.proxy)
        await self.connect()
        
        bot_token=''
        if ':' in phone:
            bot_token = phone
        
        while not phone:
            value = self.__call_phone(phone)
            if not value:
                continue
            if ':' in value:
                bot_token = value
                break

            phone = utils.parse_phone(value) 

        
        if bot_token:
            await self.sign_in(bot_token=bot_token)
            await self.__save_session(android_api)
            
            return True

        me = None
        attempts = 0
        two_step_detected = False

        cod=await self.send_code_request(phone)
        print(f'Send code type: {cod.type.__class__.__name__}')
        _code=''
        while attempts < max_attempts:
            try:
                value =self.__call_code() 
                if value=='next':
                   cod=await self.send_code_request(phone)
                   print(f'Send code type: {cod.type.__class__.__name__}')

                
                if not value:
                    raise errors.PhoneCodeEmptyError(request=None)

                _code=value
                me = await self.sign_in(phone, code=value)
                break
            except errors.SessionPasswordNeededError:
                two_step_detected = True
                break
            except (errors.PhoneCodeEmptyError,
                    errors.PhoneCodeExpiredError,
                    errors.PhoneCodeHashEmptyError,
                    errors.PhoneCodeInvalidError):
                print('Invalid code. Please try again.', file=sys.stderr)
            except errors.PhoneNumberUnoccupiedError:
                me=await self.__sign_up(_code,first_name,last_name)
                break
            attempts += 1
        else:
            raise RuntimeError('{} consecutive sign-in attempts failed. Aborting'.format(max_attempts))

       
        if two_step_detected:
            for _ in range(max_attempts):
                try:
                    value = self.__call_password()
                    me = await self.sign_in(phone=phone, password=value)
                    self.session_password=value
                    break
                except errors.PasswordHashInvalidError:
                    print('Invalid password. Please try again',file=sys.stderr)
            else:
                raise errors.PasswordHashInvalidError(request=None)

        await self.__save_session(android_api)
        
        return True

    
    async def connect_telegram(self,phone:str=None):
        
            
        
        phone=self.__call_phone(phone)
        if ":" in phone:
            phone=f"BOT-{phone.split(':')[0]}"
        
        session=self.SESSIONS.get_one(phone=phone)
        self.exist_session=session.has_data
        if session.has_data:
            if self.is_online:
                return session
            
            android_api= API.TelegramAndroid(
                api_id=session.api_id,
                api_hash=session.api_hash,
                device_model=session.device_model,
                system_version=session.system_version,
                app_version=session.app_version, 
                lang_code=self.options.lang_code, 
                system_lang_code=self.options.system_lang_code
                )
            self.session_password=session.password
            super().__init__(StringSession(session.telethon), api=android_api,proxy=self.proxy)
            self.phone=phone
            self._phone=phone
            await self.connect()
            if await self.is_user_authorized():
                self.SESSIONS.update({"status":'ACTIVE'},phone=self.phone)
                self.is_online=True
                return session

            else:
                self.SESSIONS.update({"status":'INACTIVE'},phone=self.phone)

                return False
        
            
    async def get_login_code(self):
        def search_code(text):
            cods=re.findall(r'Login code: *(\d+\d*) *\.',  text)
            if not cods:
                cods=re.findall(r': *(\d+\d*) *\.', text )
            return cods[0] if cods else ''
        
        async with self.conversation(777000) as conv:
            try:
                event:Message =await conv.wait_event(events.NewMessage(777000,func=lambda e: bool(search_code(e.message.message))) , timeout=300)
                code=search_code(event.message.message)
                
                return code
            
            except TimeoutError:
                print('time out error ')

    async def __sign_up(self,
                        code: typing.Union[str, int],
                        first_name: str,
                        last_name:str,
                        *,
                        phone: str = None,
                        phone_code_hash: str = None) -> 'types.User':
        
        

        if phone and not code :
            return await self.new_register(phone)

        
        elif code:
            phone, phone_code_hash =  self._parse_phone_and_hash(phone, phone_code_hash)
            first_name=self.__call_first_name(first_name)
            last_name=self.__call_last_name(last_name)
            request = functions.auth.SignUpRequest(phone, phone_code_hash, first_name,last_name)
        
        
        try:
            result = await self(request)
        except errors.PhoneCodeExpiredError:
            self._phone_code_hash.pop(phone, None)
            raise

        if isinstance(result, types.auth.AuthorizationSignUpRequired):

            self._tos = result.terms_of_service
            raise errors.PhoneNumberUnoccupiedError(request=request)

        return await self._on_login(result.user)
    
    async def convert_to_tdata(self,output_dir:str,new_session=False,password:str=None) -> TDesktop:
        output_path=os.path.join(output_dir,self.phone,'tdata')
        conn=await self.connect_telegram(self._phone) 
        if conn:
            password = password if password else conn.password
            tdesk = await self.ToTDesktop(
                                        flag=CreateNewSession if new_session else UseCurrentSession  ,
                                        api=API.TelegramDesktop() ,
                                        password=password,
                                        proxy=self.proxy
                                        )
            
            if os.path.exists(output_path):
                shutil.rmtree(output_path,ignore_errors=True)
            tdesk.SaveTData(output_path)
            
            return tdesk
            
    

    async def re_new_session(self,password:str|None=None):
        conn=await self.connect_telegram() 
        if conn:
            new_sessions=Sessions(f"new-{self.options.sessions_path}").create_table()
            android_api= API.TelegramAndroid.Generate(unique_id=self.phone)
            client:TelegramClient=await self.QRLoginToNewClient(None,android_api,password=password)
            me=await client.get_me()
            telethon_session=StringSession.save(client.session)
            
            account_data={
                "phone":self.phone,
                "dc_id":client.session.dc_id or 1  ,
                "user_id":me.id,
                "username":(me.username or ""),
                "first_name":me.first_name,
                "last_name":(me.last_name or "") ,
                "password" :password,
                "api_id":client.api_id,
                "api_hash":client.api_hash,
                "telethon":telethon_session,
                "pyrogram":self.pyrogram_string_session(client,me.id),
                "device_model":android_api.device_model,
                "system_version":android_api.system_version,
                "app_version":android_api.app_version,
                "status":"ACTIVE",
                "is_bot": me.bot
                }
            
            
            
            sess=new_sessions.get_one(phone=self.phone)  
            if sess.has_data:
                account_data.pop('phone')
                new_sessions.update(account_data,phone=self.phone)
            else:
                new_sessions.insert_one(account_data)
            
            
            signed, name = 'Signed in successfully as ', utils.get_display_name(me)
            try:
                print(signed, name)
            except UnicodeEncodeError:
                print(signed, name.encode('utf-8', errors='ignore').decode('ascii', errors='ignore'))
            
            return True
        
        
    async def delete_password(self):
        
        result =await self(functions.account.GetPasswordRequest())
        
        if result.has_password:
            res = await self(functions.account.ResetPasswordRequest())
            if res.__class__.__name__=="ResetPasswordOk":
                self.SESSIONS.update({"password":''},phone=self.phone)
                return True,"ResetPasswordOk"
            
            return False, res

        else:
            self.SESSIONS.update({"password":''},phone=self.phone)
            return True,"NoPassword"
        
    
    async def set_password(self,new_password='',current_password=''):

        result =await self.edit_2fa(current_password=current_password, new_password=new_password)
        
        if result is True:
            self.SESSIONS.update({"password":new_password},phone=self.phone)
        return result


    async def get_webview_auth_url(self,
                                   bot_username:str,
                                   is_miniapp:bool,
                                   short_name:str|None=None,
                                   app_url:str|None=None,
                                   peer:str|None=None,
                                   start_param:str|None=None,
                                   
                                   ):
        
        
        if not peer:
            peer=bot_username
        
        
        
            
        if is_miniapp:
            entyty=await self.get_entity(bot_username)
            bot_app= InputBotAppShortName( bot_id=InputUser(user_id=entyty.id,access_hash= entyty.access_hash), short_name=short_name)
            await asyncio.sleep(1)        
            web_view = await self(RequestAppWebViewRequest(
                            peer= peer,
                            app= bot_app,
                            platform= 'android',
                            write_allowed=True,
                            start_param= start_param))
            
        else:
            web_view = await self(RequestWebViewRequest(
                                peer=peer,
                                bot=bot_username,
                                platform='android',
                                from_bot_menu=False,
                                start_param=start_param,
                                url=app_url))
                    
        return web_view.url


    async def start_bot(self,bot_username,ref_code='',join_list=[],peer=''):
            try:
                for chat in join_list:
                    print(f'[{self.phone}] Join chat ...')
                    await self(functions.channels.JoinChannelRequest(chat))
            
                if not peer:peer=bot_username
                dialog:types.Dialog
                started=False
                async for dialog in self.iter_dialogs():
                    if isinstance(dialog.entity,types.User) and dialog.entity.username==bot_username:
                        started=True
                        break
                    
                
                if not started:
                    print(f'[{self.phone}] Start {bot_username}...')
                    await self(functions.messages.StartBotRequest(bot=bot_username,peer=peer,start_param=ref_code))
                        
                return True
            except Exception as e:
                print(e)


    @staticmethod
    def pyrogram_string_session(client:TelegramClient,user_id:int):
        try:
            telethon_session=StringSession.save(client.session)
            STRING = telethon_session[1:]
            ip_len = 4 if len(STRING) == 352 else 16
            dc_id, ip, port, auth_key= struct.unpack('>B{}sH256s'.format(ip_len),base64.urlsafe_b64decode(STRING))
            packed = struct.pack(">BI?256sQ?",dc_id,client.api_id,0,auth_key,user_id,0)
            return base64.urlsafe_b64encode(packed).decode().rstrip("=")
        except Exception as e:
            print(e)
            return ''
