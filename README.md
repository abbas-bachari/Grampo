[![Grampo](https://img.shields.io/badge/Grampo%20-Version%201.0.1-green?style=plastic&logo=codemagic)](https://python.org)




# A Python Telegram API Library , with official Telegram APIs.





## Installation guide

Install from source:
``` bash
pip install git+https://github.com/abbas-bachari/Grampo.git
```



<!-- ## user manual -->

##  Quick start

```python
import asyncio
from Grampo import TelegramApp



async def main():
    telegram=TelegramApp(None,['http','127.0.0.1',10809])

    # If there is a session, it will start it, otherwise,
    # a new session will be created and saved.
    await telegram.start_telegram('+9811122233')
    
    me=await telegram.get_me()
    
    print(me.first_name)

    await telegram.disconnect()


if __name__=="__main__":
    asyncio.run(main())

```
 



### Connect to a saved session:

```python
async def main():
    telegram=TelegramApp('+9811122233',['http','127.0.0.1',10809])

    await telegram.connect_telegram()
    
    me=await telegram.get_me()
    
    print(me.first_name)

    await telegram.disconnect()
    


if __name__=="__main__":
    asyncio.run(main())

```



#
### Convert telethon session to tdata (desktop session):

```python
async def main():
    
    telegram=TelegramApp('+9811122233',['http','127.0.0.1',10809])
    await telegram.start_telegram()
    
    me=await telegram.get_me()
    print(me.first_name)
    
    # Use the current session
    tdesk=await telegram.convert_to_tdata('E:/TelegramApp/TD-DATAS')
    
    
    # # Create a new desktop session
    # tdesk=await telegram.convert_to_tdata(
    #     output_dir='E:/Telegram/TD-DATAS',
    #     new_session=True,
    #     password='password')
    
    # Use the current session
    
    tdesk=await telegram.convert_to_tdata(output_dir='E:/Telegram/TD-DATAS',new_session=False)
    
    await telegram.disconnect()     
    
    client:TelegramApp=await tdesk.ToTelethon(None,flag=UseCurrentSession,api=tdesk.api,proxy=['http','127.0.0.1',10809])
    
    
    await client.connect()
    await client.PrintSessions()

if __name__=="__main__":
    asyncio.run(main())

```
#
### Get login code:

```python
import asyncio
from Grampo import TelegramApp

async def main():
    telegram=TelegramApp('+9811122233',['http','127.0.0.1',10809])

    await telegram.connect_telegram()
    
    me=await telegram.get_me()
    
    print(me.first_name)

    
    print('Now apply for login in the TelegramApp app:')
    
    code=await telegram.get_login_code()
    
    print('Login Code: ', code)
    
    await telegram.disconnect()

if __name__=="__main__":
    asyncio.run(main())

```
#
### Manage saved sessions:

```python
from Grampo import SESSIONS


session=SESSIONS.get_one(phone='+9811122233') 
print(f"Name: {session.first_name:<15} | Is bot: {'YES' if session.is_bot else 'NO':<3} | status: {session.status}")


all_sessions=SESSIONS.get_many()
for session in all_sessions:
    print(f"Name: {session.first_name:<15} | Is bot: {'YES' if session.is_bot else 'NO':<3} | status: {session.status}")
    
    
    
active_sessions=SESSIONS.get_many(status='ACTIVE')


inactive_sessions=SESSIONS.get_many(status='INACTIVE')


bot_sessions=SESSIONS.get_many(is_bot=True)


random_session=SESSIONS.get_one(random=True, status='ACTIVE',is_bot=False)
  

first_5_sessions=SESSIONS.get_many(limit=5, status='ACTIVE',is_bot=False)
 

delete_session=SESSIONS.delete(is_bot=True)
print(f'Deleted {delete_session} session !')


delete_all_session=SESSIONS.delete(delete_all=True)
print(f'Deleted {delete_all_session} session !')



delete_inactive_session=SESSIONS.delete(status='INACTIVE')
print(f'Deleted {delete_inactive_session} session !')


update_session=SESSIONS.update({'status':'INACTIVE'},is_bot=True)
print(f'Update {update_session} session !')

update_session=SESSIONS.update({'status':'INACTIVE'},phone='+9811111')
print(f'Update {update_session} session !')
```


Powered by [Abbas Bachari](https://github.com/abbas-bachari).
