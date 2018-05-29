import socket
import os
import pickle
from time import sleep, ctime
from random import randint
import json
import threading
import queue

server_name = 'ubuntu'
globvar = None

class FileServer():

    def __init__(self):
        self.pathToFile ='.'
        self.event = threading.Event()
        self.queue = queue.Queue()

    def ClienThreading(self, conn, addr):

        print('Star thread')
        print(conn, addr)

        conn.send('Ehlo'.encode())
        while True:
            # get file bytes
            data =conn.recv(4096)
            # when transmission is over then where will be no data, so we are closing connection
            if not data:
                break

            # files are sent as json files and are composed from three parts Owner
            # file name and data witch they are containing

            data = pickle.loads(data)
            print('Data recived from Client:',data)
            if len(data.keys()) == 2:
                dataToSend = {}
                # adding owner name
                owner = data['Owner']
                # adding file name
                path = '/home/konrad/FileTransfer/'
                files_to_send = []
                files = os.listdir(path + owner)
                print(files)
                for file in files:
                    with open((os.path.join(path, owner ,file)), "rb") as f:
                        tmpdic = {}
                        tmpdic['FileName'] = file
                        # adding content of file
                        # reading file
                        data = f.readlines()
                        tmpdic['Data'] = data
                        files_to_send.append(tmpdic)
                # send file
                dataToSend['Data'] = files_to_send
                print("[+] Sending file {}.".format(file))
                # using picle to convert json to binaries
                print(dataToSend)
                conn.sendall(pickle.dumps(dataToSend))
                # s.recv(4024)
                print("[-] Disconnected")
                return

            # checking is folder named like owner is existing if no then it will be created
            directory = os.path.dirname(os.path.abspath(__file__)) + '/' + data['Owner']
            if not os.path.exists(directory):
                os.makedirs(directory)
            fileName = os.path.dirname(os.path.abspath(__file__)) + '/' + (data['Owner'] + '/' + data['FileName'])
            # creating file object
            try:
                os.stat(fileName)
            except:
                file = open(fileName, "w")
            f = open(fileName, "wb")
            f.writelines(data['Data'])
            del data['Data']
            data['UploadTime'] = ctime
            with open((data['Owner']+'.json'), 'w') as outfile:
                json.dump(data, outfile)
            f.close()
        sleep((randint(1, 15)))




    def FileReciver(self, rootFolder, first=False):
        '''

        This function is responsible for receiving packages via TCP and managing communications.

        :param rootFolder: folder for keeping files

        :return: None
        '''
        host = ""
        # Parameters for server
        port = 8000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # strating server
        s.bind((host, port )) # FileReciver
        s.listen(5)

        print('Starting function FileReciver.')
        print('with parameters: ',host, port)
        print("Listening ...")

        # Main function for receiving data.
        while True:

            while True:
                # starting accepting data
                try:
                    conn, addr = s.accept()
                except:
                    pass
                print("[+] Client connected: ", addr[0])
                t = threading.Thread(target=self.ClienThreading,  args=((conn, addr)) )

                t.start()


    def FileSender(self, owner='me', path='.', host="192.168.1.62", port=8000):


        from hashlib import md5
        print('Staring function FileSender.')
        print("Parameters : ", owner, path, host, port)
        # connection parameters
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # creating connection to server
        s.connect((host, port)) # FileSender
        data =s.recv(4096)
        print(dir(data))
        print(data.decode())
        print("[+] Connected with Server")
        # main function used to checking is file are changed
        while True:
            # listing folder looking for content
            if socket.gethostname() == server_name:
                os.listdir()
                path = '/home/konrad/FileTransfer/'
                files = os.listdir(path + owner)
            else:
                files = os.listdir(path)

            if len(files) == 0:
                # data1 = s.recv(4096)
                dataToSend = {}
                tmp = open('filewather.json','w')
                tmp.close()
                dataToSend['Owner'] = owner
                dataToSend['path'] = path
                print('Send information to server:',dataToSend)
                s.sendall(pickle.dumps(dataToSend))
                while True:
                    data = s.recv(4096)
                    if data is None:
                        break
                    print(data)
                    data = pickle.loads(data)
                    if len(data['Data']) != 0:
                        for data in data['Data']:
                            f = open((path + '\\' + data['FileName']), "wb")
                            f.writelines(data['Data'])
                            f.close()
                        return self.FileSender()
            # looking throw all files with are in folder and comparing them to dictionary
            for file in files:
                # we make the assumption that file is new and try to disprove it in the next steps
                upload = True
                # creating object filewather witch will be used to keep information about file names
                # and when when there was last time modification was made
                filewather = None
                # checking is file created if not then it will be created
                try:
                    with open('filewather.json') as data_file:
                        # if there is file attempt of parsing contend is made  if it failed when new dictionary is created
                        try:
                            filewather = json.load(data_file)
                        except:
                            open('filewather.json', 'w')
                            filewatiseher = {}
                except IOError:
                    open('filewather.json', 'w')
                    filewatiseher = {}

                if 'filewather.json' == file:
                    break
                print('[*]Checkin file {}.'.format(file))
                # firs test is checking list of keys, if file is in key we proceed to next steep
                if filewather is None:
                    filewather = {}
                if file in filewather.keys():
                    filepathmd5 = os.path.abspath(os.path.join(path, file))
                    hasher = md5()
                    with open(filepathmd5, 'rb') as afile:
                        buf = afile.read()
                        hasher.update(buf)
                    creationDate = hasher.hexdigest()
                    # checking last modification of file
                    if filewather[file] == creationDate:
                        # if modification of file is that same like in dictionary we are assuming that it is old file
                        # and we won't upload it to server, so variable upload is set to False
                        upload = False
                # if file is new we are proceeding to upload proces
                if upload :
                    # we are opening it in binary read mode so we don't need to decode it in future
                    with open((os.path.join(path, file)), "rb") as f:
                        # reading file
                        data = f.readlines()
                        dataToSend = {}
                        # adding owner name
                        dataToSend['Owner'] = owner
                        # adding file name
                        dataToSend['FileName'] = file
                        # adding content of file
                        if len(data) ==0:
                            data = " ".encode()
                        dataToSend['Data'] = data
                        # send file
                        print("[+] Sending file {}.".format(file))
                        # using picle to convert json to binaries
                        print(dataToSend)
                        s.sendall(pickle.dumps(dataToSend))
                        print("[-] Disconnected")
                        sleep(( randint(1,15)))
                    # updating variable so we won't upload second time the same file
                    filepathmd5 = os.path.abspath(os.path.join(path, file))
                    hasher = md5()
                    with open(filepathmd5, 'rb') as afile:
                        buf = afile.read()
                        hasher.update(buf)
                    filewather[file] = hasher.hexdigest()
                    # updating file so after shutdown we won't upload the same files
                    with open('filewather.json', 'w') as outfile:
                        json.dump(filewather, outfile)
            else:
                # if file wasn't change we are put sleep for two seconds
                sleep(2)
