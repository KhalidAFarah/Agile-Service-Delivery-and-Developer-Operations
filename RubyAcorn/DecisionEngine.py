import os, time, requests, math
run = True



def calculated_replicas(title):
    query ="player_count{title='"+title+"'}"
    response = requests.get("http://128.39.121.239:9090/api/v1/query?query="+query).json()
    if response['status'] == "success":
        try:
            rate = int(response['data']['result'][0]['value'][1])
            #print(f"Rate: {rate}")
            return math.ceil(rate / 28989)
        except:
            return -1

#startup
replicas = calculated_replicas("Destiny 2")
if replicas != -1:
    print(f"replicas: {replicas}")
    os.system(f"docker service create --replicas={replicas} --name=application waterlevel_image:v1")

#scaling
while run:
    time.sleep(30)
    tmp = calculated_replicas("Destiny 2")
    if tmp != -1 and tmp != replicas:
        replicas = tmp
        print(f"replicas: {replicas}")
        os.system(f"docker service update --replicas={replicas} application")