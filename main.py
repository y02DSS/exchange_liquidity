import multiprocessing, requests, json, requests, hashlib, hmac, datetime, random, time
from typing import List, Dict
import telebot

CHAT_ID = [450919685, 572212271, 480002023]
allowed_users = ["DSSGF", "AleksandrIvanov90", "Ivan404i"]
bot = telebot.TeleBot('6981586587:AAGWGA3W6pyu-c7xrynnTtzr-zx3gK7g5BE')
user_states = {}

shared_resource = multiprocessing.Value('i', True)
lock = multiprocessing.Lock()
is_parsing = False
limit = 10


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
    previous_interval_time = last_interval_time - datetime.timedelta(minutes=INTERVAL* limit)

    previous_last_interval_time = last_interval_time.replace(second=0)
    previous_interval_time = previous_interval_time.replace(second=0)

    start_time = previous_interval_time.timestamp()
    end_time = previous_last_interval_time.timestamp()

    url = '/v5/market/kline'
    query_param = f"category=linear&interval={INTERVAL}&symbol={symbol_token}&limit={limit}&start={int(start_time*1000)}&end={int(end_time*1000)}"
    response = requests.get("https://api.bybit.com"+url+"?"+query_param, proxies=proxies).json()["result"]

    amount_interval = 0
    temp_status = "Шорт" if float(response["list"][0][4]) < float(response["list"][1][4]) else "Лонг"
    for i in range(len(response["list"])-1):
        type_status = "Шорт" if float(response["list"][i][4]) < float(response["list"][i+1][4]) else "Лонг"
        if temp_status != type_status:
            break
        amount_interval += 1    

    if amount_interval <= 3: 
        return False

    now_percent_volume = False
    dinamic_volume = ""
    n_i = []
    time_p = False
    for i in reversed(range(len(response["list"][:amount_interval]))):
        start = float(response["list"][i][5])
        end = float(response["list"][i+1][5])
        budget = float(response["list"][i+1][6])

        if i == 0:
            end_price = float(response["list"][i][4])

        if start != 0 and end != 0 and budget > MIN_BUDGET:
            percent_volume = start/end*100

            if start > end:
                dinamic_volume += "⬆️"
            else:
                dinamic_volume += "⬇️"
            
            if not now_percent_volume:
                if percent_volume > MIN_PERCENT:
                    time_p = int(response["list"][i][0][:-3])
                    now_percent_volume = percent_volume
                    n_i = []
                    dinamic_volume = ""
                    start_price = float(response["list"][i][1])

            if percent_volume < NEXT_PERCENT:
                now_percent_volume = False
                n_i = []
                dinamic_volume = ""
                start_price = float(response["list"][i][1])
                continue
            
            if n_i:
                if n_i[-1] - 1 != i:
                    n_i = []
                    dinamic_volume = ""
                    start_price = float(response["list"][i][1])
                    continue

            n_i.append(i)

    response_info = requests.get(f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol_token}", proxies=proxies).json()['result']
    if "list" in response_info:
        fundingRate = round(float(response_info['list'][0]['fundingRate'])*100, 4)
        nextFundingTime = datetime.datetime.fromtimestamp(int(response_info['list'][0]['nextFundingTime'])/1000)
        delta_funding_time = round((nextFundingTime - current_time).total_seconds() / 60)
        volume24h = format_number(int(float(response_info['list'][0]['volume24h'])))

        if abs(fundingRate) < FUNDINGRATE:
            return False

        with open("funding.json", "r") as f:
            data = json.load(f)

        if data[symbol_token]["price"] == 0:
            data[symbol_token]["price"] = end_price

        if data[symbol_token]["fg"] == 0:
            data[symbol_token]["fg"] = fundingRate

        elif data[symbol_token]["fg"] != fundingRate:
            flag = True
            # if FUNDINGRATE >= 0:
            #     if fundingRate > FUNDINGRATE:
            #         flag = True
            # else:
            #     if fundingRate < FUNDINGRATE:
            #         flag = True

            if flag:
                change_fundingRate = round(abs(abs(data[symbol_token]["fg"]) - abs(fundingRate)), 4)
                change_fundingRate_price = round(abs(abs(data[symbol_token]["price"]) - abs(end_price)), 4)

                if data[symbol_token]["fg"] < fundingRate:
                    direction_funding = "⬆️"
                else:
                    direction_funding = "⬇️"

                if data[symbol_token]["price"] < end_price:
                    direction_price = "🟢"
                else:
                    direction_price = "🔴"
      
                if change_fundingRate > 0.05:
                    for chat_id in CHAT_ID:
                        send_message_to_chat(chat_id, f"{symbol_token}, {end_price}$\n\
Фг: {fundingRate}% ({delta_funding_time//60}ч.{delta_funding_time%60}м.)\n\
{direction_funding} на {change_fundingRate}%\n\
{direction_price} на {change_fundingRate_price}%")

                    data[symbol_token]["fg"] = fundingRate
                    data[symbol_token]["price"] = end_price

        with open("funding.json", "w") as f:
            json.dump(data, f, indent=2)

    if len(n_i) >= 3 and time_p and now_percent_volume:
        if n_i[-1] == 0 and n_i[-2] == 1 and n_i[-3] == 2:
            return {
                "symbol": symbol_token, 
                "percent_volume": round(now_percent_volume, 2), 
                "dinamic_volume": dinamic_volume,
                "percent_price": round(abs(end_price/start_price*100-100), 2),
                "interval": str(INTERVAL), 
                "type_status": temp_status, 
                "time": time_p, 
                "amount_repeat": len(n_i),
                "fundingRate": fundingRate,
                "nextFundingTime": delta_funding_time,
                "end_price": end_price,
                "volume24h": volume24h,
            }
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
                
                if data["time"] != status[data["symbol"]][data["interval"]]:
                    status[data["symbol"]][data["interval"]] = data["time"]

                    if data['type_status'] == "Шорт":
                        message_status = "🔴"
                    else:
                        message_status = "🟢"

                    crit_funding = ""
                    if data['fundingRate'] < FUNDINGRATE_CRIT:
                        crit_funding = "🔥🔥🔥"

                    message = f"{data['symbol']} {data['interval']}м {data['end_price']}$\n\
                                📊{data['dinamic_volume']} на {data['percent_volume']}%\n\
                                {message_status} на {data['percent_price']}%\n\
                                Фг: {data['fundingRate']}% ({data['nextFundingTime']//60}ч.{data['nextFundingTime']%60}м.)\n\
                                Vol24: {data['volume24h']}$\n{crit_funding}"

                    for chat_id in CHAT_ID:
                        send_message_to_chat(chat_id, "\n".join(line.strip() for line in message.split("\n")))

                with open('status.json', 'w') as f:
                    json.dump(status, f, indent=2)
        except Exception as e:
            print(e)


