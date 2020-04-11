# utf-8
# 4.11.2020
# US-6 Task 1 : Graphical User Interface

# blank.wav must exist in same dir as this file

import tkinter as tk
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
import pyaudio
import wave
import time
import os

# Global
playing_bool = False
global img
sound_file = ''
GUI = tk.Tk()
listbox = Listbox(GUI, height=2, width=100, selectmode='single')

# Open blank Wav file
wf = wave.open('blank.wav', 'r')

# init PyAudio
p = pyaudio.PyAudio()


def callback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    return (data, pyaudio.paContinue)


# open stream using callback
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback)

# Stop stream from playing initially
stream.stop_stream()

## Begin Functions ##


def upload():
    global listbox
    file_path = filedialog.askopenfilename(title="Select Graph Image", filetypes=[
                                           ("Image Files", ".png .jpg .gif .img")])
    listbox.insert(END, file_path)

    img = Image.open(file_path)
    if img.size[0] > 690 or img.size[1] > 545:
        img = img.resize((690, 545), Image.ANTIALIAS)
    openImg = ImageTk.PhotoImage(img)
    image = tk.Label(master=background, width=690, height=505, image=openImg)
    image.image = openImg
    image.place(x=160, y=120)

    print(file_path + " has been opened in the preview window")


def readPreviousGraph():
    # CAN ONLY GET HERE IF AGR FOLDER EXISTS plzNty
    AGR_FOLDER = os.path.normpath(os.path.expanduser("~/Desktop/AGR/Graphs/"))
    file_path = filedialog.askopenfilename(
        initialdir=AGR_FOLDER, title="Select Previous Graph Image", filetypes=[
            ("Image Files", ".png .jpg .gif .img")])
    img = Image.open(file_path)
    if img.size[0] > 690 or img.size[1] > 545:
        img = img.resize((690, 545), Image.ANTIALIAS)

    openImg = ImageTk.PhotoImage(img)
    image = tk.Label(master=background, width=690, height=545, image=openImg)
    image.image = openImg
    image.place(x=160, y=120)

    print(file_path + " has been opened in the preview window")


def readTextfile():
    print("ReadingTextFile?")


def play_tutorial():
    print("Playing Tut")


def play_line_desc(line_number):
    global playing_bool
    global stream
    global p
    global wf
    global sound_file

    if playing_bool or stream.is_active():
        stream.stop_stream()

    sound_file = str(line_number) + ".wav"
    print(sound_file)
    wf = wave.open(sound_file, 'r')
    print(sound_file, " loaded")

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    stream_callback=callback)
    return stream


def replay():
    global playing_bool
    global stream
    global p
    global wf
    global sound_file

    if str(sound_file) != '':  # This doesnt work

        if playing_bool or stream.is_active():
            stream.stop_stream()

        try:
            wf = wave.open(sound_file, 'r')
            print(sound_file, " loaded")

            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True,
                            stream_callback=callback)
            return stream
        except:
            print(" Error: Bad Sound file ")
    else:
        print(" Error: Sound file does not exist ")


def play_pause():  # playing_bool):
    global playing_bool
    global stream
    if stream.is_stopped():
        print('play pressed')
        # listbox.insert(END, "Playing Played")
        stream.start_stream()
        playing_bool = True
        return False
    elif stream.is_active():
        print('pause pressed')
        # listbox.insert(END, "Playing Paused")
        stream.stop_stream()
        playing_bool = False
        return False
    return False


def key(event):
    key_char = event.char
    key_symb = event.keysym
    key_code = event.keycode
    print("Pressed ", key_char, " ", key_symb, " ", key_code)
    # play_pause_button.place_forget()
    # play_pause_button.place(x=50, y=60)

    if event.keysym == 'space':
        play_pause()
    elif event.keysym == '1':
        play_line_desc(1)
    elif event.keysym == '2':
        play_line_desc(2)
    elif event.keysym == '3':
        play_line_desc(3)
    elif event.keysym == '4':
        play_line_desc(4)
    elif event.keysym == '5':
        play_line_desc(5)
    elif event.keysym == '6':
        play_line_desc(6)
    elif event.keysym == '7':
        play_line_desc(7)
    elif event.keysym == '8':
        play_line_desc(8)
    elif event.keysym == 'h':
        play_tutorial()
    elif event.keysym == 'r':
        replay()
    elif event.keysym == 'u':
        upload()


