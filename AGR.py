#!/usr/bin/env python3
# utf-8


# The Audible Graph Reader Project
# Copyright 2020 Missouri State University

# 4.11.2020


# User must install pytesseract version 5
# blank.wav must exist in same dir as this file
# USE: ./AGR.py
# On execution AGR/Graphs Folder is created on Desktop
#       timestamped folder containing json, image and list files are created


import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
import pyaudio
import wave
import time
import os
#
import cv2
import sys
#from sys import argv
from datetime import datetime
import os
import json
import ntpath  # To interact with filepath
import shutil  # High level file operations (cp img)
import numpy as np
from PIL import Image, ImageEnhance
from collections import OrderedDict
from operator import itemgetter
import pytesseract
from pytesseract import Output
import re
import statistics
import math
from itertools import islice
from stat import S_IREAD, S_IRGRP, S_IROTH  # allows os for read only

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe' # Josh/Alex
#pytesseract.pytesseract.tesseract_cmd = r"C:\\Users\\Think\\AppData\\Local\\Tesseract-OCR\\tesseract.exe"  # Nate

# Global
x_axis_pos = []  # image1 (98, 395), (543, 395)
y_axis_pos = []  # image1 (95, 393), (97, 85)
playing_bool = False
global img
global file_path
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

    if (len(file_path) > 247):
        messagebox.showerror(
            title="AGR:Error", message="File path is too long.")
        print(" Error: File path is too long")
    else:
        file_name, file_extension = os.path.splitext(file_path)
        og_file_name = path_leaf(file_path)

        regex = '<>:"|?*'
        for char in regex:
            if char in og_file_name:
                messagebox.showerror(
                    title="AGR:Error", message="File path has illegal chars.")
                print(" Error: File path must not contain ",
                      str(char), " or <>\":|?*")
                return False

        if os.path.getsize(file_path) >= 1000000:
            messagebox.showerror(
                title="AGR:Error", message="File is too large.")
            print(" Error: File is too large, must be less than 1 MB")
            return False

        now = datetime.now()
        timestamp = str(round(datetime.timestamp(now)))

        new_file_name = og_file_name + "." + timestamp
        # print("newfilename: ", new_file_name)

        desktop = os.path.normpath(os.path.expanduser("~/Desktop"))
        path = desktop + "/AGR/Graphs/" + new_file_name + "/"

        try:
            os.makedirs(path)  # Create all necessary directories
        except OSError:
            print(" Error: Creation of the directory %s failed" % path)
        else:
            print(" info: Successfully created the directory %s" % path)

        shutil.copy(file_path, path)

        # change wd to path of desktop
        os.chdir(path)

        # check if img is png
        if og_file_name[-4:] in {'.png'}:
            img = Image.open(og_file_name)
            img = cv2.imread(og_file_name)  # 'eimg.png')
        else:
            name_no_ext = og_file_name.split('.')
            # print("nameNoext: ", name_no_ext[0])  # nameNoext:  image4
            img = Image.open(og_file_name).save(path + name_no_ext[0] + '.png')
            img = cv2.imread(name_no_ext[0] + '.png')  # 'eimg.png')

        # img = ImageEnhance.Sharpness(img.convert('RGB'))
        # img = img.enhance(5.0).save('eimg.png')

        img_size = img.shape
        print(img_size)
        y_pixels_height = img.shape[0]
        x_pixels_width = img.shape[1]
        cropped_img = img[10: y_pixels_height-10, 10: x_pixels_width-10]
        cropped_y_pixels_height = img.shape[0]
        cropped_x_pixels_width = img.shape[1]
        print(cropped_img.shape)
        x_axis_exists = True
        y_axis_exists = True

        cropped_x_axis = cropped_img[round(
            cropped_y_pixels_height*0.7): cropped_y_pixels_height, 0: cropped_x_pixels_width]

        cropped_y_axis = cropped_img[0: cropped_y_pixels_height, 0: round(
            cropped_x_pixels_width*0.3)]

        xcoords, ycoords = find_coords(cropped_x_axis, cropped_y_axis)

        y_pixel_line, x_pixel_line, longest_yline_size, longest_xline_size, x_axis_exists, y_axis_exists, origin = store_coords(
            cropped_img, xcoords, ycoords, cropped_x_pixels_width, cropped_y_pixels_height, x_axis_exists, y_axis_exists)

        y_axis_values, biggest_max, y_axis_title = get_ydata(
            cropped_img, x_pixel_line, y_pixel_line, y_axis_exists, longest_xline_size)

        line_data, x_axis_values, num_lines, x_axis_title = get_xdata(cropped_img, y_pixel_line, x_pixel_line,
                                                                      x_axis_exists, y_axis_values, longest_yline_size, longest_xline_size)

        # ASSIGN VARIABLES

        X_AXIS_MIN = 0
        J_GRAPH_TITLE = str(get_graph_title(cropped_img))
        J_X_AXIS_TITLE = x_axis_title
        J_Y_AXIS_TITLE = y_axis_title
        J_X_AXIS_VALUES = x_axis_values
        J_Y_AXIS_VALUES = y_axis_values
        J_ORIGIN = str(origin)

        # SET CORRECT VALS HERE
        J_FOUND_COLORS = "toBeDetermined"
        J_DATA_POINTS = "toBeDetermined"  # xcoords
        J_LEGEND_DATA = "toBeDetermined"  # dict

        # pass dict of points
        # points = dict({1: [(1, 300), (2, 125), (3, 200), (4, 400), (5, 378)], 2: [
        #              (1, 200), (2, 429), (3, 400), (4, 300), (5, 500)], 3: [(1, 0), (2, 100), (3, 250), (4, 450), (5, 440)]})
        trend_line_dict, slopes_strings_dict, intersections_dict = getIntersections(
            line_data, x_axis_values, num_lines, biggest_max)

        x = {
            "image_name": new_file_name,
            "main_title": J_GRAPH_TITLE,  # STRING
            "x_axis_title": J_X_AXIS_TITLE,  # STRING
            "x_axis_values": J_X_AXIS_VALUES,  # LIST
            "y_axis_title": J_Y_AXIS_TITLE,  # STRING
            "y_axis_values": J_Y_AXIS_VALUES,  # LIST
            "found_colors": J_FOUND_COLORS,  # LIST OF RGB
            "data_points": J_DATA_POINTS,  # LIST OF TUPLES
            "origin": J_ORIGIN,  # TUPLE
            "legend_data": J_LEGEND_DATA  # DICT (line names, line colors)
        }

        try:
            f = open(path + og_file_name +
                     ".json", 'w')  # Create .json file
        except:
            print(" Error: JSON file creation failed")
        else:
            print(" info: Successfully created .json")

        try:
            jsonData = json.dumps(x,  indent=2)  # with newline
            # jsonData = json.dumps(x)   # without newline
            # print(jsonData)
            print(" info: Successfully dumpt json")
        except:
            print(" Error: Unable to format json")
            pass

        try:
            f.write(jsonData)
            print(" info: Successfully wrote json data")
        except:
            print(" Error: Unable to write json")

        f.close()

        audText = "Graph " + timestamp + " \n"
        audText += "The graph is titled " + J_GRAPH_TITLE + ". \n"

        aud_text_file_name = new_file_name + '.txt'

        try:
            f = open(aud_text_file_name, "w+")  # create read/write
            print(" info: Successfully created text file")
            try:
                f.write(audText)
                print(" info: Successfully wrote text data")
                try:
                    os.chmod(aud_text_file_name, S_IREAD | S_IRGRP |
                             S_IROTH)  # lock file to read-only
                    print(" info: Succesfully write locked text file")
                except:
                    print(" Error: Unable to lock file to read only")
            except:
                print(" Error: Unable to write text data")
            f.close

        except:
            print(" Error: Unable to create file")

        img = Image.open(file_path)
        if img.size[0] > 690 or img.size[1] > 545:
            img = img.resize((690, 545), Image.ANTIALIAS)
        openImg = ImageTk.PhotoImage(img)
        image = tk.Label(master=background, width=690,
                         height=505, image=openImg)
        image.image = openImg
        image.place(x=160, y=120)

    print(file_path + " has been opened in the preview window")


