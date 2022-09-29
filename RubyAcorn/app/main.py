from prometheus_client import start_http_server, Gauge
import requests
import time

concurrentDestiny2Players = Gauge('player_count', 'Player count', ["title", "publisher"])

def gatherConcurrentPlayers():
    try:
        response = requests.get("https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?format=json&appid=1085660").json()
        concurrentDestiny2Players.labels(title="Destiny 2", publisher="Bungie").set(response['response']['player_count'])
    except:
	    print("Unable to log player numbers!")

if __name__ == "__main__":
    start_http_server(8000)
    while True:
        time.sleep(15)
        gatherConcurrentPlayers()