import socket
import os
import pickle
from time import sleep
from random import randint
import json
import threading
import queue

server_name = 'ubuntu'
server_ip = "192.168.8.140"

class FileServer():

    def __init__(self):
        '''
        Initial variables.
        '''
        self.pathToFile = '.'
        self.event = threading.Event()
        self.queue = queue.Queue()

    def ClienThreading(self, conn, addr):
        """
        Main function for server is responsible for managing new clients, checking files and depends of a status
        files are send or downlad.

        :param conn: socket connection type object use for communication
        :param addr: client address
        :return: nothing
        """
        print('Star thread')
        print(conn, addr)
        # information that connection is established like in smtp
        conn.send('Ehlo'.encode())
        while True:
            # get file bytes
            data = conn.recv(4096)
            # when transmission is over then where will be no data, so we are closing connection
            if not data:
                break
            # Unpacking received json
            data = pickle.loads(data)
            print('Data recived from Client:', data)
            # If json is containg only twp keys
            if len(data.keys()) == 2:
                # Create dictionary for sending data
                dataToSend = {}
                # adding owner name
                owner = data['Owner']
                # adding file name
                path = '/home/konrad/FileTransfer/'
                # dictionary have one field wit data dataToSend['Data'] with is contain list dictionary file name
                # and data with is inside file
                files_to_send = []
                #  listing all files to send
                files = os.listdir(path + owner)
                # looping thou them
                for file in files:
                    # opening file
                    with open((os.path.join(path, owner, file)), "r") as f:
                        # temporary dictionary for transporting data
                        tmpdic = {}
                        tmpdic['FileName'] = file
                        # adding content of file
                        # reading file
                        data = f.readlines()
                        tmpdic['Data'] = data
                        # adding to list
                        files_to_send.append(tmpdic)
                # send file
                dataToSend['Data'] = files_to_send
                print("[+] Sending file {}.".format(dataToSend))
                # using picle to convert json to binaries
                print(dataToSend)
                conn.sendall(pickle.dumps(dataToSend))
                conn.send('end'.encode())
                # s.recv(4024)
                print("[-] Disconnected")
                # exiting thread
                return None
            # loading json file contains information about local files and when they where created.
            try:
                with open(data['Owner'] +'.json') as data_file:
                    data_item = json.load(data_file)
            except :
                data_item = {}
            print(data_item)
            # checking is folder named like owner is existing if no then it will be created
            directory = os.path.dirname(os.path.abspath(__file__)) + '/' + data['Owner']
            if not os.path.exists(directory):
                os.makedirs(directory)
            # checking if file is new or it have already bean on the server if it is new file creation time is set to 0
            # if not then information from local file are keep in data_item
            print("keys: {} |||||| data['FileName'] ".format(data_item.keys(),data['FileName']))
            if data['FileName'] not in data_item.keys() :
                data_item[data['FileName']] = float(0)
            print(data_item)
            # comparing local information and received from client
            # if isinstance(data_item, dict):
            #     data_item = data_item[data['FileName']]

            if data_item[data['FileName']] <= data['Creation_date']:
                # making full file name path for writing purposes
                fileName = os.path.dirname(os.path.abspath(__file__)) + '/' + (data['Owner'] + '/' + data['FileName'])
                # creating file object
                try:
                    os.stat(fileName)
                except:
                    file = open(fileName, "w")
                    file.close()
                f = open(fileName, "w")
                # write data to file
                f.writelines(data['Data'])
                # removing data from json file, i don't need it anny more
                del data['Data']
                # closing file connection
                f.close()
                print("File {} is saved".format(fileName))
                # writing data to json file about our new file
                with open((data['Owner'] + '.json'), 'w') as outfile:
                    # removing old data
                    data_item_info = {}
                    data_item_info[data['FileName']] = data_item
                    #  creating object to write
                    data_from_clent = {}
                    #  adding data to it
                    data_from_clent[data['FileName']] = data['Creation_date']
                    # combing two dictionaries previous and new one.
                    print('136',data_from_clent, data_item)
                    json_to_write = {**data_from_clent, **data_item}
                    # writing to file
                    json.dump(json_to_write, outfile)
                print("Staring waiting for next file.")
            else:
                # on the server is newer version of file send information to client about it
                conn.send('Sending'.encode())
                # constructing full file name so we can use it to open file
                file = os.path.dirname(os.path.abspath(__file__))+data['Owner']+'/'+data['FileName']
                # creating variable to send data
                dataToSend = {}
                with open(file, "r") as f:
                    # adding content of file
                    data_to_client = f.readlines()
                # combing and sending information to client
                dataToSend[data['FileName']] = data_to_client
                conn.sendall(pickle.dumps(dataToSend))
            # communicating to client that files are proceed
            conn.send('Next'.encode())

    def FileReciver(self, ):
        '''

        This function is responsible for receiving packages via TCP and managing communications. For every new
        connection new thread is created and function self.ClienThreading is launched with arguments conn, addr.

        :param rootFolder: folder for keeping files

        :return: None
        '''
        host = ""
        # Parameters for server
        port = 8000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # strating server
        s.bind((host, port))  # FileReciver
        s.listen(5)
        # printing basic information
        print('Starting function FileReciver.')
        print('with parameters: ', host, port)
        print("Listening ...")

        # Main function for receiving data.
        while True:
            # starting accepting data
            try:
                conn, addr = s.accept()
            except:
                pass
            print("[+] Client connected: ", addr[0])
            # Starting new thread for every new client
            t = threading.Thread(target=self.ClienThreading, args=((conn, addr)))
            # launching new thread
            t.start()

    def FileUploadToServer(self,path, file, owner, s):
        '''

        Purpose of this function is to create object with is use for multi threding

        :param path: path of file to send
        :param file: file name to send
        :param owner: who is sendind this data
        :param s: connection parameter
        :return: nothing
        '''
        # we are opening it in  read mode so we don't need to decode it in future
        with open((os.path.join(path, file)), "r") as f:
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
            dataToSend['Creation_date'] = os.path.getctime((os.path.join(path, file)))
            # printing received data for debug purpose
            print(dataToSend)
            # sendind compress data
            s.sendall(pickle.dumps(dataToSend))
            # declaration of new variable
            wait_for_data = False
        # loop for sending data to server
        while True:
            data = s.recv(4096)
            # when then is no data stop listening
            if data is None:
                break
            # if wait_for_data is true that means that on server is never version of file so write procedure
            # is beginning
            if wait_for_data:
                data = pickle.loads(data)
                with open((os.path.join(path, file)), "w") as f:
                    f.writelines(data['Data'])
                break
            # receiving importation fro server to receive never version of current file or proceed to next
            if data.decode() == 'Sending':
                wait_for_data = True
            elif data.decode() == 'Next':
                break
        # printing information that current precede of file is done
        print("[-] Disconnected")
        #  imitating file sending, random number for 1 to 15 is selecting ant putting ito sleep function parameter
        # for second
        sleep(randint(1,15))

    def FileSender(self, owner='me', path='.', host=server_ip, port=8000):
        # importing md5 algorithm
        from hashlib import md5
        # printing basic information
        print('Staring function FileSender.')
        print("Parameters : ", owner, path, host, port)
        # connection parameters
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # creating connection to server
        s.connect((host, port))  # FileSender
        data = s.recv(4096)
        print(data.decode())
        print("[+] Connected with Server")
        # main function used to checking is file are changed
        while True:
            # listing folder looking for content
            files = os.listdir(path)
            # if len of file is equal to zero, client is checking does the server have anny fi;es
            if len(files) == 0:
                # declaration of variable
                dataToSend = {}
                tmp = open('filewather.json', 'w')
                tmp.close()
                # adding information who ane where to send files
                dataToSend['Owner'] = owner
                dataToSend['path'] = path
                print('Send information to server:', dataToSend)
                # sending data to server
                s.sendall(pickle.dumps(dataToSend))
                # receiving data from server
                while True:
                    data = s.recv(4096)
                    if data is None:
                        break
                    # printing recived data fo troubleshooting purposes
                    print(pickle.loads(data))
                    try:
                        # if data received from server is equal to end  function FileSender is called
                        if data.decode() == 'end':
                            return self.FileSender()
                    except:
                        pass
                    # decoding data
                    data = pickle.loads(data)
                    # if anny file is received writing process is started
                    if len(data['Data']) != 0:
                        for data in data['Data']:
                            f = open((path + '\\' + data['FileName']), "w")
                            f.writelines(data['Data'])
                            f.close()
                    return self.FileSender(owner='Konrad', path='client_folder', host=server_ip, port=8000)

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
                    break
                print('[*] Checkin file {}.'.format(file))
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
                # if file is new we are proceeding to upload process
                if upload:
                    # staring new thred for new file
                    t = threading.Thread(target=self.FileUploadToServer, args=(path, file, owner, s))
                    # printing debug informatics about new thread 
                    print(t)
                    # launching new thread
                    t.start()
                    #  random sleep time is generating 
                    sleep(randint(1,15))
                    # appending inflation files valus for new files
                    filepathmd5 = os.path.abspath(os.path.join(path, file))
                    #  creating hash file function
                    hasher = md5()
                    with open(filepathmd5, 'rb') as afile:
                        buf = afile.read()
                        hasher.update(buf)
                    filewather[file] = hasher.hexdigest()
                    # updating file so after shutdown we won't upload the same files
                    with open('filewather.json', 'w') as outfile:
                        print()
                        json.dump(filewather, outfile)
