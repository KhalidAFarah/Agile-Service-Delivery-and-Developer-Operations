import os, time, requests, datetime
run = True


def reactive_rate(title):
    query ="player_count{title='"+title+"'}"
    response = requests.get("http://128.39.121.239:9090/api/v1/query?query="+query).json()
    if response['status'] == "success":
        try:
            return int(response['data']['result'][0]['value'][1])
        except:
            return -1


def proactive_rate(title):
    #Getting the rate for the past 4 days
    weight = [0.40, 0.30, 0.20, 0.10]

    weighted_rate = 0
    
    
    today = datetime.datetime.today()
    for i in range(len(weight)):
        timestamp = today - datetime.timedelta(days=i, minutes=(-1)).strftime("%Y-%d-%mT%H:%M:%S") # days before today and a minute ahead each day.
        query ="player_count{title='"+title+"'}" # need to the timestamp
        response = requests.get(f"http://128.39.121.239:9090/api/v1/query?query={query}&start={timestamp}&end={timestamp}").json()
        if response['status'] == "success":
            try:
                weighted_rate += weight[i]*float(response['data']['result'][0]['values'][0][1])
            except:
                pass


def calculated_replicas(title):
    reactive_rate_value = reactive_rate(title)
    proactive_rate_value = proactive_rate(title)

    reactive_replicas = (round(reactive_rate_value/29231) + 1)
    proactive_replicas = (round(proactive_rate_value/29231) + 1)



    if reactive_replicas > proactive_replicas:
        return reactive_replicas, proactive_replicas, reactive_replicas
    else:
        return reactive_replicas, proactive_replicas, proactive_replicas


#startup
reactive_replicas, proactive_replicas, hybrid_replicas = calculated_replicas("Destiny 2")

print(f"Reactive replicas: {reactive_replicas}")
print(f"Proactive replicas: {proactive_replicas}")
print(f"Hybrid replicas: {hybrid_replicas}")

os.system(f"docker service create --replicas={reactive_replicas} --name=application-reactive waterlevel_image:v1")
os.system(f"docker service create --replicas={proactive_replicas} --name=application-proactive waterlevel_image:v1")
os.system(f"docker service create --replicas={hybrid_replicas} --name=application-hybrid waterlevel_image:v1")

#scaling
while run:
    time.sleep(30)
    tmp_reactive, tmp_proactive, tmp_hybrid = calculated_replicas("Destiny 2")


    if tmp_reactive != -1 and tmp_reactive != reactive_replicas:
        reactive_replicas = tmp_reactive
        print(f"Reactive replicas: {reactive_replicas}")
        os.system(f"docker service update --replicas={reactive_replicas} application-reactive")

    if tmp_proactive != -1 and tmp_proactive != proactive_replicas:
        proactive_replicas = tmp_proactive
        print(f"Proactive replicas: {proactive_replicas}")
        os.system(f"docker service update --replicas={proactive_replicas} application-proactive")


    if tmp_hybrid != -1 and tmp_hybrid != hybrid_replicas:
        hybrid_replicas = tmp_hybrid
        print(f"Hybrid replicas: {hybrid_replicas}")
        os.system(f"docker service update --replicas={hybrid_replicas} application-hybrid")