def load_previous_graph():
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


def read_text_file():
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
    global line_1_button

    # pretty print keys
    key_char = event.char
    key_symb = event.keysym
    key_code = event.keycode
    print("Pressed ", key_char, " ", key_symb, " ", key_code)

    # play_pause_button.place_forget()
    # play_pause_button.place(x=50, y=60)

    if event.keysym == 'space':
        play_pause()
    elif event.keysym == '1':
        print("button1 state: ", line_1_button["state"])
        if line_1_button["state"] == "normal":
            play_line_desc(1)
        else:
            print(" Error: Line desc not enabled")
    elif event.keysym == '2':
        print("button2 state: ", line_2_button["state"])
        if line_1_button["state"] == "normal":
            play_line_desc(2)
        else:
            print(" Error: Line desc not enabled")
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


def place_line_desc_buttons(number_of_lines):
    global line_1_button
    global line_2_button
    global line_3_button
    global line_4_button
    global line_5_button
    global line_6_button
    global line_7_button
    global line_8_button
    if number_of_lines == 8:
        line_1_button.place(x=190, y=640)
        line_1_button["state"] = "normal"
        line_2_button.place(x=260, y=640)
        line_2_button["state"] = "normal"
        line_3_button.place(x=330, y=640)
        line_3_button["state"] = "normal"
        line_4_button.place(x=400, y=640)
        line_4_button["state"] = "normal"
        line_5_button.place(x=470, y=640)
        line_5_button["state"] = "normal"
        line_6_button.place(x=540, y=640)
        line_6_button["state"] = "normal"
        line_7_button.place(x=610, y=640)
        line_7_button["state"] = "normal"
        line_8_button.place(x=680, y=640)
        line_8_button["state"] = "normal"
    elif number_of_lines == 7:
        line_1_button.place(x=190, y=640)
        line_1_button["state"] = "normal"
        line_2_button.place(x=260, y=640)
        line_2_button["state"] = "normal"
        line_3_button.place(x=330, y=640)
        line_3_button["state"] = "normal"
        line_4_button.place(x=400, y=640)
        line_4_button["state"] = "normal"
        line_5_button.place(x=470, y=640)
        line_5_button["state"] = "normal"
        line_6_button.place(x=540, y=640)
        line_6_button["state"] = "normal"
        line_7_button.place(x=610, y=640)
        line_7_button["state"] = "normal"
    elif number_of_lines == 6:
        line_1_button.place(x=190, y=640)
        line_1_button["state"] = "normal"
        line_2_button.place(x=260, y=640)
        line_2_button["state"] = "normal"
        line_3_button.place(x=330, y=640)
        line_3_button["state"] = "normal"
        line_4_button.place(x=400, y=640)
        line_4_button["state"] = "normal"
        line_5_button.place(x=470, y=640)
        line_5_button["state"] = "normal"
        line_6_button.place(x=540, y=640)
        line_6_button["state"] = "normal"
    elif number_of_lines == 5:
        line_1_button.place(x=190, y=640)
        line_1_button["state"] = "normal"
        line_2_button.place(x=260, y=640)
        line_2_button["state"] = "normal"
        line_3_button.place(x=330, y=640)
        line_3_button["state"] = "normal"
        line_4_button.place(x=400, y=640)
        line_4_button["state"] = "normal"
        line_5_button.place(x=470, y=640)
        line_5_button["state"] = "normal"
    elif number_of_lines == 4:
        line_1_button.place(x=190, y=640)
        line_1_button["state"] = "normal"
        line_2_button.place(x=260, y=640)
        line_2_button["state"] = "normal"
        line_3_button.place(x=330, y=640)
        line_3_button["state"] = "normal"
        line_4_button.place(x=400, y=640)
        line_4_button["state"] = "normal"
    elif number_of_lines == 3:
        line_1_button.place(x=190, y=640)
        line_1_button["state"] = "normal"
        line_2_button.place(x=260, y=640)
        line_2_button["state"] = "normal"
        line_3_button.place(x=330, y=640)
        line_3_button["state"] = "normal"
    elif number_of_lines == 2:
        line_1_button.place(x=190, y=640)
        line_1_button["state"] = "normal"
        line_2_button.place(x=260, y=640)
        line_2_button["state"] = "normal"
    elif number_of_lines == 1:
        line_1_button.place(x=190, y=640)
        line_1_button["state"] = "normal"
    else:
        print(
            " Error: bad args on place_line_desc_buttons(), must be integer between 1 and 8")


