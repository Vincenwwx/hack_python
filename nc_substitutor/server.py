import socket
import subprocess
import threading
import os

def server_loop(configuration):
    target = configuration["target"]
    port = configuration["port"]
    upload_destination = configuration["upload_destination"]
    execute = configuration["execute"]
    command = configuration["command"]

    # if no target is defined, we listen on all interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    print("[*] Listening on {}: {}".format(target, port))

    while True:
        client_socket, addr = server.accept()

        print(f"[*] Accepted connection from: {addr[0]}: {addr[1]}")

        # spin off a thread to handle our new client
        client_thread = threading.Thread(target=client_handler,
                                         args=(client_socket, upload_destination, execute, command,))
        client_thread.start()

def client_handler(client_socket, upload_destination, execute, command):

    # check for upload
    if len(upload_destination):

        print("[*] Upload mode")
        # read in all of the bytes and write to our destination
        file_buffer = ""

        # keep reading data until none is available
        while True:
            data = client_socket.recv(1024)

            if not data:
                print("Received: {}".format(file_buffer.decode("utf-8")))
                break
            else:
                file_buffer += data

        # now we take these bytes and try to write them out
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # acknowledge that we wrote the file out
            client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send("Failed to save file to %s\r\n" % upload_destination)

    # check for command execution
    if len(execute):

        print("[*] Execution mode")
        # run the command
        output = os.system(execute)

        client_socket.send(output)

    # now we go into another loop if a command shel was requested
    if command:

        print("[*] Command mode")
        while True:
            # show a simple prompt
            client_socket.send("<NC:#> ".encode("utf-8"))

            # now we receive until we see a line feed
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode("utf-8")

            # send back the command output

            print("Server receive command: ", cmd_buffer)
            response = run_command(cmd_buffer)

            # send back the response
            print("Response to be sent: ", response)
            client_socket.send(response)


def run_command(command):
    # trim the newline
    command = command.rstrip()

    # run the command and get the output back
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n".encode("utf-8")

    # send the output back
    return output