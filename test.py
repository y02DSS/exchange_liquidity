import requests, datetime

symbol_token = "XEMUSDT"

INTERVAL = 15
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
response = requests.get("https://api.bybit.com"+url+"?"+query_param).json()["result"]
print(response)








    # "socks5://sC3G57:PGX3jb@168.196.237.197:9970",
    # "socks5://sC3G57:PGX3jb@168.196.239.75:9580",
    # "socks5://sC3G57:PGX3jb@38.170.254.142:9246",
    # "socks5://sC3G57:PGX3jb@168.196.237.233:9462",
    # "socks5://sC3G57:PGX3jb@38.170.124.161:9950",
    # "socks5://sC3G57:PGX3jb@168.196.238.168:9855",
    # "socks5://sC3G57:PGX3jb@168.196.239.236:9792",
    # "socks5://sC3G57:PGX3jb@168.196.239.3:9367",
    # "socks5://sC3G57:PGX3jb@38.170.121.27:9361",
    # "socks5://sC3G57:PGX3jb@38.170.104.106:9094",
    # "socks5://sC3G57:PGX3jb@38.170.254.97:9976",
    # "socks5://sC3G57:PGX3jb@38.170.124.124:9922",
    # "socks5://sC3G57:PGX3jb@38.170.104.104:9150",
    # "socks5://sC3G57:PGX3jb@168.196.237.147:9226",
    # "socks5://sC3G57:PGX3jb@38.170.121.195:9070",
    # "socks5://sC3G57:PGX3jb@38.170.253.226:9282",
    # "socks5://sC3G57:PGX3jb@200.71.126.208:9403",
    # "socks5://sC3G57:PGX3jb@38.170.254.168:9738",
    # "socks5://sC3G57:PGX3jb@38.170.252.155:9750",
    # "socks5://sC3G57:PGX3jb@168.196.237.210:9200",
    # "socks5://sC3G57:PGX3jb@168.196.238.4:9912",
    # "socks5://sC3G57:PGX3jb@168.196.239.53:9736",
    # "socks5://sC3G57:PGX3jb@38.170.124.12:9669",
    # "socks5://sC3G57:PGX3jb@38.170.102.248:9246",
    # "socks5://sC3G57:PGX3jb@38.170.124.72:9979",
    # "socks5://sC3G57:PGX3jb@38.170.102.161:9339",
    # "socks5://sC3G57:PGX3jb@38.170.253.237:9698",
    # "socks5://sC3G57:PGX3jb@38.170.124.93:9755",
    # "socks5://sC3G57:PGX3jb@38.170.104.49:9516",
    # "socks5://sC3G57:PGX3jb@38.170.121.188:9696",
    # "socks5://sC3G57:PGX3jb@168.196.237.254:9440",
    # "socks5://sC3G57:PGX3jb@200.71.126.29:9849",
    # "socks5://sC3G57:PGX3jb@38.170.102.225:9942",
    # "socks5://sC3G57:PGX3jb@38.170.124.150:9771",
    # "socks5://sC3G57:PGX3jb@168.196.239.157:9742",
    # "socks5://sC3G57:PGX3jb@38.170.102.204:9370",
    # "socks5://sC3G57:PGX3jb@38.170.255.4:9036",
    # "socks5://sC3G57:PGX3jb@38.170.254.176:9359",
    # "socks5://sC3G57:PGX3jb@38.170.252.46:9338",
    # "socks5://sC3G57:PGX3jb@138.99.37.137:9674",
    # "socks5://sC3G57:PGX3jb@38.170.104.169:9038",
    # "socks5://sC3G57:PGX3jb@38.170.253.158:9087",
    # "socks5://sC3G57:PGX3jb@200.71.127.223:9832",
    # "socks5://sC3G57:PGX3jb@38.170.124.210:9878",
    # "socks5://sC3G57:PGX3jb@168.196.237.21:9494",
    # "socks5://sC3G57:PGX3jb@200.71.126.191:9898",
    # "socks5://sC3G57:PGX3jb@38.170.104.14:9455",
    # "socks5://sC3G57:PGX3jb@200.71.126.54:9347",
    # "socks5://sC3G57:PGX3jb@38.170.102.107:9596",
    # "socks5://sC3G57:PGX3jb@200.71.127.253:9316",
    # "socks5://sC3G57:PGX3jb@168.196.239.162:9096",
    # "socks5://sC3G57:PGX3jb@168.196.238.136:9687",
    # "socks5://sC3G57:PGX3jb@38.170.121.252:9748",
    # "socks5://sC3G57:PGX3jb@38.170.252.97:9190",
    # "socks5://sC3G57:PGX3jb@38.170.121.156:9672",
    # "socks5://sC3G57:PGX3jb@38.170.255.207:9501",
    # "socks5://sC3G57:PGX3jb@168.196.239.37:9560",
    # "socks5://sC3G57:PGX3jb@168.196.239.15:9120",
    # "socks5://sC3G57:PGX3jb@38.170.255.107:9820",
    # "socks5://sC3G57:PGX3jb@200.71.126.53:9976",
    # "socks5://sC3G57:PGX3jb@38.170.253.200:9406",
    # "socks5://sC3G57:PGX3jb@168.196.239.101:9466",
    # "socks5://sC3G57:PGX3jb@168.196.237.141:9840",
    # "socks5://sC3G57:PGX3jb@168.196.239.27:9898",
    # "socks5://sC3G57:PGX3jb@168.196.239.107:9781",
    # "socks5://sC3G57:PGX3jb@38.170.255.11:9956",
    # "socks5://sC3G57:PGX3jb@38.170.255.66:9700",
    # "socks5://MkSLXr:8sM1E2@38.170.253.152:9185",
    # "socks5://sC3G57:PGX3jb@168.196.237.157:9332",
    # "socks5://sC3G57:PGX3jb@168.196.238.198:9551",
    # "socks5://A5qzSP:q7wU1x@185.59.232.224:8000",
    # "socks5://sC3G57:PGX3jb@190.185.108.78:9141",
    # "socks5://sC3G57:PGX3jb@38.170.104.140:9232",
    # "socks5://sC3G57:PGX3jb@38.170.252.168:9206",
    # "socks5://sC3G57:PGX3jb@38.170.121.57:9082",
    # "socks5://sC3G57:PGX3jb@168.196.239.242:9454",
    # "socks5://sC3G57:PGX3jb@38.170.255.99:9151",
    # "socks5://sC3G57:PGX3jb@38.170.255.197:9822",
    # "socks5://sC3G57:PGX3jb@38.170.124.220:9723",
    # "socks5://sC3G57:PGX3jb@38.170.252.244:9742",
    # "socks5://sC3G57:PGX3jb@38.170.124.239:9461",
    # "socks5://sC3G57:PGX3jb@38.170.102.254:9249",
    # "socks5://sC3G57:PGX3jb@168.196.237.58:9700",
    # "socks5://sC3G57:PGX3jb@38.170.102.17:9759",
    # "socks5://sC3G57:PGX3jb@38.170.255.227:9362",
    # "socks5://sC3G57:PGX3jb@38.170.124.82:9989",
    # "socks5://sC3G57:PGX3jb@168.196.238.26:9340"
    #  "socks5://sC3G57:PGX3jb@168.196.239.75:9580",
    # "socks5://sC3G57:PGX3jb@38.170.254.142:9246",
    # "socks5://sC3G57:PGX3jb@168.196.237.233:9462",
    # "socks5://sC3G57:PGX3jb@38.170.124.161:9950",
    # "socks5://sC3G57:PGX3jb@168.196.238.168:9855",
    # "socks5://sC3G57:PGX3jb@168.196.239.236:9792",
    # "socks5://sC3G57:PGX3jb@168.196.239.3:9367",
    # "socks5://sC3G57:PGX3jb@38.170.121.27:9361"