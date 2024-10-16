import json
import asyncio
import aiohttp
import db.db as db
from .Push import send_push


MainURL = "https://sd.sprt-service.ru/sd/services/rest"
accesskey = "364041b3-4853-41f4-96e5-6de8d19d298f"
headers = {'Content-Type': 'application/json'}


lock = asyncio.Lock()

async def userUUID(login):
    url = f"{MainURL}/find/employee?accessKey={accesskey}&attrs=UUID"
    data = {
        "telegram": login
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            if response.status == 200:
                user_uuid = await response.json()
                if not user_uuid:
                    return None
                else:
                    user_uuid = user_uuid[0]["UUID"]
            else:
                print(f"Error: {response.status}")
    return user_uuid


async def key(login):
    url = f"{MainURL}/find/employee?accessKey={accesskey}&attrs=keyEmployee"
    data = {
        "telegram": login
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            if response.status == 200:
                keyEmployee = await response.json()
                if not keyEmployee:
                    return None
                else:
                    keyEmployee = keyEmployee[0]["keyEmployee"]
                    if keyEmployee == True:
                        keyEmployee = 0
                    else:
                        keyEmployee = 1
            else:
                print(f"Error: {response.status}")
    return keyEmployee


async def view_requests(user_uuid):
    url = f'{MainURL}/find/serviceCall?accessKey={accesskey}&attrs=UUID,shortDescr,descriptionRTF,number,responsible,state'
    data = {
        "clientEmployee": user_uuid,
        "state": ["registered", "inprogress", "waitClientAnswer","deferred"]
        }
    json_data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json_data) as response:
            if response.status == 200:
                result = await response.json()
            else:
                print(f"Error: {response.status}")
    return result


async def view_comment(uuid):
    url = f"{MainURL}/find/comment?accessKey={accesskey}&attrs=author,text,private"
    data = {
        "source": uuid
    }
    json_data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json_data) as response:
            if response.status == 200:
                result_text = await response.json()
            else:
                print(f"Error: {response.status}")
    return result_text


async def send_comment_to_api(uuid, user_uuid,user_comment, image):
    print(type(user_comment))
    if user_comment is None:
        user_comment = " "
    url = f"{MainURL}/create-m2m/comment?accessKey={accesskey}&attrs="
    if image:
        user_comment = await build_html_content(user_comment, image)
    if user_uuid == "0":
        data = {
            "source": uuid,
            "text": [user_comment],
        }
    else:
        data = {
            "source": uuid,
            "text": [user_comment],
            "author": [user_uuid]
        }
    json_data = json.dumps(data)
    result_text = None
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json_data, headers=headers) as response:
            if response.status == 201:
                return True
            else:
                print(f"Error: {response.status}")
                return False

async def build_html_content(user_comment, image):
    html_content = f"<p>{user_comment}</p>"
    html_content += f'<img src="data:image/jpeg;base64,{image}">'
    return html_content

async def ou_request(user_uuid):
    url = f"{MainURL}/get/{user_uuid}?accessKey={accesskey}&attrs=parent"
    result_text = None
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                result_text = await response.json()
                result_text = result_text['parent']['UUID']
            else:
                print(f"Error: {response.status}")
            return result_text
        
async def office_request(ou_uid):
    url = f"{MainURL}/get/{ou_uid}?accessKey={accesskey}&attrs=childOUs"
    result_text = None
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                result_text = await response.json()
            else:
                print(f"Error: {response.status}")
            return result_text
        
        
async def send_service_to_api(short, descr, critical , ou_uid, user_uuid, office, number, login, image):
    url = f"{MainURL}/create-m2m/serviceCall?accessKey={accesskey}&attrs="
    if descr == None:
        descr = " "
    if image:
        descr = await build_html_content(descr, image)
    if ou_uid == "0":
        data =  {
        "metaClass" : "serviceCall$request",
        "shortDescr" : short ,
        "descriptionRTF": descr + str(number),
        "agreement" : critical,
    }
    else:
        data =  {
        "metaClass" : "serviceCall$request",
        "shortDescr" : short,
        "descriptionRTF": descr,
        "agreement" : critical,
        "clientOU" : ou_uid,
        "clientEmployee" : user_uuid,
        "office" : office
    }
    data = json.dumps(data)
    result_text = None
    async with aiohttp.ClientSession() as session:
        async with session.post(url,data = data) as response:
            if response.status == 201:
                result = True
                task = await response.json()
                uuid = task["UUID"]
                if ou_uid == "0":
                    await db.write_task(uuid, login)
                return result
            else:
                result = False
                print(f"Error: {response.status}")
                return result


