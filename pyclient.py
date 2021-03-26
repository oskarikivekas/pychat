import socket
import sys
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
nick = input("Give ur desired nickname: ")

IP = sys.argv[1]

#IP = "localhost"

PORT = 1234
hostname = socket.gethostname()
client.connect((IP, PORT))


def recv():

    while (True):
        try:
            msg = client.recv(1024).decode('utf-8')
            if msg == 'giveNICK':
                client.send(nick.encode('utf-8'))
            else:

                print(msg)
        except:
            print("Closing connection!")
            client.close()
            sys.exit(1)
            break


def msg_handler():

    while (True):

        textinput = input('')
        if(not textinput):
            print("\n")
            continue

        if(textinput[0] == '!'):
            if(textinput == '!help'):
                controls()
                continue

            client.send(textinput.encode('utf-8'))
            if(textinput == '!Quit'):
                client.close()
                sys.exit(0)

        else:

            msg = '{}: {}'.format(nick, textinput)
            client.send(msg.encode('utf-8'))


def controls():
    print("\n ##############################################################\n",
          "# !Quit = Leave the chat                                      #\n",
          "# !List = List of channels                                    #\n",
          "# !Join <channel number> = Join to channels, or to create new #\n",
          "# !Pm <username> = send private message to person             #\n",
          "###############################################################\n")


recv_thread = threading.Thread(target=recv).start()
send_thread = threading.Thread(target=msg_handler).start()
print("Type '!help' to see controls\n")
