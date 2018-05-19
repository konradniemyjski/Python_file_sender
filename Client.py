import ftlib
import argparse

def main():
    """
    Client site script, import from main library function FileSender and it is sending files to server.

    use case
    python.exe .\Client.py Me c:\
    owner is "Me" and path is c:\

    :return: nothing
    """
    # if you want to get help just launch Client.py -h ad below message will appear :
    # 
    # python.exe .\Client.py -h
    # usage: Client.py [-h] owner path
    # 
    # Please provide user and path to folder for synchronization.
    # 
    # positional arguments:
    #   owner       Put owner of files.
    #   path        Put path to folder for synchronization,.
    # 
    # optional arguments:
    #   -h, --help  show this help message and exit

    parser = argparse.ArgumentParser(description='Please provide user and path to folder for synchronization.')
    # parameters declaration na dhelp message
    parser.add_argument('owner', type=str, help='Put owner of files.')
    parser.add_argument('path', type=str, help='Put path to folder for synchronization,.')
    # parsing parameters
    args = parser.parse_args()
    # creating instance of FileServer function
    listdir = ftlib.FileServer()
    # passing arguments and launching watcher 
    listdir.FileSender(owner=args.owner, path=args.path)



if __name__ == '__main__':

    main()