def exitAGR():

    GUI.destroy()

## End oF Functions ##


def line1Desc():
    play_line_desc(1)


def line2Desc():
    play_line_desc(2)


def line3Desc():
    play_line_desc(3)


def line4Desc():
    play_line_desc(4)


def line5Desc():
    play_line_desc(5)


def line6Desc():
    play_line_desc(6)


def line7Desc():
    play_line_desc(7)


def line8Desc():
    play_line_desc(8)


# If you have a large number of widgets, like it looks like you will for your
# game you can specify the attributes for all widgets simply like this.
GUI.option_add("*Button.Background", "light blue")
GUI.option_add("*Button.Foreground", "black")
GUI.option_add("*Button.Font", ("Impact", 10))

GUI.title('Audible Graph Reader')
# You can set the geometry attribute to change the root windows size
GUI.geometry("900x700")  # You want the size of the app to be 500x500
GUI.resizable(0, 0)  # Don't allow resizing in the x or y direction

background = tk.Frame(master=GUI, bg='white')
# Don't allow the widgets inside to determine the frame's width / height
background.pack_propagate(0)
# Expand the frame to fill the root window
background.pack(fill=tk.BOTH, expand=1)

listbox.place(x=180, y=80)

# Changed variables so you don't have these set to None from .pack()
welcome_label = tk.Label(master=background, text='\nWelcome to the Audible Graph Reader',
                         bg='white', fg='black', font=("Impact", 20))
welcome_label.pack()
upload_button = tk.Button(master=background, text='Upload Graph',
                          width=19, command=upload)
upload_button.place(x=30, y=120)
read = tk.Button(master=background, text='Read Graph',
                 width=19, command=readTextfile)
read.place(x=30, y=180)
tutorial_button = tk.Button(master=background, text='Tutorial',
                            width=19, command=play_tutorial)
tutorial_button.place(x=30, y=240)
load_previous_graph = tk.Button(master=background, text='Load Previous Graph',
                                width=19, command=readPreviousGraph)
load_previous_graph.place(x=30, y=300)
pause_play_button = tk.Button(master=background, text='Pause / Play',
                              width=19, command=play_pause)
pause_play_button.place(x=30, y=360)

replay_button = tk.Button(
    master=background, text='Replay', width=19, command=replay)
replay_button.place(x=30, y=420)


exitButton = tk.Button(master=background, text='Exit AGR',
                       width=19, command=exitAGR)
exitButton.place(x=30, y=640)

line_1_button = tk.Button(master=background, text='Line 1',
                          width=8, command=line1Desc)
line_1_button.place(x=190, y=640)

line_2_button = tk.Button(master=background, text='Line 2',
                          width=8, command=line2Desc)
line_2_button.place(x=260, y=640)

line_3_button = tk.Button(master=background, text='Line 3',
                          width=8, command=line3Desc)
line_3_button.place(x=330, y=640)

line_4_button = tk.Button(master=background, text='Line 4',
                          width=8, command=line4Desc)
line_4_button.place(x=400, y=640)

line_5_button = tk.Button(master=background, text='Line 5',
                          width=8, command=line5Desc)
line_5_button.place(x=470, y=640)

line_6_button = tk.Button(master=background, text='Line 6',
                          width=8, command=line6Desc)
line_6_button.place(x=540, y=640)

line_7_button = tk.Button(master=background, text='Line 7',
                          width=8, command=line7Desc)
line_7_button.place(x=610, y=640)

line_8_button = tk.Button(master=background, text='Line 8',
                          width=8, command=line8Desc)
line_8_button.place(x=680, y=640)

# Disable buttons on startup
line_1_button["state"] = "disabled"
line_2_button["state"] = "disabled"
line_3_button["state"] = "disabled"
line_4_button["state"] = "disabled"
line_5_button["state"] = "disabled"
line_6_button["state"] = "disabled"
line_7_button["state"] = "disabled"
line_8_button["state"] = "disabled"
replay_button["state"] = "disabled"
load_previous_graph["state"] = "disabled"
pause_play_button["state"] = "disabled"

GUI.bind("<Key>", key)  # calls key (function above) on Keyboard input
GUI.resizable(False, False)

GUI.mainloop()

# stop stream
stream.stop_stream()
stream.close()
wf.close()

# close PyAudio
p.terminate()

print("Program Terminated")
