import socket

def client_sender(buffer, configuration):
    target = configuration["target"]
    port = configuration["port"]

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connect to our target host
        client.connect((target, port))
        
        if len(buffer):
            client.send(buffer.encode("utf-8"))
        
        while True:

            # now wait for data back
            recv_len = 1
            response = ""

            while recv_len:

                data = client.recv(4096)
                recv_len = len(data)
                response += data.decode("utf-8")

                if recv_len < 4096:
                    break

            print(response.rstrip()+'\t')
            
            # wait for more input
            buffer = input("")
            buffer += "\n"

            # send it off
            client.send(buffer.encode("utf-8"))
    
    except:
        print("[*] Exception! Exiting.")

        # tear down connection
        client.close()


