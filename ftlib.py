import socket
import os
import pickle
from time import sleep


class FileServer():

    def __init__(self):
        self.pathToFile ='.'

    def FileReciver(self, rootFolder):
        '''

        This function is responsible for receiving packages via TCP and managing communications.

        :param rootFolder: folder for keeping files

        :return: None
        '''
        HOST = ""
        # Parameters for server
        PORT = 8000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # strating server
        s.bind((HOST, PORT))
        s.listen(5)

        print("Listening ...")

        # Main function for receiving data.
        while True:

            # starting accepting data
            conn, addr = s.accept()
            print("[+] Client connected: ", addr)

            # get file name to download

            while True:
                # get file bytes
                data =conn.recv(4096)
                # when transmission is over then where will be no data, so we are closing connection
                if not data:
                    break

                # files are sent as json files and are composed from three parts Owner
                # file name and data witch they are containing
                data = pickle.loads(data)
                # checking is folder named like owner is existing if no then it will be created
                if not os.path.exists(data['Owner']):
                    os.makedirs(data['Owner'])
                # creating file object
                f = open(rootFolder +(data['Owner']+'/'+data['FileName']), "wb")
                # write bytes on file,
                f.writelines(data['Data'])
            f.close()

    def FileSender(self, owner='me', path='.'):

        import json
        # connection parameters
        HOST = "192.168.66.56"
        PORT = 8000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # creating connection to server
        s.connect((HOST, PORT))
        print("[+] Connected with Server")
        # main function used to checking is file are changed
        while True:
            # listing folder looking for content
            files = os.listdir(path)
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

            # looking throw all files with are in folder and comparing them to dictionary
            for file in files:
                # we make the assumption that file is new and try to disprove it in the next steps
                upload = True
                if 'filewather.json' == file:
                    break
                print('[*]Checkin file {}.'.format(file))
                # firs test is checking list of keys, if file is in key we proceed to next steep 
                if file in filewather.keys():
                    creationDate = os.path.getmtime((os.path.join(path, file)))
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
                        dataToSend['Data'] = data
                        # send file
                        print("[+] Sending file {}.".format(file))
                        # using picle to convert json to binaries 
                        s.sendall(pickle.dumps(dataToSend))
                        print("[-] Disconnected")
                    # updating variable so we won't upload second time the same file
                    filewather[file] = os.path.getmtime((os.path.join(path, file)))
                    # updating file so after shutdown we won't upload the same files 
                    with open('filewather.json', 'w') as outfile:
                        json.dump(filewather, outfile)
                else:
                    # if file wasn't change we are put sleep for two seconds
                    sleep(2)
        # closing connection to server
        s.close()
