import socket
from time import sleep
import threading
import datetime

server = socket.socket()
server.bind(('0.0.0.0', 8080))
server.listen(10)

temp = 0
humi = 0
n = 30
Arr_Temp_Humi_Time = []


def Update_value(t,h):
    if t == -1 or h == -1:
        return
    now_time = datetime.datetime.now().strftime("%H:%M:%S")
    if len(Arr_Temp_Humi_Time) < n:
        Arr_Temp_Humi_Time.append((t,h,now_time,))
    else:
        for i in range(0,n-1):
            Arr_Temp_Humi_Time[i] = Arr_Temp_Humi_Time[i+1]
        Arr_Temp_Humi_Time[n-1] = (t,h,now_time,)


def Send_value(client,lst):
    sleep(0.1)
    client.recv(16)
    client.sendall(str(len(lst)).encode())
    for i in range(0,len(lst)):
        for j in range(0,3):
            client.recv(16)
            sleep(0.1)
            client.sendall(str(lst[i][j]).encode())


def Handle_Client_Esp(client_esp):
    def Thread_Client_Esp():
        global temp
        global humi
        while True:
            temp = -1
            humi = -1
            try:
                content = client_esp.recv(128)
                if content == b'esp8266':
                    content1 = client_esp.recv(128)
                    if content1 == b'-999':
                        print("Err read sensor DHT11")
                    else:
                        #print(content1)
                        content1 = content1.decode()
                        value = content1.split('%')
                        temp = float(value[0])
                        humi = float(value[1])
            except Exception as e:
                #print(e)
                print("ESP8266 disconnect")
                client_esp.close()
                return
            Update_value(temp,humi)
            sleep(1)

    threading.Thread(target=Thread_Client_Esp, daemon=True).start()


def Handle_Client_User(client_user):
    def Thread_Client_User():
        while True:
            try:
                request = client_user.recv(128).decode()
                if request == 'get_list':
                    client_user.sendall(b'1')
                    sleep(0.5)
                    Send_value(client_user,Arr_Temp_Humi_Time)
                    continue
                if len(Arr_Temp_Humi_Time)==0:
                    client_user.sendall(b'999')
                else:
                    client_user.sendall(b'2')
                    client_user.recv(16)
                    client_user.sendall(str(Arr_Temp_Humi_Time[len(Arr_Temp_Humi_Time)-1][0]).encode())
                    client_user.recv(16)
                    client_user.sendall(str(Arr_Temp_Humi_Time[len(Arr_Temp_Humi_Time)-1][1]).encode())
                    client_user.recv(16)
                    client_user.sendall(str(Arr_Temp_Humi_Time[len(Arr_Temp_Humi_Time)-1][2]).encode())
            except Exception as e:
                #print(e)
                print('User disconnect')
                client_user.close()
                return
            sleep(1)
    threading.Thread(target=Thread_Client_User,daemon=True).start()


while True:
    try:
        client, addr = server.accept()
        client.settimeout(10)

        type_client = client.recv(128)
        if type_client == b'ESP':
            Handle_Client_Esp(client)
            print('ESP8266 connected')
            print(addr)
        elif type_client == b'USER':
            Handle_Client_User(client)
            print('User connected')
            print(addr)
        else:
            print('Refuse connect')
            client.close()

    except Exception as e:
        print(e)
    sleep(1)
