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


def uploadButton():
    global listbox
    file_path = filedialog.askopenfilename(title="Select Graph Image", filetypes=[
                                           ("Image Files", ".png .jpg .gif .img")])
    listbox.insert(END, file_path)

    img = Image.open(file_path)
    if img.size[0] > 690 or img.size[1] > 545:
        img = img.resize((690, 545), Image.ANTIALIAS)
    openImg = ImageTk.PhotoImage(img)
    image = tk.Label(master=back, width=690, height=505, image=openImg)
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
    image = tk.Label(master=back, width=690, height=545, image=openImg)
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

    if str(sound_file) != '':
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
    '''
    if play_pause_button["state"] == "normal":
            play_pause_button["state"] = "disabled"
        elif play_pause_button["state"] == "disabled":
            play_pause_button["state"] = "normal"
        else:
            play_pause_button["state"] == "normal"

        b1["state"] == "normal":
        b1["state"] = "disabled"
        b2["text"] = "enable"

    '''

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
        uploadButton()


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

back = tk.Frame(master=GUI, bg='white')
# Don't allow the widgets inside to determine the frame's width / height
back.pack_propagate(0)
back.pack(fill=tk.BOTH, expand=1)  # Expand the frame to fill the root window


listbox.place(x=180, y=80)

# Changed variables so you don't have these set to None from .pack()
welcomeSPace = tk.Label(master=back, text='',
                        bg='white', fg='black', font=("Impact", 20))
welcomeSPace.pack()
welcome = tk.Label(master=back, text='Welcome to the Audible Graph Reader',
                   bg='white', fg='black', font=("Impact", 20))
welcome.pack()
upload = tk.Button(master=back, text='Upload Graph',
                   width=19, command=uploadButton)
upload.place(x=30, y=120)
read = tk.Button(master=back, text='Read Graph',
                 width=19, command=readTextfile)
read.place(x=30, y=180)
tutorial = tk.Button(master=back, text='Tutorial',
                     width=19, command=play_tutorial)
tutorial.place(x=30, y=240)
previous = tk.Button(master=back, text='Read Previous Graph',
                     width=19, command=readPreviousGraph)
previous.place(x=30, y=300)
pausePlay = tk.Button(master=back, text='Pause / Play',
                      width=19, command=play_pause)
pausePlay.place(x=30, y=360)

replayButton = tk.Button(master=back, text='Replay', width=19, command=replay)
replayButton.place(x=30, y=420)

exitButton = tk.Button(master=back, text='Exit AGR', width=19, command=exitAGR)
exitButton.place(x=30, y=640)

line1Button = tk.Button(master=back, text='Line 1', width=8, command=line1Desc)
line1Button.place(x=190, y=640)

line2Button = tk.Button(master=back, text='Line 2', width=8, command=line2Desc)
line2Button.place(x=260, y=640)

line3Button = tk.Button(master=back, text='Line 3', width=8, command=line3Desc)
line3Button.place(x=330, y=640)

line4Button = tk.Button(master=back, text='Line 4', width=8, command=line4Desc)
line4Button.place(x=400, y=640)

line5Button = tk.Button(master=back, text='Line 5', width=8, command=line5Desc)
line5Button.place(x=470, y=640)

line6Button = tk.Button(master=back, text='Line 6', width=8, command=line6Desc)
line6Button.place(x=540, y=640)

line7Button = tk.Button(master=back, text='Line 7', width=8, command=line7Desc)
line7Button.place(x=610, y=640)

line8Button = tk.Button(master=back, text='Line 8', width=8, command=line8Desc)
line8Button.place(x=680, y=640)


# works, just doesn't work in a function yet
# im = Image.open('images\image4.png')
# ph = ImageTk.PhotoImage(im)
# image = tk.Label(master=back, width=690, height=545, image=ph)
# image.place(x=160, y=120)

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
