import requests, json, time
from main import split_list

INTERVAL = 5
MIN_PERCENT = 100

def find_liguidity(symbol_token:str, proxies:dict):
    url = '/derivatives/v3/public/kline'
    now_time = time.time()
    query_param = f"interval={INTERVAL}&symbol={symbol_token}&limit=2&start={int((now_time-INTERVAL*2*60+1)*1000)}&end={int((now_time)*1000)}"
    response = requests.get("https://api.bybit.com"+url+"?"+query_param, proxies=proxies).json()["result"]
    if "list" in response:
        start = float(response["list"][0][6])
        end = float(response["list"][1][6])
        time_p = int(response["list"][0][0][:-3])

        if start != 0 and end != 0:
            percent = start/end*100
            print(percent)
            if percent > MIN_PERCENT:
                return {"symbol": symbol_token, "percent": round(percent, 2), "interval": str(INTERVAL), "time": time_p}
    return False


with open("tokens.json", "r") as f:
    data_tokens = json.load(f)

with open("proxies.json", "r") as f:
    data_proxies = json.load(f)

amount_parts = len(data_proxies["proxies"])
token_groups = split_list(data_tokens["tokens"], amount_parts)

for i in range(amount_parts):
    this_proxie = data_proxies["proxies"][i]
    proxies = {"https": this_proxie, "http": this_proxie}
    for token in token_groups[i]:
        find_liguidity(token, proxies)