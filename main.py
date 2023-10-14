import multiprocessing, requests, json, requests, hashlib, hmac, datetime, random, time
from typing import List, Dict
import telebot

CHAT_ID = [450919685, 572212271]
bot = telebot.TeleBot('6640866974:AAHAoI71ZVaD_CK9dXC-XwVQUlaquyhj-Vw')
user_states = {}

shared_resource = multiprocessing.Value('i', True)
lock = multiprocessing.Lock()
is_parsing = False


def requests_bybit(url:str, method:str, query_param:str='', payload_string:str='') -> Dict[str,dict]:
    key = "Hk8kF7w9nYREtu66hp"
    secret = "ocHDE3O3ce19tlWPEgc60dkp3gOPgBcQq3qE"

    recv_window = "5000"
    timestamp = str(int(requests.get("https://api.bybit.com" + "/v5/market/time").json()["result"]["timeSecond"])*1000)
    if method == "POST":
        payload_string["timestamp"] = int(timestamp)
        payload_string = str(payload_string)
        payload_string = payload_string.replace(" ", "").replace("'", '"')

    param_str = timestamp + key + recv_window + query_param + payload_string
    hash = hmac.new(bytes(secret, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
    signature = hash.hexdigest()
    headers = {
        'X-BAPI-API-KEY': key,
        'X-BAPI-SIGN': signature,
        'X-BAPI-TIMESTAMP': timestamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json',
    }
    return requests.request(method, "https://api.bybit.com" + url + '?' + query_param, headers=headers, data=payload_string)


def add_proxie(proxie: str) -> bool:
    if check_proxie(proxie):
        with open('proxies.json', 'r') as f:
            data = json.load(f)  
        proxies = data["proxies"]
        proxies.append(proxie)
        with open("proxies.json", "w") as f:
            json.dump({"proxies": proxies}, f, indent=2)
        return True
    return False


def check_proxie(proxie: str) -> bool:
    this_proxie = {"https": proxie, "http": proxie}
    try:
        r = requests.get("https://google.com", proxies=this_proxie, timeout=10)
        if r.status_code != 200:
            return False
    except:
        return False
    return True


def find_liguidity(symbol_token:str, proxies:dict):
    current_time = datetime.datetime.now()
    minutes_ago = current_time.minute % INTERVAL

    last_interval_time = current_time - datetime.timedelta(minutes=minutes_ago)
    previous_interval_time = last_interval_time - datetime.timedelta(minutes=INTERVAL)

    previous_last_interval_time = last_interval_time.replace(second=0)
    previous_interval_time = previous_interval_time.replace(second=0)

    start_time = previous_interval_time.timestamp()
    end_time = previous_last_interval_time.timestamp()

    url = '/derivatives/v3/public/kline'
    query_param = f"interval={INTERVAL}&symbol={symbol_token}&limit=2&start={int(start_time*1000)}&end={int(end_time*1000)}"
    response = requests.get("https://api.bybit.com"+url+"?"+query_param, proxies=proxies).json()["result"]
    if "list" in response:
        start = float(response["list"][0][5])
        end = float(response["list"][1][5])

        start_close = float(response["list"][0][4])
        end_close = float(response["list"][1][4])

        budget = float(response["list"][1][6])
        time_p = int(response["list"][0][0][:-3])

        if start != 0 and end != 0 and budget > MIN_BUDGET:
            percent = start/end*100
            print(symbol_token, round(percent, 2), budget)
            if percent > MIN_PERCENT:
                type_status = "Шорт" if start_close < end_close else "Лонг"
                return {"symbol": symbol_token, "percent": round(percent, 2), "interval": str(INTERVAL), "type_status": type_status, "time": time_p}
    return False


def run_me(tokens:list, proxie:dict):
    for token in tokens:
        with lock:
            if not shared_resource.value:
                break
        try:
            data = find_liguidity(token, proxie)
            if data:
                with open('status.json', 'r') as f:
                    status = json.load(f)
                message = f"Токен {data['symbol']} изменение на промежутке {data['interval']}м на {data['percent']}%.\nТип: {data['type_status']}. "
                print(message)
                if data["symbol"] in status:
                    if data["interval"] in status[data["symbol"]]:
                        if data["time"] != status[data["symbol"]][data["interval"]]:
                            status[data["symbol"]][data["interval"]] = data["time"]
                            for chat_id in CHAT_ID:
                                send_message_to_chat(chat_id, message+"Статус 1")
                    else:
                        status[data["symbol"]][data["interval"]] = data["time"]
                        for chat_id in CHAT_ID:
                            send_message_to_chat(chat_id, message+"Статус 2")
                else:
                    status[data["symbol"]] = {data["interval"]: data["time"]}
                    for chat_id in CHAT_ID:
                        send_message_to_chat(chat_id, message+"Статус 3")
                with open('status.json', 'w') as f:
                    json.dump(status, f, indent=2)
        except:
            ...


def split_list(lst:list, n:int) -> List[list]:
    chunk_size = len(lst) // n
    result = []
    for i in range(0, len(lst), chunk_size):
        result.append(lst[i:i + chunk_size])
    return result


def update_tokens() -> int:
    cookies = {
            "secure-token": "",
            "_ym_uid": "",
            'domain': '.bybit.com',
            'path': '/'
           }
    response = requests.get("https://api2.bybit.com/contract/v5/product/dynamic-symbol-list?filter=all", cookies=cookies)
    print(response.status_code)
    if response.status_code != 200:
        return False
    else:
        response = response.json()

    tokens_name = []
    for token in response["result"]["LinearPerpetual"]:
        tokens_name.append(token["symbolName"])

    with open("tokens.json", "w") as f:
        json.dump({"tokens": tokens_name}, f, indent=2)

    return len(tokens_name)
    # url = '/v5/asset/coin/query-info'
    # response = requests_bybit(url, 'GET').json()["result"]["rows"]
    # tokens_name = list(token["coin"] for token in response)

    # with open("tokens.json", "w") as f:
    #     json.dump({"tokens": tokens_name}, f, indent=2)

    # return len(tokens_name)


def update_proxie(chat_id:str=None, message_id:str=None) -> int:
    with open("proxies.json", "r") as f:
        data = json.load(f)

    new_proxie_list = []
    i=0
    for proxie in data["proxies"]:
        i+=1
        if check_proxie(proxie):
            new_proxie_list.append(proxie)
        progress = int(i/len(data["proxies"])*100)
        if message_id and chat_id:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"Прогресс {progress}%")

    with open("proxies.json", "w") as f:
        json.dump({"proxies": new_proxie_list}, f, indent=2)
    return len(new_proxie_list)


def update_config(new_info:list) -> dict:
    with open("config.json", "r") as f:
        data = json.load(f)

    data[new_info[0]] = new_info[1]

    with open("config.json", "w") as f:
        json.dump(data, f, indent=2)

    return data


def clear_status():
    with open('status.json', 'w') as f:
        json.dump({}, f, indent=2)


def start_parse():
    global INTERVAL, MIN_PERCENT, MIN_BUDGET, is_parsing
    is_parsing = True
    with lock:
        shared_resource.value = True
    while True:
        with lock:
            if not shared_resource.value:
                break

        start = time.time()
        with open('config.json', 'r') as config_file:
            config_data = json.load(config_file)
        INTERVAL = config_data['INTERVAL']
        MIN_PERCENT = config_data['MIN_PERCENT']
        MIN_BUDGET = config_data['MIN_BUDGET']

        with open("tokens.json", "r") as f:
            data_tokens = json.load(f)

        with open("proxies.json", "r") as f:
            data_proxies = json.load(f)

        tokens = data_tokens["tokens"]
        random.shuffle(tokens)

        amount_parts = len(data_proxies["proxies"])
        token_groups = split_list(tokens, amount_parts)

        pool = multiprocessing.Pool(processes=amount_parts)
        futures = []
        for i in range(amount_parts):
            this_proxie = data_proxies["proxies"][i]
            proxies = {"https": this_proxie, "http": this_proxie}
            future = pool.apply_async(run_me, (token_groups[i], proxies))
            futures.append(future)

        for future in futures:
            future.get()
        print(time.time()-start)


def stop_parse():
    global is_parsing
    is_parsing = False
    with lock:
        shared_resource.value = False


def is_number(text:str) -> bool:
    try:
        int(text)
        return True
    except ValueError:
        return False


def change_cookies(new_secure_token:str):
    with open("cookies.json", "r") as f:
        data = json.load(f)
    data["secure-token"] = new_secure_token
    with open("proxies.json", "w") as f:
        json.dump({"proxies": data}, f, indent=2)


@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    item0 = telebot.types.KeyboardButton("Добавить прокси")
    item1 = telebot.types.KeyboardButton("Проверить прокси")
    item2 = telebot.types.KeyboardButton("Очистить историю")
    item3 = telebot.types.KeyboardButton("Обновить токены")
    item4 = telebot.types.KeyboardButton("Изменить интервал")
    item5 = telebot.types.KeyboardButton("Изменить бюджет")
    item6 = telebot.types.KeyboardButton("Изменить процент")
    item7 = telebot.types.KeyboardButton("Остановить")
    item8 = telebot.types.KeyboardButton("Запустить")

    row1 = [item0, item1, item2, item3]
    row2 = [item4, item5, item6]
    row3 = [item7, item8]

    markup.row(*row1)
    markup.row(*row2)
    markup.row(*row3)
    
    bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Добавить прокси")
def add_proxie_bot(message):
    user_states[message.chat.id] = "waiting_for_text_add_proxie"
    bot.send_message(message.chat.id, "Отправьте прокси в следующем формате:\nsocks5://login:password@ip:port")

@bot.message_handler(func=lambda message: message.text == "Очистить историю")
def clear_history_bot(message):
    clear_status()
    bot.send_message(message.chat.id, "Успешно!")

@bot.message_handler(func=lambda message: message.text == "Проверить прокси")
def check_proxie_bot(message):
    bot.send_message(message.chat.id, "Это может занять несколько минут")
    this_message = bot.send_message(message.chat.id, "Прогресс 0%")
    info = update_proxie(message.chat.id, this_message.message_id)
    bot.send_message(message.chat.id, f"Кол-во прокси: {info}")

@bot.message_handler(func=lambda message: message.text == "Обновить токены")
def token_update_bot(message):
    bot.send_message(message.chat.id, "Ожидайте.")
    data = update_tokens()
    if data:
        bot.send_message(message.chat.id, f"Успешно! Кол-во токенов: {data}")
    else:
        user_states[message.chat.id] = "waiting_for_text_token_update"
        bot.send_message(message.chat.id, "Ошибка. Вставьте secure-token")

@bot.message_handler(func=lambda message: message.text == "Изменить бюджет")
def change_budget_bot(message):
    user_states[message.chat.id] = "waiting_for_text_budget"
    bot.send_message(message.chat.id, "Введите минимальный бюджет целым числом в $")

@bot.message_handler(func=lambda message: message.text == "Изменить интервал")
def change_interval_bot(message):
    user_states[message.chat.id] = "waiting_for_text_change_interval"
    bot.send_message(message.chat.id, "Введите интервал целым числом минут\nВозможные значения 1,3,5,15,30,60,120,240,360,720")

@bot.message_handler(func=lambda message: message.text == "Изменить процент")
def change_percent_bot(message):
    user_states[message.chat.id] = "waiting_for_text_change_percent"
    bot.send_message(message.chat.id, "Введите процент целым числом")

@bot.message_handler(func=lambda message: message.chat.id in user_states and 
                                  user_states[message.chat.id] in ["waiting_for_text_change_interval", 
                                                                   "waiting_for_text_change_percent",
                                                                   "waiting_for_text_token_update",
                                                                   "waiting_for_text_add_proxie",
                                                                   "waiting_for_text_budget"
                                                                   ])
def handle_text(message):
    user_state = user_states[message.chat.id]
    text = message.text
    if user_state == "waiting_for_text_change_interval":
        if is_number(text):
            interval = int(text)
            if interval in [1,3,5,15,30,60,120,240,360,720]:
                data = update_config(['INTERVAL', interval])
                bot.send_message(message.chat.id, f"Сохранено! Новые настройки:\nМинимальный процент: {data['MIN_PERCENT']}%\nМинимальный бюджет: {data['MIN_BUDGET']}$\nИнтервал: {data['INTERVAL']}м")
            else:
                bot.send_message(message.chat.id, f"Ошибка.")
        else:
            bot.send_message(message.chat.id, f"Ошибка.")

    elif user_state == "waiting_for_text_change_percent":
        if is_number(text):
            percent = int(text)
            data = update_config(['MIN_PERCENT', percent])
            bot.send_message(message.chat.id, f"Сохранено! Новые настройки:\nМинимальный процент: {data['MIN_PERCENT']}%\nМинимальный бюджет: {data['MIN_BUDGET']}$\nИнтервал: {data['INTERVAL']}м")
        else:
            bot.send_message(message.chat.id, f"Ошибка.")

    elif user_state == "waiting_for_text_budget":
        if is_number(text):
            budget = int(text)
            data = update_config(['MIN_BUDGET', budget])
            bot.send_message(message.chat.id, f"Сохранено! Новые настройки:\nМинимальный процент: {data['MIN_PERCENT']}%\nМинимальный бюджет: {data['MIN_BUDGET']}$\nИнтервал: {data['INTERVAL']}м")
        else:
            bot.send_message(message.chat.id, f"Ошибка.")

    elif user_state == "waiting_for_text_token_update":
        change_cookies(message.text)
        bot.send_message(message.chat.id, f"Сохранено! secure-token изменен. Запустите поиск токенов снова")

    elif user_state == "waiting_for_text_add_proxie":
        if add_proxie(message.text):
            bot.send_message(message.chat.id, f"Сохранено!")
        else:
            bot.send_message(message.chat.id, f"Ошибка.")

    user_states[message.chat.id] = ""

@bot.message_handler(func=lambda message: message.text == "Запустить")
def start_bot(message):
    if is_parsing:
        bot.send_message(message.chat.id, "Поиск уже запущен, остановите его.")
    else:
        bot.send_message(message.chat.id, "Поиск запущен")
        start_parse()

@bot.message_handler(func=lambda message: message.text == "Остановить")
def stop_bot(message):
    bot.send_message(message.chat.id, "Поиск остановлен")
    stop_parse()


def send_message_to_chat(chat_id, message):
    bot.send_message(chat_id, message)

if __name__ == "__main__":
    bot.polling()