def remove_line_desc_buttons(number_of_lines):
    global line_1_button
    global line_2_button
    global line_3_button
    global line_4_button
    global line_5_button
    global line_6_button
    global line_7_button
    global line_8_button
    if number_of_lines == 8:
        line_1_button.place_forget()
        line_1_button["state"] = "disabled"
        line_2_button.place_forget()
        line_2_button["state"] = "disabled"
        line_3_button.place_forget()
        line_3_button["state"] = "disabled"
        line_4_button.place_forget()
        line_4_button["state"] = "disabled"
        line_5_button.place_forget()
        line_5_button["state"] = "disabled"
        line_6_button.place_forget()
        line_6_button["state"] = "disabled"
        line_7_button.place_forget()
        line_7_button["state"] = "disabled"
        line_8_button.place_forget()
        line_8_button["state"] = "disabled"
    elif number_of_lines == 7:
        line_1_button.place_forget()
        line_1_button["state"] = "disabled"
        line_2_button.place_forget()
        line_2_button["state"] = "disabled"
        line_3_button.place_forget()
        line_3_button["state"] = "disabled"
        line_4_button.place_forget()
        line_4_button["state"] = "disabled"
        line_5_button.place_forget()
        line_5_button["state"] = "disabled"
        line_6_button.place_forget()
        line_6_button["state"] = "disabled"
        line_7_button.place_forget()
        line_7_button["state"] = "disabled"
    elif number_of_lines == 6:
        line_1_button.place_forget()
        line_1_button["state"] = "disabled"
        line_2_button.place_forget()
        line_2_button["state"] = "disabled"
        line_3_button.place_forget()
        line_3_button["state"] = "disabled"
        line_4_button.place_forget()
        line_4_button["state"] = "disabled"
        line_5_button.place_forget()
        line_5_button["state"] = "disabled"
        line_6_button.place_forget()
        line_6_button["state"] = "disabled"
    elif number_of_lines == 5:
        line_1_button.place_forget()
        line_1_button["state"] = "disabled"
        line_2_button.place_forget()
        line_2_button["state"] = "disabled"
        line_3_button.place_forget()
        line_3_button["state"] = "disabled"
        line_4_button.place_forget()
        line_4_button["state"] = "disabled"
        line_5_button.place_forget()
        line_5_button["state"] = "disabled"
    elif number_of_lines == 4:
        line_1_button.place_forget()
        line_1_button["state"] = "disabled"
        line_2_button.place_forget()
        line_2_button["state"] = "disabled"
        line_3_button.place_forget()
        line_3_button["state"] = "disabled"
        line_4_button.place_forget()
        line_4_button["state"] = "disabled"
    elif number_of_lines == 3:
        line_1_button.place_forget()
        line_1_button["state"] = "disabled"
        line_2_button.place_forget()
        line_2_button["state"] = "disabled"
        line_3_button.place_forget()
        line_3_button["state"] = "disabled"
    elif number_of_lines == 2:
        line_1_button.place_forget()
        line_1_button["state"] = "disabled"
        line_2_button.place_forget()
        line_2_button["state"] = "disabled"
    elif number_of_lines == 1:
        line_1_button.place_forget()
        line_1_button["state"] = "disabled"
    else:
        print(" Error: bad args on remove_line_desc_buttons() line buttons, must be integer between 1 and 8")


def exitAGR():

    GUI.destroy()

## Begin functions outside of GUI ##


def getTrendlines(points, y_max):
    # Correct answer
    # dict({1: [10, 7, -9], 2: [5, 1, -4]})
    # dict({1: [-175, 75, 200, -22], 2: [229, -29, -100, 200], 3:[100, 150, 200, -10]})
    MAX_Y_VAL = float(y_max)  # Max value found on the y-axis
    slopes = dict()  # holds all of the slope values
    relative_slopes = dict()  # holds the values of "up", "down", "stays the same"
    x_y = points.items()
    for key, values in x_y:
        for i in range(len(values) - 1):
            x1 = values[i][0]
            y1 = values[i][1]
            x2 = values[i + 1][0]
            y2 = values[i + 1][1]
            # print("x1: ", x1, "y1: ", y1, "x2: ", x2, "y2: ", y2)
            slope = round((y2 - y1) / (x2 - x1), 2)
            if slope > 0:
                if slope/MAX_Y_VAL > 0.5:
                    if key in relative_slopes:
                        relative_slopes[key].append("up sharply")
                    else:
                        relative_slopes[key] = ["up sharply"]
                elif slope/MAX_Y_VAL > 0.3:
                    if key in relative_slopes:
                        relative_slopes[key].append("up significantly")
                    else:
                        relative_slopes[key] = ["up significantly"]
                elif slope/MAX_Y_VAL > 0.1:
                    if key in relative_slopes:
                        relative_slopes[key].append("up moderately")
                    else:
                        relative_slopes[key] = ["up moderately"]
                else:
                    if key in relative_slopes:
                        relative_slopes[key].append("up slightly")
                    else:
                        relative_slopes[key] = ["up slightly"]
            elif slope < 0:
                if slope/MAX_Y_VAL < -0.5:
                    if key in relative_slopes:
                        relative_slopes[key].append("down sharply")
                    else:
                        relative_slopes[key] = ["down sharply"]
                elif slope/MAX_Y_VAL < -0.3:
                    if key in relative_slopes:
                        relative_slopes[key].append("down significantly")
                    else:
                        relative_slopes[key] = ["down significantly"]
                elif slope/MAX_Y_VAL < -0.1:
                    if key in relative_slopes:
                        relative_slopes[key].append("down moderately")
                    else:
                        relative_slopes[key] = ["down moderately"]
                else:
                    if key in relative_slopes:
                        relative_slopes[key].append("down slightly")
                    else:
                        relative_slopes[key] = ["down slightly"]
            else:
                if key in relative_slopes:
                    relative_slopes[key].append("stays the same")
                else:
                    relative_slopes[key] = ["stays the same"]
            if key in slopes:
                slopes[key].append(slope)
            else:
                slopes[key] = [slope]
    print("slopes: ", slopes)
    print("relative_slopes: ", relative_slopes)
    return slopes, relative_slopes

