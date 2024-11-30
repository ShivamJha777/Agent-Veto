import requests
def deepseek(message,cot= True):
    url = "https://chat.deepseek.com/api/v0/chat/completion"
    cookie = {
        "_frid":"88c1ef4572ab42b091406beb7f5efc67",
        "intercom-device-id-guh50jw4":"a2f04e80-303d-47f2-a742-1f56f09cf846",
        "HWWAFSESID":"f3ac776dc40f14b913",
        "HWWAFSESTIME":"1732708119664",
        "_fr_ssid":"585bd537c5754f08acf6dafa84b3238e",
        "_fr_pvid":"b15c03c2d51346439010d9f7c0374f26",
        "intercom-session-guh50jw4":"N1h6eURmUWRsekp4T3NCQ3FRT2tMaDVZc3VRQm9RZmZtT1phTVpTeWxkSXFoVkZYRkJkY09CWDBIV1I2aFRvUC0tUGJMYWlOK1FoRzFVUlZqN1ZPR3Jadz09--08426c42536693fa8d360349533d55fc9966c88e"
    }
    headers = {
        "Authorization":"Bearer 5ee1300c1fcb4d168e522fd42abb1930"
    }
    payload = {
        "chat_session_id":"00bbc155-43f5-47e4-9858-e9f9b1e86521",
        "prompt":message,
        "ref_file_ids":[],
        "thinking_enabled" : cot,
        "parent_message_id":5
    }
    response = requests.post(url, headers=headers, cookies=cookie, json=payload)
    print(response.text)
    if response.status_code == 200:
        return response.text
print(deepseek("Hello, how are you?"))