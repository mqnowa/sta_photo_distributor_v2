import platform

dic = {
    "iPad13,1": (False, True),
    "iPad13,2": (False, True),
    "iPhone9,1": (False, False),
    "iPhone9,3": (False, False),
    "iPhone9,2": (False, False),
    "iPhone9,4": (False, False)
}

notch = True
homebar = True

id = platform.machine()
if id in dic.keys():
    notch = dic[id][0]
    homebar = dic[id][1]