# Need to pass in the dictionary of (x,y) values as points


def getIntersections(points, x_axis_values, num_lines, biggest_max):
    intersections = dict()  # holds the intersections

    # For 3 lines with 5 points each
    # points = dict({1: [(1, 300), (2, 125), (3, 200), (4, 400), (5, 378)], 2: [
    #              (1, 200), (2, 429), (3, 400), (4, 300), (5, 500)], 3: [(1, 0), (2, 100), (3, 250), (4, 450), (5, 440)]})

    trendlines, slope_strings = getTrendlines(points, biggest_max)

    # For 2 lines with 4 points each
    # points = dict({1: [(0,0), (1, 10), (2,17), (3, 8)], 2: [(0, 8), (1, 13), (2, 14), (3, 10)]})
    # trendlines, slope_strings = getTrendlines(points)
    x_y = points.items()
    trendline_items = trendlines.items()
    SPACING = 1  # distance between values on the x-axis
    # number of points per line
    NUM_POINTS = len(x_axis_values)
    NUM_LINES = num_lines  # number of lines in the graph
    X_MIN = 1  # minimum value on the x-axis

    # Only want to compare the parts of the line that are within
    # the same x value range, ie the parts of each line that exist
    # between x = 1 and x = 2
    for i in range(NUM_POINTS - 1):
        slopes = []  # holds all the slopes
        x_y_vals = []  # holds all of the x and y vals

        # Creates the 2D matrix that holds the values for the equations
        # m, b, x, y for the eq y = m * x + b
        cols, rows = (NUM_LINES, 4)
        equations = [[0 for index in range(rows)] for jindex in range(cols)]

        # Used to reset after each iteration
        x_max = 0
        m1 = 0
        m2 = 0
        m3 = 0
        b1 = 0
        b2 = 0
        b3 = 0
        x_i = 0  # x intersection value
        y_i = 0  # y intersection value

        for keys, values in x_y:
            x_y_vals.append(values[i][0])
            x_y_vals.append(values[i][1])

        for k, value in trendline_items:
            slopes.append(value[i])

        for j in range(NUM_LINES):
            m1 = slopes[j]
            x = x_y_vals[2 * j]
            y = x_y_vals[2 * j + 1]
            b1 = y - (m1 * x)

            # order is [m, b, x, y]
            equations[j][0] = m1
            equations[j][1] = b1
            equations[j][2] = x
            equations[j][3] = y

            m1 = 0
            x = 0
            y = 0
            b1 = 0

        eq = 0
        for equation in range(NUM_LINES):
            eq += 1
            X_MIN += X_MIN
            for eq in range(NUM_LINES):
                x_max = equations[equation][2] + SPACING

                m1 = equations[equation][0]
                b1 = equations[equation][1]
                m2 = equations[eq][0]
                b2 = equations[eq][1]
                b3 = b2 - b1
                m3 = m1 - m2
                if m3 == 0:  # means the lines are parallel and will never intersect or are the same line
                    continue

                x_i = b3/m3
                if x_i > x_max or x_i < X_MIN:
                    continue

                y_i = round((m1 * x_i) + b1, 1)

                x_i = round(x_i, 1)

                intersection_coord = (eq + 1, x_i, y_i)

                if equation + 1 in intersections:
                    intersections[equation + 1].append(intersection_coord)
                else:
                    intersections[equation + 1] = [(eq + 1, x_i, y_i)]
                # print("Intersection at: ", x_i, y_i)

    print("Intersections: ", intersections)
    return trendlines, slope_strings, intersections
    # Correct answer
    # intersections = dict({1: [(2, 1.5, 13.5), (2, 2.6, 11.6)]})


def check_fileType(file_name):
    if file_name[-4:] in {'.jpg', '.png', '.img', '.gif'}:
        return True
    elif file_name[-5:] in {'.jpeg'}:
        return True
    else:
        return False


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def find_coords(cropped_x_axis, cropped_y_axis):
    gray = cv2.cvtColor(cropped_x_axis, cv2.COLOR_BGR2GRAY)

    # set threshold level
    threshold_level = 120

    # find coordinates of all pixels below threshold
    xcoords = np.column_stack(np.where(gray < threshold_level))

    # create mask of all pixels lower than threshold level
    mask = gray < threshold_level

    # color the pixels in the mask
    # cropped_img[mask] = (204, 119, 0)

    gray = cv2.cvtColor(cropped_y_axis, cv2.COLOR_BGR2GRAY)

    # set threshold level
    threshold_level = 120

    # find coordinates of all pixels below threshold
    ycoords = np.column_stack(np.where(gray < threshold_level))

    # create mask of all pixels lower than threshold level
    mask = gray < threshold_level

    # color the pixels in the mask
    # cropped_img[mask] = (204, 119, 0)

    return xcoords, ycoords


def store_coords(cropped_img, xcoords, ycoords, cropped_x_pixels_width, cropped_y_pixels_height, x_axis_exists, y_axis_exists):
    global x_axis_pos
    global y_axis_pos
    # dictionary stores the y coordinates of pixels along with how many times they appear at one y position
    y_values = {}

    # coordinate values are added to this list to iterate through
    ylist = []

    # stores the y coordinates of each pixel under the threshold into the dictionary y_values
    for i in range(len(xcoords)):
        ylist.append(xcoords[i])
        if xcoords[i][0] not in y_values:
            y_values[xcoords[i][0]] = 1
        else:
            y_values[xcoords[i][0]] += 1

    # sorts the dicctionary based on the number of times a pixel appears at one y coordinate
    sorted_xdict = OrderedDict(
        sorted(y_values.items(), key=itemgetter(1), reverse=True))

    # the longest line is the first in the sorted dictionary
    longest_yline_size = list(sorted_xdict.values())[0]
    y_pixel_line = list(sorted_xdict.keys())[
        0] + round(cropped_y_pixels_height*0.7)

    x_values = {}

    # coordinate values are added to this list to iterate through
    xlist = []

    # stores the y coordinates of each pixel under the threshold into the dictionary y_values
    for i in range(len(ycoords)):
        xlist.append(ycoords[i])
        if ycoords[i][1] not in x_values:
            x_values[ycoords[i][1]] = 1
        else:
            x_values[ycoords[i][1]] += 1

    # sorts the dictionary based on the number of times a pixel appears at one y coordinate
    sorted_ydict = OrderedDict(
        sorted(x_values.items(), key=itemgetter(1), reverse=True))

    # the longest line is the first in the sorted dictionary
    longest_xline_size = list(sorted_ydict.values())[0]
    # print(list(sorted_ydict.values())[1], 'gggg')
    x_pixel_line = list(sorted_ydict.keys())[0]

    origin = (x_pixel_line, y_pixel_line)

    print("origin: ", origin)  # , 'aaaaa')

