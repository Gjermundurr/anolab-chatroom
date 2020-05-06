# data1 = {'head':'login', 'body':(username, password)}
# data2 = {'head':'bcast', 'body':(username, message)}
# data3 = {'head':'dm', 'body': {dest: (source, message)}}
# data4 = {'head': 'meta', 'body': [users]}
#
test = {'name1': 'obj1', 'name2': 'obj2', 'name3': 'obj3', 'name4': 'obj4', 'name5': 'obj5', }
target = 'name2'
for x in test.items():
    if target in x:
        print(target,  x)
