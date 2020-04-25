clientssdsd = {'sock0': 'name0', 'sock1': 'name1', 'sock2': 'name2'}
client_list = [{'socket-1':{'username':'jerry', 'fullname': 'gjermund f. haugen', 'state': 0}}, {'socket-2':{'username':'tomas', 'fullname': 'tomas valen', 'state': 2}}]
# 'sock3': 'name3'
offline = ['name3']
clients = [{'socket':{'username':'jerry', 'fullname': 'gjermund f. haugen', 'state': 0}, 'socket1':{'username':'jerry1', 'fullname': 'gjermund f. haugen1', 'state': 0}, 'socket2':{'username':'jerry2', 'fullname': 'gjermund f. hauge2', 'state': 0}}]


for client in clients.values():
    if client['state'] == 0:
        print(client['state'])










data = {'head': 'login', 'body':(False,)}
print(type(data['body'][0]))
print([client['fullname'] for client in clients1.values()])

load = [client['fullname'] for client in clients1.values()]
online = [client for client in load]
print('load: ', load)
print('online: ', online)


def is_online():
    global clients, offline
    if len(offline) > 0:
        body = {'online': list(clients.values()), 'offline': offline}
        print('sent: ', {'head': 'meta', 'body': body})
        offline.clear()
