import sys
import getopt
from server import server_loop
from client import client_sender


def usage():
    print("<<<<---BHP Net Tool--->>>>\n")
    print("Usage: bhpnet.py -t target_host -p port")
    print("-l --listen              - listen on [host]:[port] for ibhpoming connections")
    print("-e --execute=file_to_run - execute the given file upon receiving a connection")
    print("-c --command             - initializing a command shell")
    print("-u --upload=destination  - upon receiving connection upload a file and write to [destination]")
    print("\n")
    print("Examples: ")
    print("bhp.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhp.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe")
    print("bhp.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDE' | ./bhp.py -t 192.168.11.12 -p 135")
    sys.exit(0)

def parse_argv():
    configuration = {
        "listen": False,
        "command": False,
        "execute": "",
        "target": "",
        "upload_destination": "",
        "port": 0,
    }

    # read the commandline options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hle:t:p:cu', ["help", "listen", "execute", "target", "port", "command", "upload"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            configuration["listen"] = True
        elif o in ("-e", "--execute"):
            configuration["execute"] = a
        elif o in ("-c", "--commandshell"):
            configuration["command"] = True
        elif o in ("-u", "--upload"):
            configuration["upload_destination"] = a
        elif o in ("-t", "--target"):
            configuration["target"] = a
        elif o in ("-p", "--port"):
            configuration["port"] = int(a)
        else:
            assert False, "Unhandled Option"

    return configuration

def main():

    if not len(sys.argv[1:]):
        usage()

    configuration = parse_argv()

    # Are we going to listen or just send data from stdin?
    if not configuration["listen"] and len(configuration["target"]) and configuration["port"] > 0:

        # read in the buffer from the commandline
        # this will block, so send CTRL-D if not sending input to stdin
        #buffer = input("Input something: ")
        buffer = sys.stdin.read()

        # send data off
        client_sender(buffer, configuration)

    # we are going to listen and potentially upload things,
    # execute commands, and drop a shell back depending on 
    # our command line options above
    if configuration["listen"]:
        server_loop(configuration)


if __name__ == "__main__":
    main()
