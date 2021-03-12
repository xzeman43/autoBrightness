# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import threading
from tkinter import *
import paho.mqtt.client as mqtt
from monitorcontrol import *

listen = False
monitor_num = len(get_monitors())
print(monitor_num)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



def set_luminance(luminance, monitor):
    mon = get_monitors()[monitor]
    with mon:
        mon.set_luminance(int(luminance))


def set_contrast(contrast, monitor):
    mon = get_monitors()[monitor]
    with mon:
        mon.set_contrast(int(contrast))


def on_connect(client, userdata, flags, rc):
    client.subscribe("brightness")
    print("Connected to the MQTT!")


def on_message(client, userdata, msg):
    if listen:
        print(msg.topic + " " + str(msg.payload.decode()))
        userdata['brightness_value'].configure(text=msg.payload)
        for monitor in get_monitors():
            with monitor:
                print(monitor.set_luminance(int(msg.payload)))


def mqtt_thread(name, b_value):
    client = mqtt.Client(userdata=b_value)
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("admin", "FritzBox2")
    client.connect("192.168.1.221", 1883, 60)
    client.loop_forever()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    window = Tk()
    window.geometry("700x300")
    lbl = Label(window, text="Current Brightness:")
    lbl.grid(column=0, row=0)
    brightness_value = Label(window, text="")
    brightness_value.grid(column=1, row=0)
    data_dict = {'brightness_value': brightness_value}
    window.title("autoBrightness awesomness")

    photoOffImg = resource_path("figures/power-off.png")
    photoOff = PhotoImage(file=photoOffImg)
    photoOff = photoOff.subsample(7, 7)
    photoOn = PhotoImage(file=resource_path("figures/power-on.png"))
    photoOn = photoOn.subsample(7, 7)


    def clicked():
        global listen
        if listen:
            power_btn.configure(image=photoOn)
            listen = False
        else:
            power_btn.configure(image=photoOff)
            listen = True

    power_btn = Button(window, text="Turn Off", image=photoOn, command=clicked)
    # power_btn.grid(column=2, row=0)
    power_btn.place(x=650, y=0, width=50, height=50)

    slider_pos = 0
    for i in range(monitor_num):
        mon_it = get_monitors()[i]
        with mon_it:
            code = vcp.VCPCode("image_luminance")
            # Not sure how to do this better
            if mon_it._get_code_maximum(code) != 0:
                brightness_label = Label(window, text="Brightness")
                brightness_label.place(x=slider_pos*50, y=80)
                brightness_slider = Scale(window, from_=0, to=100, command=lambda value, monitor_numik=i: set_luminance(value, monitor_numik))
                brightness_slider.set(int(mon_it.get_luminance()))
                brightness_slider.place(x=slider_pos*50, y=100)
                slider_pos += 1
                contrast_label = Label(window, text="Contrast")
                contrast_label.place(x=slider_pos*75, y=80)
                contrast_slider = Scale(window, from_=0, to=100, command=lambda value, monitor_numik=i: set_contrast(value, monitor_numik))
                contrast_slider.set(int(mon_it.get_contrast()))
                contrast_slider.place(x=slider_pos*75, y=100)
                slider_pos += 1

    x = threading.Thread(target=mqtt_thread, args=(1, data_dict))
    x.start()
    window.mainloop()

    # data_dict["photoOn"] = {photoOn}
    # data_dict["photoOff"] = {photoOff}
    #
    # data_dict["powerBtn"] = power_btn