# if the longest line is bigger than half the width of the page it is the x-axis
    if longest_yline_size > 0.5*cropped_x_pixels_width:
        print("The x-axis is at y pixel ", y_pixel_line)
        print("The x-axis is ", longest_yline_size, " pixels long")
    else:
        messagebox.showinfo(title = "Get x-axis", message = "Double click at the origin and the end of the x-axis")
        click_img_x_axis(cropped_img)
        print(x_axis_pos)
        y_pixel_line = x_axis_pos[0][1]
        longest_yline_size = x_axis_pos[1][0] - x_axis_pos[0][0]
        print("The x-axis is at y pixel ", y_pixel_line)
        print("The x-axis is ", longest_yline_size, " pixels long")
        x_axis_exists = True

    if longest_xline_size > 0.5*cropped_y_pixels_height:
        print("The y-axis is at x pixel ", x_pixel_line)
        print("The y-axis is ", longest_xline_size, " pixels long")
        
    else:
        messagebox.showinfo(title = "Get y-axis", message = "Double click at the origin and the end of the y-axis")
        click_img_y_axis(cropped_img)
        print(y_axis_pos)
        x_pixel_line = y_axis_pos[0][0]
        longest_xline_size = y_axis_pos[0][1] - y_axis_pos[1][1]
        print("The y-axis is at x pixel ", x_pixel_line)
        print("The y-axis is ", longest_xline_size, " pixels long")
        y_axis_exists = True
      

    # makes a text file with all the y and x coordinates of the pixels under the threshold
    # with open('listfile.txt', 'w') as filehandle:
    #     for listitem in ylist:
    #         filehandle.write('%s\n' % listitem)
    # print("ffff", x_axis_exists)
    return y_pixel_line, x_pixel_line, longest_yline_size, longest_xline_size, x_axis_exists, y_axis_exists, origin


def click_img_x_axis(cropped_img):
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', get_x_axis)
    cv2.imshow('image', cropped_img)
    #cv2.circle(cropped_img, (x_axis_pos[0], 5, (255, 0, 0)))
    cv2.waitKey(0)
    if len(x_axis_pos) == 2:
        cv2.destroyAllWindows()


def click_img_y_axis(cropped_img):
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', get_y_axis)
    cv2.imshow('image', cropped_img)
    #cv2.circle(cropped_img, (x_axis_pos[0], 5, (255, 0, 0)))
    cv2.waitKey(0)
    if len(y_axis_pos) == 2:
        cv2.destroyAllWindows()


