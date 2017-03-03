from pympg.pympg import pympg
from time import sleep

def main():
    m = pympg()
    p = '/home/tim/Music/Twenty One Pilots - Vessel (2013)/04_-_House_of_Gold.mp3'
    m.playfile(p)

    sleep(3)
    m.pause()
    print(m._title)

    try:
        input('Wait for call, press enter to exit')
    except (SyntaxError, EOFError, KeyboardInterrupt):
        pass

if __name__ == '__main__':
    main()