async def push():
    url = f"{MainURL}/find/serviceCall?accessKey={accesskey}&attrs=lastComment,client,number,UUID,state,resultDescr"
    data = {
         "state": ["waitClientAnswer", "resolved"]
         }
    json_data = json.dumps(data)
    async with lock:
        async with  aiohttp.ClientSession() as session:
            async with session.post(url,data = json_data) as response:
                if response.status == 200:
                    result_text = await response.json()
                    await send_push(result_text)
                else:
                    print(f"Error: {response.status}")
                    

async def loop_push():
    while True:
        await push()
        

async def find_telegram(uuid):
    url = f"{MainURL}/find/employee?accessKey={accesskey}&attrs=telegram"
    data = {
        "UUID": uuid
    }
    json_data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(url,data = json_data) as response:
            if response:
                telegram_username = await response.json()
                return telegram_username
            else:
                return None
            


async def find_contact(login):
    URL = f"{MainURL}/find/employee?accessKey=364041b3-4853-41f4-96e5-6de8d19d298f&attrs=mobilePhoneNumber"
    data = {
        "telegram":login
        }
    async with aiohttp.ClientSession() as session:
        async with session.post(URL, data = data) as response:
            if response.status == 200:
                result = await response.json()
                if not result:
                    return False
                else:
                    phone_number = result[0].get('mobilePhoneNumber')
                    return phone_number
            else:
                print(f"Error: {response.status}")




async def handle_user(message, user_contact):
    url = f"{MainURL}/find/employee?accessKey={accesskey}&attrs=UUID"
    login = message.from_user.username
    chat = message.chat.id
    data = {
        "mobilePhoneNumber":user_contact
        }
    json_data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(url,data = json_data) as response:
            if response.status == 200:
                response = await response.json()
                if response:
                    uuid = response[0].get("UUID")
                    await change_telegram(login, uuid)
                    await db.write_user_info(login, chat)
                else:
                    await db.write_unauth(login,chat, user_contact)


async def change_telegram(login, uuid):
    url = f"{MainURL}/edit-m2m/{uuid}?accessKey={accesskey}&attrs=UUID"
    data = {
        "telegram": login
    }
    json_data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(url,data = json_data) as response:
            if response:
                await response.json()
                
                
async def find_task(servicecall):
    URL = f"{MainURL}/find/serviceCall?accessKey=364041b3-4853-41f4-96e5-6de8d19d298f&attrs=UUID,number,shortDescr,descriptionRTF,responsible,state"
    data = {
        "state": ["registered", "inprogress", "waitClientAnswer",],
        "UUID": servicecall
        }
    json_data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(URL, data=json_data) as response:
            if response.status == 200:
                result = await response.json()
            else:
                print(f"Error: {response.status}")
    return result


async def revive(uuid):
    url = f"{MainURL}/edit-m2m/{uuid}?accessKey={accesskey}&attrs=UUID"
    data = {
        "state": "resumed"
    }
    json_data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(url,data = json_data) as response:
            if response:
                await response.json()
                
                
async def mark(uuid, mark):
    url = f"{MainURL}/edit-m2m/{uuid}?accessKey={accesskey}&attrs=UUID"
    data = {
        "mark": mark,
        "state": "closed"
    }
    json_data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(url,data = json_data) as response:
            if response:
                await response.json()
                
                
async def take_task():
    url = f'{MainURL}/find/serviceCall?accessKey={accesskey}&attrs=UUID,shortDescr,descriptionRTF,number,responsible,clientOU,state'
    data = {
        "state": ["registered", "inprogress", "waitClientAnswer","deferred"]
        }
    json_data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json_data) as response:
            if response.status == 200:
                result = await response.json()
            else:
                print(f"Error: {response.status}")
    return result

async def download_photo(file_uuid):
    file_download_url = f'https://sd.sprt-service.ru/sd/services/rest/get-file/file${file_uuid}?accessKey={accesskey}'
    async with aiohttp.ClientSession() as session:
        async with session.get(file_download_url) as response:
            if response.status == 200:
                # Получаем содержимое фото
                photo_data = await response.read()
                # Сохраняем фото в файл
                file_path = f"template/{file_uuid}.jpg"
                with open(file_path, 'wb') as file:
                    file.write(photo_data)
                
                # Возвращаем путь к сохраненному файлу
                return file_path
            else:
                print(f"Error downloading photo. Status code: {response.status}")
                return None



async def refresh_info(login,number,uuid):
    url = f"{MainURL}/edit-m2m/{uuid}?accessKey={accesskey}&attrs=UUID"
    print(login,number,uuid)
    data = {
        "telegram": login,
        "mobilePhoneNumber": number
    }
    json_data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(url,data = json_data) as response:
            if response:
                await response.json()


async def find_user(number):
    url = f"{MainURL}/find/employee?accessKey={accesskey}&attrs=UUID"
    data = {
        "mobilePhoneNumber":number
        }
    json_data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(url,data = json_data) as response:
            if response.status == 200:
                response = await response.json()
                if response:
                    uuid = response[0].get("UUID")
                    return uuid