def get_xdata(cropped_img, y_pixel_line, x_pixel_line, x_axis_exists, y_axis_values, longest_yline_size, longest_xline_size):
    cropped_y_pixels_height = cropped_img.shape[0]
    cropped_x_pixels_width = cropped_img.shape[1]

    x_axis_img = cropped_img[y_pixel_line +
                             5: cropped_y_pixels_height, 0: cropped_x_pixels_width]

    # gets data from image
    d2 = pytesseract.image_to_data(x_axis_img, output_type=Output.DICT)
    text = d2['text']
    top = d2['top']
    left = d2['left']
    width = d2['width']
    cv2.imshow('image', x_axis_img)
    cv2.waitKey(0)
    print(d2)
    # the most common value in the top list should be the number of pixels from the bounding box to x-axis values

    # list that holds the x axis values
    x_axis_values = []

    # list that holds the x axis title
    x_axis_title = []

    # list that holds the pixel value of the median of the box that surrounds each x-axis value
    x_axis_value_medians = []

    # dictionary that holds the lines and the positions of the datapoints that exist on the graph
    line_data = {}

    # holds the minimum point for each line
    min_points = {}

    # holds the maximum point for each line
    max_points = {}

    # holds the coordinates of the x-axis values
    x_axis_value_datapoints = []

    # holds all the colors in one list that appear on the graph
    new_datapoints_colors = []

    # holds the colors in a list of lists, each sublist has a number of colors equal to the number of lines,
    # the length of the list is the number of x-axis values
    final_colors = []

    # holds the coordinates where colors appear on the graph, has a sublist with length equal to the number of lines
    # the length of the list is the number of x-axis values
    new_datapoints = []

    # holds a sublist with tuples containing all the y coordinate value and a number corresponding to the line number.
    # eg [(1, 151), (2, 149)] where 151 and 149 are the y coordinates for the first two lines on the graph
    line_positions = []

    # the number of lines on the graph is stored in num_lines
    num_lines = 0

    not_space = ''
    space = ''

    # if the value in text is not '' then add its value to not_space and break the loop
    for i in range(len(text)):
        if text[i].isdigit() or text[i].isalpha():
            not_space += text[i]
        if not_space != '':
            break

    # the first index where an x-axis value appears in text
    first_value = text.index(not_space)
    last_value = 0
    text = text[first_value:]

    # the next index where a space occurs after the x-axis values are finished
    if space in text:
        last_value = text.index(space)
    else:
        last_value = -1

    # a sliced list to the next index where a space occurs
    xvalues_text = text[:last_value]

    # if any character in the x-axis values is not a digit or alpha character then remove it
    for i in range(len(xvalues_text)):
        for x in xvalues_text[i]:
            if not x.isdigit() or not x.isalpha():
                new = re.sub('[^a-zA-Z0-9_]', '', xvalues_text[i])
                xvalues_text.remove(xvalues_text[i])
                xvalues_text.insert(i, new)

    # all the values that are not a space should be added to the x_axis_values list
    for i in xvalues_text:
        if i != '' and i.isdigit() or i.isalpha():
            x_axis_values.append(i)

    # a sliced list from the value after the last space value appears to the end of the list
    values_after_xvalues_text = text[last_value:]

    # all the values that are not a space that occur after the x axis values
    for i in values_after_xvalues_text:
        if i != '':
            x_axis_title.append(i)

    # the points where the x axis values appear on the x axis should be this many pixels
    # key_x_axis_values = round(longest_line_size / len(x_axis_values))
    # print("Every ", key_x_axis_values, " pixels there is a key point")

    # the number of pixels each x-axis value box is from the left
    left = left[first_value:]

    # the width of each box around the x-axis values
    width = width[first_value:]
    print("x-axis title", x_axis_title)
    print("x-axis values ", x_axis_values)

    # finds the median pixel for each x-axis value box
    for i in range(len(x_axis_values)):
        median = round(left[i] + round(width[i] / 2))
        x_axis_value_medians.append(median)

    # holds the x pixel value for the median of each x-axis value box
    x_axis_points = 0

    # adds the median x pixel values for each x-axis value box to x_axis_value_datapoints
    if len(x_axis_value_medians) > 0:
        x_axis_points = x_axis_value_medians[0]
        x_axis_value_datapoints.append(x_axis_points)

   # for each line the coordinates and the colors at those coordinates are saved in new_datapoints and new_datapoints_colors
    for i in range(len(x_axis_value_medians)):
        x_axis_points = x_axis_value_medians[i]
        res, col, top_of_graph, fin_col = get_line_positions(
            cropped_img, x_axis_exists, y_pixel_line, longest_xline_size, x_axis_points)
        new_datapoints.append(res)
        new_datapoints_colors.append(col)
        final_colors.append(fin_col)

    # num_lines is found by getting the most common length of the sublists in new_datapoints
    # new_datapoints is a list made up of sublists containing the coordinates of a color pixel for each x-axis value
    # eg [[[73, 151], [73, 191]], [[103, 159], [103, 202]], [[133, 145], [133, 156]]] this list has two lines and
    # 3 x-axis values
    most_common_list = []
    for i in range(len(new_datapoints)):
        for j in range(len(new_datapoints[i])):
            most_common_list.append(len(new_datapoints[i]))
    most_common = max(set(most_common_list), key=most_common_list.count)
    num_lines = most_common

    # colors are being stored in this dict. If the colors at the first x-axis value are not equal to the actual number
    # of lines, eg if a datapoint is covered by another, check several lines
    line_colors_dict = {}
    line = 1
    for i in range(num_lines):
        if len(new_datapoints_colors[0]) == num_lines and new_datapoints_colors[0][i][0] != None:
            line_colors_dict[line] = new_datapoints_colors[0][i]
            line += 1
        elif len(new_datapoints_colors[1]) == num_lines and new_datapoints_colors[1][i][0] != None:
            line_colors_dict[line] = new_datapoints_colors[1][i]
            line += 1
        elif len(new_datapoints_colors[2]) == num_lines and new_datapoints_colors[2][i][0] != None:
            line_colors_dict[line] = new_datapoints_colors[2][i]
            line += 1
    print('A', line_colors_dict)

    # if there are less values in the new_datapoints list than there are lines, append "None" to the list to show the
    # system could not get any data
    for i in range(len(new_datapoints)):
        if len(new_datapoints[i]) < num_lines:
            diff = num_lines - len(new_datapoints[i])
            for j in range(diff):
                new_datapoints[i].append([None, None])
                final_colors[i].append([[None, None], [None, None, None]])
                new_datapoints_colors[i].append([None, None, None])

    print('s', num_lines, "\n")
    print('f', new_datapoints_colors[0])
    '''
    for i in range(len(final_colors)):
        print('new', final_colors[i], "\n")
    '''
    print('most', new_datapoints)

    buffer = 50
    correct_final_colors = [[] for k in range(num_lines)]
    # iterate over the number of x-axis values
    for i in range(len(final_colors)):

        # iterate over the number of points on the graph per x-axis value
        for j in range(num_lines):

            first_val = list(line_colors_dict.values())[j]
            print('lll', first_val, j)
            print('asdf', final_colors[i][j][1], "\n")
            if None in final_colors[i][j][1]:
                correct_final_colors[j].append(
                    [[None, None], [None, None, None]])
                print('fd', correct_final_colors[j], "\n")

            else:
                color_index = 0
                # iterate over each datapoint and corresponding color to see if the color matches one in line_colors_dict
                for k in range(num_lines):
                    print('yoyo', final_colors[i][k][1])
                    if None in final_colors[i][k][1]:
                        pass
                    else:
                        # if the colors match a color in the line_colors_dict then append them to their own sublist
                        if int(final_colors[i][k][1][0]) in range(int(first_val[0]-buffer), int(first_val[0]+buffer)) \
                                and int(final_colors[i][k][1][1]) in range(int(first_val[1]-buffer), int(first_val[1]+buffer)) \
                                and int(final_colors[i][k][1][2]) in range(int(first_val[2]-buffer), int(first_val[2]+buffer)):
                            correct_final_colors[j].append(final_colors[i][k])
                            print('kj', correct_final_colors[j], "\n")
                            color_index += 1
                if color_index == 0:

                    correct_final_colors[j].append(
                        [[None, None], [None, None, None]])

    for i in range(len(correct_final_colors)):
        print(i)
        print('ppp', correct_final_colors[i], "\n")

    print('ggggggggg', len(correct_final_colors[0]))
    # a list with sublists. number of sublists is determined by the number of lines
    line_positions = [[] for k in range(num_lines)]
    yAxis_values = []
    yAxis_values = calculate_yAxis_values(
        cropped_img, y_pixel_line, new_datapoints, correct_final_colors, num_lines, y_axis_values, top_of_graph)

    print('yyy', yAxis_values)
    # each sublist in line_positions represents each line's y coordinates and a number from 1 to the number of x-axis values
    # eg [[(1, 213), (2, 222)], (1,124), (2, 211)] there are two lines and two x-axis values. the value on the right in
    # the tuple indicates the y coordinate at the corresponding x-axis value
    val = 0
    for i in range(len(new_datapoints)):
        val += 1
        for j in range(num_lines):
            line_positions[j].append(
                (val, yAxis_values[j][i]))

    # line_data gets keys based on the number of lines and the values are line_positions values
    # min and max points are dictionaries containing the min and max value for each line
    for i in range(num_lines):
        line_data[i+1] = line_positions[i]
        min_points[i+1] = None
        max_points[i+1] = None

    print("Line data: ", line_data)

    min_position = [[] for k in range(num_lines)]
    max_position = [[] for k in range(num_lines)]
    for i in range(len(line_data)):
        for j in range(len(line_data[i+1])):
            y = line_data[i+1][j][1]
            if y != None:
                min_position[i].append((y))
                print('dddssss', min_position[i])
            if y != None:
                max_position[i].append((y))
        min_points[i+1] = (min(min_position[i]))
        max_points[i+1] = (max(max_position[i]))
    print(min_points)
    print(max_points)

    '''
    print("The points where colors exist are at x, y pixel: ", new_datapoints)
    print("The colors at the corresponding positions are: ", new_datapoints_colors)
    '''
    # the data from the graph has boxes created around it
    n_boxes2 = len(d2['level'])
    for i in range(n_boxes2):
        (x, y, w, h) = (d2['left'][i], d2['top']
                        [i], d2['width'][i], d2['height'][i])
        cv2.rectangle(x_axis_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # cv2.imshow('image', x_axis_img)
    # cv2.waitKey(0)

    return line_data, x_axis_values, num_lines, x_axis_title


def get_ydata(cropped_img, x_pixel_line, y_pixel_line, y_axis_exists, longest_xline_size):
    cropped_y_pixels_height = cropped_img.shape[0]
    cropped_x_pixels_width = cropped_img.shape[1]

    y_axis_img = cropped_img[0: y_pixel_line + 10, 0: x_pixel_line-5]


    # gets data from image
    d2 = pytesseract.image_to_data(y_axis_img, output_type=Output.DICT)
    text = d2['text']
    top = d2['top']
    left = d2['left']
    width = d2['width']

    # print(d2)

    # the most common value in the top list should be the number of pixels from the bounding box to x-axis values
    most_common = max(set(left), key=left.count)

    # list that holds the x axis values
    y_axis_values = []

    # list that holds the x axis title
    y_axis_title = []

    # list that holds the pixel value of the median of the box that surrounds each y-axis value
    y_axis_value_medians = []

    separated_text = []
    new_text = []

    # all the values that are not a space should be added to the x_axis_values list
    for i in text:
        if i != '':
            new_text.append(i)

            for i in range(len(new_text)):
                separated_text.append(list(new_text[i]))

            for i in range(len(separated_text)):
                for j in range(len(separated_text[i])):
                    if separated_text[i][j] == 'o' or separated_text[i][j] == 'O':
                        separated_text[i][j] = '0'
                    if separated_text[i][j] == 's' or separated_text[i][j] == 'S':
                        separated_text[i][j] = '5'
            # print("".join(separated_text[i]))
            if separated_text[i][j].isdigit():
                y_axis_values.append("".join(separated_text[i]))
            else:
                y_axis_title.append(separated_text[i][j])

    # all the values that are not a space that occur after the x axis values
    for i in text:
        if i != ''and i.isalpha():
            y_axis_title.append(i)

    print("y-axis values", y_axis_values)
    print("y-axis title", y_axis_title)

    for i in range(len(y_axis_values)):
        median = round(top[i] + round(width[i] / 2))
        y_axis_value_medians.append(median)

    n_boxes2 = len(d2['level'])
    for i in range(n_boxes2):
        (x, y, w, h) = (d2['left'][i], d2['top']
                        [i], d2['width'][i], d2['height'][i])
        cv2.rectangle(y_axis_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # cv2.imshow('image', y_axis_img)
    # cv2.waitKey(0)
    biggest_max = y_axis_values[0]

    return y_axis_values, biggest_max, y_axis_title


def get_line_positions(cropped_img, x_axis_exists, y_pixel_line, longest_xline_size, x_axis_points):
    colors = []
    color_positions = []
    final_colors = []
    datapoints = []
    datapoints_colors = []
    # new_datapoints holds the correct datapoints
    new_datapoints = []
    # new_datapoints_colors holds the correct datapoints colors
    new_datapoints_colors = []

    top_of_graph = 0
    if x_axis_exists:
        top_of_graph = y_pixel_line - longest_xline_size
    else:
        top_of_graph = y_pixel_line - longest_xline_size

    if top_of_graph < 0:
        top_of_graph = 0

    for i in range(int(top_of_graph), int(y_pixel_line)):
        pix = cropped_img[i, x_axis_points]
        if pix[0] > 230 and pix[1] > 230 and pix[2] > 230 or pix[0] < 30 and pix[1] < 30 and pix[2] < 30:
            continue
        else:
            color_positions.append([x_axis_points, i])
            # cropped_img[151, 73] = (0, 0, 0)
            colors.append(list(pix))

    # finds the consecutive y pixel values and groups them into lists
    for i in range(len(color_positions)):
        if color_positions[i-1][1] + 1 == color_positions[i][1]:
            datapoints[-1].append(color_positions[i][1])

        else:
            datapoints.append([color_positions[i][1]])

    # add colors to the datapoints_colors
    for i in range(len(colors)):
        if colors[i-1] == colors[i]:
            datapoints_colors[-1].append(colors[i])
        else:
            datapoints_colors.append([colors[i]])

    # if a datapoint has more than 2 pixel values that means it has more than 2 consecutive pixel values.
    # add those values to a new list
    for i in range(len(datapoints)):
        if len(datapoints[i]) > 2:
            new_datapoints.append(datapoints[i])

    # finds the median y pixel value for each datapoint and replaces the consecutive value lists with the median
    for i in range(len(new_datapoints)):
        median = math.ceil(statistics.median(new_datapoints[i]))
        new_datapoints.remove(new_datapoints[i])
        new_datapoints.insert(i, [x_axis_points, median])

    # add to a new list the colors that appear at the specified datapoints
    for i in range(len(new_datapoints)):
        # colors at the positions where datapoints exist
        d = cropped_img[new_datapoints[i][1], x_axis_points]
        if d[0] > 230 and d[1] > 230 and d[2] > 230:
            continue
        else:
            new_datapoints_colors.append(d)

    for i in range(len(new_datapoints)):

        final_colors.append(
            [new_datapoints[i], new_datapoints_colors[i]])

    return new_datapoints, new_datapoints_colors, top_of_graph, final_colors


def calculate_yAxis_values(cropped_img, y_pixel_line, new_datapoints, correct_final_colors, num_lines, y_axis_values, top_of_graph):
    cropped_y_pixels_height = cropped_img.shape[0]
    cropped_x_pixels_width = cropped_img.shape[1]

    top_of_graph = cropped_y_pixels_height - top_of_graph
    y_pixel_line = cropped_y_pixels_height - y_pixel_line
    datapoints = [[] for k in range(num_lines)]
    distance_from_top_to_x_axis = top_of_graph - y_pixel_line
    pixels_divider = distance_from_top_to_x_axis / float(y_axis_values[0])

    '''
    for i in range(len(correct_final_colors)):
        print('ya', correct_final_colors[i], "\n")
    '''
    print(len(new_datapoints), len(new_datapoints[0]))
    for i in range(len(new_datapoints)):
        for j in range(len(new_datapoints[0])):
            print(correct_final_colors[j][i][0])
            if correct_final_colors[j][i][0][1] == None:
                datapoints[j].append(None)
            else:
                yAxis_values = round(
                    ((cropped_y_pixels_height - float(correct_final_colors[j][i][0][1])) - y_pixel_line) / pixels_divider, 2)

                datapoints[j].append(yAxis_values)
    return datapoints


def get_x_axis(event, x, y, flags, param):
    global x_axis_pos
    if event == cv2.EVENT_LBUTTONDBLCLK:
        x_axis_pos.append((x, y))
    if len(x_axis_pos) == 2:
        cv2.destroyAllWindows()
        


def get_y_axis(event, x, y, flags, param):
    global y_axis_pos
    if event == cv2.EVENT_LBUTTONDBLCLK:
        y_axis_pos.append((x, y))
    if len(y_axis_pos) == 2:
        cv2.destroyAllWindows()



def get_graph_title(cropped_img):

    cropped_y_pixels_height = cropped_img.shape[0]
    cropped_x_pixels_width = cropped_img.shape[1]
    
    cropped_img = cropped_img[0: round(
        cropped_y_pixels_height*0.3), 0: cropped_x_pixels_width]

    image_to_text = pytesseract.image_to_string(cropped_img, lang='eng')

    GraphTitle = []  # Will hold the chars of the tile
    iter1 = 0  # set i to 0, to look at the first char of the title
    current_char = ''  # set the current char to start the loop
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '\n']

    while True:
        if image_to_text[iter1] in numbers:
            iter1 += 1
        else:
            current_char = image_to_text[iter1]
            break

    while current_char != '\n':
        GraphTitle.append(image_to_text[iter1])  # get the chars of the title
        iter1 += 1
        if iter1 < len(image_to_text):
            current_char = image_to_text[iter1]
        else:
            break

    # strips the '' from the array of title chars.
    JoinedGraphTitle = ''.join(GraphTitle)
    # print(JoinedGraphTitle)
    return JoinedGraphTitle


## End oF Functions ##


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

play_entire_graph_desc = tk.Button(master=background, text='Explain Graph',
                                   width=19, command=read_text_file)

tutorial_button = tk.Button(master=background, text='Tutorial',
                            width=19, command=play_tutorial)

load_previous_graph = tk.Button(master=background, text='Load Previous Graph',
                                width=19, command=load_previous_graph)

pause_play_button = tk.Button(master=background, text='Pause / Play',
                              width=19, command=play_pause)

replay_button = tk.Button(
    master=background, text='Replay', width=19, command=replay)

exit_button = tk.Button(master=background, text='Exit AGR',
                        width=19, command=exitAGR)

line_1_button = tk.Button(master=background, text='Line 1',
                          width=8, command=lambda: play_line_desc(1))

line_2_button = tk.Button(master=background, text='Line 2',
                          width=8, command=lambda: play_line_desc(2))

line_3_button = tk.Button(master=background, text='Line 3',
                          width=8, command=lambda: play_line_desc(3))

line_4_button = tk.Button(master=background, text='Line 4',
                          width=8, command=lambda: play_line_desc(4))

line_5_button = tk.Button(master=background, text='Line 5',
                          width=8, command=lambda: play_line_desc(5))

line_6_button = tk.Button(master=background, text='Line 6',
                          width=8, command=lambda: play_line_desc(6))

line_7_button = tk.Button(master=background, text='Line 7',
                          width=8, command=lambda: play_line_desc(7))

line_8_button = tk.Button(master=background, text='Line 8',
                          width=8, command=lambda: play_line_desc(8))


upload_button.place(x=30, y=120)
play_entire_graph_desc.place(x=30, y=180)
tutorial_button.place(x=30, y=240)
load_previous_graph.place(x=30, y=300)
pause_play_button.place(x=30, y=360)
replay_button.place(x=30, y=420)
exit_button.place(x=30, y=640)

replay_button["state"] = "disabled"
load_previous_graph["state"] = "disabled"
pause_play_button["state"] = "disabled"

# TODO
# Verify file path
# Add hotkey for entire graph description
# Add hotkey for general graph info apart from data (ie graph title, num lines, etc)
# Add functionality to grab proper files (.wav .json ...) from folder on old graph load
#

# Once analyzed
remove_line_desc_buttons(8)

# And place buttons using num_lines
# place_line_desc_buttons(num_lines)


GUI.bind("<Key>", key)  # calls key (function above) on Keyboard input
GUI.resizable(False, False)

GUI.mainloop()


# stop stream
stream.stop_stream()
stream.close()
wf.close()

# close PyAudio
p.terminate()