def split_list(lst:list, n:int) -> List[list]:
    chunk_size = len(lst) // n
    result = []
    for i in range(0, len(lst), chunk_size):
        result.append(lst[i:i + chunk_size])
    return result


def format_number(number: int) -> str:
    return f"{number:,}"


def update_tokens() -> int:
    response = requests.get("https://api.bybit.com/v5/market/tickers?category=linear")
    if response.status_code != 200:
        return False
    else:
        response = response.json()
    
    tokens_name = []
    tokens_for_funding = {}
    tokens_status = {}
    for i in response["result"]["list"]:
        if i["symbol"].endswith("USDT"):
            tokens_name.append(i["symbol"])
            tokens_for_funding[i["symbol"]] = {}
            tokens_for_funding[i["symbol"]]["fg"] = 0
            tokens_for_funding[i["symbol"]]["price"] = 0
            tokens_status[i["symbol"]] = {str(item): 0 for item in [1,3,5,15,30,60,120,240,360,720]}

    with open("status.json", "w") as f:
        json.dump(tokens_status, f, indent=2)

    with open("tokens.json", "w") as f:
        json.dump({"tokens": tokens_name}, f, indent=2)

    with open("funding.json", "w") as f:
        json.dump(tokens_for_funding, f, indent=2)

    return len(tokens_name)


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


def start_parse():
    global INTERVAL, MIN_PERCENT, MIN_BUDGET, FUNDINGRATE, FUNDINGRATE_CRIT, NEXT_PERCENT, is_parsing
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
        FUNDINGRATE = config_data['FUNDINGRATE']
        NEXT_PERCENT = config_data['NEXT_PERCENT']
        FUNDINGRATE_CRIT = config_data['FUNDINGRATE_CRIT']

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


