import sys
import dialogs

def print(*arg, end='\n', alert=True):
    for a in arg:
        sys.stdout.write(str(a) + ' ')
    if alert:
        dialogs.hud_alert(arg[0])
    sys.stdout.write(end)

if __name__ == '__main__':
    print('a')
