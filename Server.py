import ftlib

server = ftlib.FileServer()

if __name__ == '__main__':
    while True:
        try:
            server.FileReciver()
        except:
            pass