def is_float(text:str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False


def change_cookies(new_secure_token:str):
    with open("cookies.json", "r") as f:
        data = json.load(f)
    data["secure-token"] = new_secure_token
    with open("proxies.json", "w") as f:
        json.dump({"proxies": data}, f, indent=2)


@bot.message_handler(func=lambda message: message.chat.username not in allowed_users)
def restrict_access(message):
    bot.send_message(message.chat.id, "Извините, у вас нет доступа к этому боту.")


@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    item1 = telebot.types.KeyboardButton("Добавить прокси")
    item2 = telebot.types.KeyboardButton("Проверить прокси")
    item3 = telebot.types.KeyboardButton("Обновить токены")

    item4 = telebot.types.KeyboardButton("Изменить интервал")
    item5 = telebot.types.KeyboardButton("Изменить бюджет")
    item6 = telebot.types.KeyboardButton("Изменить ставку")
    item7 = telebot.types.KeyboardButton("Изменить крит. ставку")

    item8 = telebot.types.KeyboardButton("Изменить процент")
    item9 = telebot.types.KeyboardButton("Изменить второй процент")

    item10 = telebot.types.KeyboardButton("Остановить")
    item11 = telebot.types.KeyboardButton("Запустить")

    markup.row(*[item1, item2, item3])
    markup.row(*[item4, item5, item6, item7])
    markup.row(*[item8, item9])
    markup.row(*[item10, item11])
    
    bot.send_message(message.chat.id, "Выберите опцию:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Добавить прокси")
def add_proxie_bot(message):
    user_states[message.chat.id] = "waiting_for_text_add_proxie"
    bot.send_message(message.chat.id, "Отправьте прокси в следующем формате:\nsocks5://login:password@ip:port")

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

@bot.message_handler(func=lambda message: message.text == "Изменить второй процент")
def change_percent_2_bot(message):
    user_states[message.chat.id] = "waiting_for_text_change_next_percent"
    bot.send_message(message.chat.id, "Введите процент целым числом")

@bot.message_handler(func=lambda message: message.text == "Изменить ставку")
def change_fundingRate_bot(message):
    user_states[message.chat.id] = "waiting_for_text_change_fundingRate"
    bot.send_message(message.chat.id, "Введите изменение ставки дробным числом (десятичную часть через точку)")


@bot.message_handler(func=lambda message: message.text == "Изменить крит. ставку")
def change_crit_fundingRate_bot(message):
    user_states[message.chat.id] = "waiting_for_text_change_crit_fundingRate"
    bot.send_message(message.chat.id, "Введите изменение ставки дробным числом (десятичную часть через точку)")

@bot.message_handler(func=lambda message: message.chat.id in user_states and 
                                  user_states[message.chat.id] in ["waiting_for_text_change_interval", 
                                                                   "waiting_for_text_change_percent",
                                                                   "waiting_for_text_change_next_percent",
                                                                   "waiting_for_text_add_proxie",
                                                                   "waiting_for_text_budget",
                                                                   "waiting_for_text_change_fundingRate",
                                                                   "waiting_for_text_change_crit_fundingRate"
                                                                   ])
def handle_text(message):
    user_state = user_states[message.chat.id]
    text = message.text
    if user_state == "waiting_for_text_change_interval":
        if is_number(text):
            interval = int(text)
            if interval in [1,3,5,15,30,60,120,240,360,720]:
                data = update_config(['INTERVAL', interval])
                send_info_config(message.chat.id, data)
            else:
                bot.send_message(message.chat.id, f"Ошибка.")
        else:
            bot.send_message(message.chat.id, f"Ошибка.")

    elif user_state == "waiting_for_text_change_percent":
        if is_number(text):
            data = update_config(['MIN_PERCENT', int(text)])
            send_info_config(message.chat.id, data)
        else:
            bot.send_message(message.chat.id, f"Ошибка.")

    elif user_state == "waiting_for_text_change_next_percent":
        if is_number(text):
            data = update_config(['NEXT_PERCENT', int(text)])
            send_info_config(message.chat.id, data)
        else:
            bot.send_message(message.chat.id, f"Ошибка.")

    elif user_state == "waiting_for_text_budget":
        if is_number(text):
            data = update_config(['MIN_BUDGET', int(text)])
            send_info_config(message.chat.id, data)
        else:
            bot.send_message(message.chat.id, f"Ошибка.")

    elif user_state == "waiting_for_text_change_fundingRate":
        if is_float(text):
            data = update_config(['FUNDINGRATE', float(text)])
            send_info_config(message.chat.id, data)
        else:
            bot.send_message(message.chat.id, f"Ошибка.")

    elif user_state == "waiting_for_text_change_crit_fundingRate":
        if is_float(text):
            data = update_config(['FUNDINGRATE_CRIT', float(text)])
            send_info_config(message.chat.id, data)
        else:
            bot.send_message(message.chat.id, f"Ошибка.")

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

def send_info_config(chat_id, data):
    message = f"Сохранено! Новые настройки:\n\
                Минимальный процент: {data['MIN_PERCENT']}%\n\
                Второй процент: {data['NEXT_PERCENT']}%\n\
                Минимальный бюджет: {data['MIN_BUDGET']}$\n\
                Интервал: {data['INTERVAL']}м\n\
                Изменение ставки на: {data['FUNDINGRATE']}%\n"
    send_message_to_chat(chat_id, "\n".join(line.strip() for line in message.split("\n")))

if __name__ == "__main__":
    while True:
        try:
            bot.polling(non_stop=True, interval=0)
            start_parse()
        except Exception as e:
            print(e)
            time.sleep(5)
            continue