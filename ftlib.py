import socket
import os
import pickle
from time import sleep


class FileServer():
    def __init__(self):
        self.pathToFile ='.'

    def FileReciver(self,dumy,dum1):
        HOST = ""
        PORT = 8000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(5)
        print("Listening ...")

        while True:
            conn, addr = s.accept()
            print("[+] Client connected: ", addr)

            # get file name to download

            while True:
                # get file bytes
                data =conn.recv(4096)
                if not data:
                    break
                data = pickle.loads(data)
                # write bytes on file
                if not os.path.exists(data['Owner']):
                    os.makedirs(data['Owner'])
                f = open((data['Owner']+'/'+data['FileName']), "wb")

                f.writelines(data['Data'])
            f.close()

    def FileSender(self, owner='me', path='.'):

        import json

        HOST = "192.168.66.56"
        PORT = 8000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        print("[+] Connected with Server")

        while True:
            # files = [f for f in os.listdir(path) if os.path.isfile(f)]
            files = os.listdir(path)
            filewather = None
            try:
                with open('filewather.json') as data_file:
                    try:
                        filewather = json.load(data_file)
                    except:
                        open('filewather.json', 'w')
                        filewatiseher = {}
            except IOError:
                open('filewather.json', 'w')

            for file in files:

                upload = True
                if 'filewather.json' == file:
                    break
                print('[*]Checkin file {}.'.format(file))
                if file in filewather.keys():
                    creationDate = os.path.getmtime((os.path.join(path, file)))
                    if filewather[file] == creationDate:
                        upload = False
                if upload :
                    with open((os.path.join(path, file)), "rb") as f:

                        # send file
                        print("[+] Sending file {}.".format(file))
                        data = f.readlines()
                        dataToSend = {}
                        dataToSend['Owner'] = owner
                        dataToSend['FileName'] = file
                        dataToSend['Data'] = data
                        s.sendall(pickle.dumps(dataToSend))
                        print("[-] Disconnected")

                    filewather[file] = os.path.getmtime((os.path.join(path, file)))
                    with open('filewather.json', 'w') as outfile:
                        json.dump(filewather, outfile)
                else:
                    sleep(2)


        s.close()