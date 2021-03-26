# server

import sys
import socket
from threading import Thread

IP = "localhost"
PORT = 1234
BufSize = 1024
# Create socket object using TCP

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


server_socket.bind((IP, PORT))
server_socket.listen()

# Handling clients and channels by nested dictionary
# nest dict for channel {id : channeldict }
# channel dict {client_obj : username}

main_channel = {}
channel_dict = {1: main_channel}

print(f'Listening connetions on {IP}:{PORT} ')


def client_handler(client):

    while (True):
        try:
            msg = client.recv(BufSize)
            d_msg = msg.decode('utf-8')

            # Get commands from received messages
            if(d_msg[0] == '!'):

                # quit
                if(d_msg[0:5] == '!Quit'):
                    delete(client)

                # join/create channel
                elif(d_msg[0:5] == '!Join'):

                    channelcontrol(client, int(d_msg[5:]))

                # private message
                elif(d_msg[0:3] == '!Pm'):
                    msg_params = d_msg.split(' ')
                    text = ""
                    for i in range(len(msg_params)):
                        if i > 1:
                            text += (msg_params[i] + " ")
                    privatemsg(client, msg_params[1], text)

                # return list of available channels
                elif(d_msg[0:5] == '!List'):
                    channels(client)

                else:
                    client.send("Unknown command, try again.".encode('utf-8'))

            # in case of no commands, just send msg to everyone in your channel
            else:

                broadcast(msg, client)
        except:
            delete(client)
            client.close()


def channels(client):
    channels = "\nCHANNELS:\n"
    for x in channel_dict.keys():
        channels += "channel {}\n".format(x)
    client.send((channels).encode('utf-8'))


def channelcontrol(client, channel):
    # check if that channel exists
    try:
        for c_id, ch in channel_dict.items():

            if c_id == channel and client in ch:
                client.send("You are already in this channel!".encode('utf-8'))
                return

        removekeyfrom = []
        for channel_n, channel_l in channel_dict.items():
            for key in channel_l:
                if(key == client):

                    oldchannel = channel_n
                    userobj = key
                    username = channel_l.get(key)
                    removekeyfrom.append(channel_l)

        for x in removekeyfrom:
            x.pop(client)

        removekeyfrom.clear()

        if not channel in channel_dict.keys():
            channel_dict[channel] = {userobj: username}

            userobj.send(("New channel created! \n Joined to channel {}".format(
                str(channel))).encode('utf-8'))
        else:

            channel_dict[channel].update({userobj: username})
            userobj.send(("\n" + username + " Joined channel " +
                          str(channel)).encode('utf-8'))

    except:
        print("Some error occured in channel manager!")
        pass


def broadcast(msg, client):

    # get current channel of client
    for channel in channel_dict.values():
        if(channel):
            if(client in channel or client == 9999):
                for c in channel:
                    try:
                        c.send(msg)
                    except:
                        c.close()
                        delete(c)


def privatemsg(client, receiver, msg):
    # get username for msg sender
    for channel in channel_dict.values():
        for c in channel.keys():
            if c == client:
                sender = channel.get(c)

    # find target socket by username

    for channel_i, channel_l in channel_dict.items():
        for c, u in channel_l.items():
            if u == receiver:
                c.send("<PM from |{}|: {}".format(
                    sender, msg).encode('utf-8'))


def delete(client):
    removekeyfrom = []
    for channel in channel_dict.values():
        for c in channel.keys():
            if c == client:
                removekeyfrom.append(channel)
    client.close()

    for x in removekeyfrom:
        x.pop(client)
    removekeyfrom.clear()


def new_client(client, username):
    main_channel.update({client: username})


while (True):
    print("Server listening..")
    client, address = server_socket.accept()

    print("\n{} Connected!".format(str(address)))

    client.send('giveNICK'.encode('utf-8'))
    username = client.recv(BufSize).decode('utf-8')
    new_client(client, username)

    print("\nUsername: {}".format(username))
    broadcast("{} has joined to chat!".format(
        username).encode('utf-8'), client)
    client.send("\nYou have connected to main channel!".encode('utf-8'))

    Thread(target=client_handler, args=(client,)).start()


client.close()
server_socket.close()
