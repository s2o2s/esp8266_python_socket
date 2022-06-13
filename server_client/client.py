import socket
import threading
from time import sleep
import tkinter as gui
from tkinter import ttk
from matplotlib import pyplot as plt

arr_temp = []
arr_humi = []
arr_time = []

now_temp = '.....'
now_humi = '.....'
now_time = '.....'


# ----------------------------------------------------- xu li gui
def thr_gui():
    win = gui.Tk()
    win.title('Nhiệt độ - Độ ẩm - Nhóm 05')
    win.geometry('380x180')
    win.resizable(0, 0)

    show1 = ttk.Label(win)
    show1.place(x=50, y=20, width=200, heigh=50)
    show2 = ttk.Label(win)
    show2.place(x=210, y=20, width=200, heigh=50)
    show3 = ttk.Label(win)
    show3.place(x=120, y=60, width=200, heigh=50)

    def show_():
        while True:
            show1.config(font=20, foreground='blue', text="Nhiệt độ: " + str(now_temp) + " °C")
            show2.config(font=20, foreground='green', text="Độ ẩm: " + str(now_humi) + " %")
            show3.config(font=20, foreground='black', text="At time: " + now_time)
            sleep(2)

    threading.Thread(target=show_, daemon=True).start()

    def show_chart():
        def thread_show():
            # thong so
            y2 = arr_temp  # gia tri cua nhiet do
            y1 = arr_humi  # gia tri cua do am
            x = arr_time  # thoi gian

            # khoi tao
            fig, ax1 = plt.subplots(1, 1)
            plt.subplots_adjust(left=None, bottom=0.22, right=None, top=0.88, wspace=None, hspace=None)
            ax2 = ax1.twinx()
            # gioi han
            ax1.set(ylim=(0, 90))
            ax2.set(ylim=(0, 70))
            # ve 2 duong
            a1 = ax1.bar(x, y1, 0.5, color='green', label="do am")
            a2 = ax2.plot(x, y2, "r*--", color='blue', label="nhiet do")
            # thiet lap cac truc
            ax1.set_xlabel("Thời gian")
            ax1.tick_params(axis='x', rotation=90)
            ax1.set_ylabel("Độ ẩm", color='green')
            ax1.tick_params(axis='y', labelcolor='green')
            ax2.set_ylabel("Nhiệt độ", color='blue')
            ax2.tick_params(axis='y', labelcolor='blue')
            # chu thich
            plt.legend([a1[0], a2[0]], ['Nhiệt độ', 'Độ ẩm'], loc='best', title='Chú thích')
            # tieu de
            plt.title("Biểu đổ nhiệt độ và độ ẩm")
            # hien thi
            plt.show()

        thread_show()

    button = ttk.Button(win, text='Biểu đồ', command=show_chart)
    button.place(x=130, y=115, width=100, heigh=60)
    win.mainloop()


thread_gui = threading.Thread(target=thr_gui, daemon=True)
thread_gui.start()


# -------------------------------------------------- xu li socket
client_user = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def mss_handle():
    def thread_mss():
        while True:
            mss = client_user.recv(128).decode()
            print('Mss: ' + mss)
            try:
                mss = int(mss)
            except:
                continue
            if mss == 1:
                recv_value(client_user, arr_temp, arr_humi, arr_time)
            elif mss == 2:
                get_value_usually()
            else:
                print('else')
            sleep(0.1)

    threading.Thread(target=thread_mss, daemon=True).start()


def get_value_usually():
    global now_temp
    global now_humi
    global now_time
    client_user.sendall(b'-1')
    now_temp = float(client_user.recv(128).decode())
    client_user.sendall(b'-1')
    now_humi = float(client_user.recv(128).decode())
    client_user.sendall(b'-1')
    now_time = client_user.recv(128).decode()

    print(str(now_temp) + " " + str(now_humi) + " " + now_time)


def recv_value(client, lst_temp, lst_humi, lst_time):
    lst_temp.clear()
    lst_humi.clear()
    lst_time.clear()
    client.sendall(b'-1')
    lent = int(client.recv(128).decode())
    for i in range(0, lent):
        client.sendall(b'-1')
        temp = float(client.recv(128).decode())
        client.sendall(b'-1')
        humi = float(client.recv(128).decode())
        client.sendall(b'-1')
        tim = client.recv(128).decode()
        lst_temp.append(temp)
        lst_humi.append(humi)
        lst_time.append(tim)
    print(lst_temp)
    print(lst_humi)
    print(lst_time)


def main():
    client_user.connect(("dia chi ip", 8080))
    client_user.sendall(b"USER")
    mss_handle()
    sleep(0.1)
    client_user.sendall(b'get_list')
    while True:
        sleep(2)
        client_user.sendall(b'get_data')


main = threading.Thread(target=main, daemon=True)
main.start()

thread_gui.join()


