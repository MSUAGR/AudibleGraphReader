#!/usr/bin/env python3
# utf-8

# The Audible Graph Reader Project
# Copyright 2020 Missouri State University

# 5.6.2020

# User must install pytesseract version 5

# The following  must exist in same dir as this file:
#       blank.wav, tutorial.wav, tonal_intro.wav, ffmpeg.exe, 
#       agr.ico, AGRHorizontalLogo.png

# USE: ./AGR.py

import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar
from tkinter import ttk
from PIL import ImageTk, Image, ImageEnhance
import pyaudio  
import wave     # Handling wave sound files
import time
import os
from gtts import gTTS
import cv2      # For image processing
import sys
from datetime import datetime
import glob
import json
import ntpath  # To interact with filepath
import shutil  # High level file operations (cp img)
import numpy as np
from collections import OrderedDict
from operator import itemgetter
import pytesseract  # OCR
from pytesseract import Output
import re       # Regular Expressions
import statistics
import math
from itertools import islice
from stat import S_IREAD, S_IRGRP, S_IROTH  # allows os for read only
import subprocess
import platform  # allows dev to check what os user is running
import threading
from statistics import mean
from tones import SINE_WAVE     # For creating sounds as tonal descriptions
from tones.mixer import Mixer
from langdetect import detect_langs
from langdetect import DetectorFactory
DetectorFactory.seed = 0

user_platform = platform.platform()
user_os = user_platform.split('.')[0]
if 'Windows-10' in user_os:
    print(' info: Accepted OS')
else:
    print(' ERROR: Operating System not accepted!')
    print(' press enter key to exit...')
    input()
    sys.exit()

# Global
ref_points = []
playing_bool = False
global file_path
global path
global program_path
global err_count
global draw_axes_img
global draw_axes_img_redo
global tonal_enabled

tonal_enabled = False
program_path = os.getcwd()
sound_file = ''
GUI = tk.Tk()
GUI.iconbitmap('agr.ico')
s = ttk.Style()
s.theme_use('clam')
s.configure("light_blue.Horizontal.TProgressbar",
            foreground='white', background='#ADD8E6')

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

## Begin GUI Functions ##


def upload():
    t1 = threading.Thread(target=t_upload, args=())
    t1.start()


def wait():
    messagebox.showinfo(
        title="Waiting", message="The system is taking longer than expected")


def t_upload():
    global load_previous_graph_button
    global play_entire_graph_desc_button
    global sound_file
    global prog_bar
    global path
    # To allow disabling buttons
    global upload_button
    global tutorial_button
    global pause_play_button
    global replay_button
    global exit_button
    global playing_bool
    global draw_axes_img
    global draw_axes_img_redo

    if stream.is_active():
        print(' info: stream paused for new upload')
        stream.stop_stream()
        playing_bool = False

    file_path = filedialog.askopenfilename(title="Select Graph Image", filetypes=[
        ("Image Files", ".png .jpg .gif .img .jpeg")])

    if os.path.isfile(file_path):
        remove_line_desc_buttons(8)

        try:
            img = Image.open(file_path)
            img.verify()
            img = Image.open(file_path)
        except:
            print('Bad files: ', file_path)
            messagebox.showerror(
                title="AGR:Error", message="File is corrupted.")
            return -1

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

            prog_bar["value"] = 0
            proc_label.place(x=85, y=60)
            prog_bar.place(x=30, y=90)
            prog_bar.step(10)  # 10%
            background.update()

            # Prevent extra input from the user
            upload_button["state"] = "disabled"
            play_entire_graph_desc_button["state"] = "disabled"
            tutorial_button["state"] = "disabled"
            load_previous_graph_button["state"] = "disabled"
            pause_play_button["state"] = "disabled"
            replay_button["state"] = "disabled"
            exit_button["state"] = "disabled"

            now = datetime.now()
            timestamp = str(round(datetime.timestamp(now)))

            new_file_name = og_file_name + "." + timestamp

            desktop = os.path.normpath(os.path.expanduser("~/Desktop"))
            ffmpeg_dest_path = desktop + "/AGR"
            ffmpeg_src_path = program_path + r'\ffmpeg.exe'
            path = desktop + "/AGR/Graphs/" + new_file_name + "/"

            try:
                os.makedirs(path)  # Create all necessary directories
            except OSError:
                print(" Error: Creation of the directory %s failed" % path)
            else:
                print(" info: Successfully created the directory %s" % path)

            shutil.copy(file_path, path)
            shutil.copy(ffmpeg_src_path, ffmpeg_dest_path)

            # change wrk dir to path of desktop
            os.chdir(path)

            # check if img is png
            if og_file_name[-4:] in {'.png'}:

                img = Image.open(og_file_name)
                img = cv2.imread(og_file_name)
                draw_axes_img = img.copy()
                draw_axes_img_redo = img.copy()
                name_no_ext = og_file_name.split('.')
            else:
                name_no_ext = og_file_name.split('.')
                # print("nameNoext: ", name_no_ext[0])  # nameNoext:  image4
                img = Image.open(og_file_name).save(
                    path + name_no_ext[0] + '.png')
                img = Image.open(og_file_name).save(
                    path + name_no_ext[0] + '.png')
                img = cv2.imread(name_no_ext[0] + '.png')
                draw_axes_img = img.copy()
                draw_axes_img_redo = img.copy()

            img_size = img.shape
            print(' info: Image Size: ', img_size)
            y_pixels_height = img.shape[0]
            x_pixels_width = img.shape[1]
            crop_img = img
            x_axis_exists = True
            y_axis_exists = True

            prog_bar.step(10)  # 20%
            background.update()

            cropped_x_axis = crop_img[round(
                y_pixels_height*0.7): y_pixels_height, 0: x_pixels_width]

            cropped_y_axis = crop_img[0: y_pixels_height, 0: round(
                x_pixels_width*0.3)]

            xcoords, ycoords = find_coords(cropped_x_axis, cropped_y_axis)

            prog_bar.step(10)  # 30%
            background.update()

            img = Image.open(file_path)
            if img.size[0] > 690 or img.size[1] > 545:
                img = img.resize((690, 545), Image.ANTIALIAS)
            openImg = ImageTk.PhotoImage(img)
            image = tk.Label(master=background, width=690,
                             height=505, image=openImg)
            image.image = openImg
            image.place(x=160, y=120)
            print(' info: ' + os.path.normpath(file_path) +
                  " has been opened in the preview window")

            y_pixel_line, x_pixel_line, longest_yline_size, longest_xline_size, x_axis_exists, y_axis_exists, origin = store_coords(
                crop_img, xcoords, ycoords, x_pixels_width, y_pixels_height, x_axis_exists, y_axis_exists)
            t2 = threading.Timer(30, wait)
            t2.start()
            try:
                y_axis_values, biggest_max, smallest_min, y_axis_title = get_ydata(
                    crop_img, x_pixel_line, y_pixel_line, y_axis_exists, longest_xline_size)
            except:
                t2.cancel()
                print('The y-axis data could not be found')
                messagebox.showerror(
                    title="AGR:Error", message="The y-axis data could not be found.")
                os.chdir('..')
                shutil.rmtree(path)
                print("Bad image directory deleted")
                proc_label.place_forget()
                prog_bar.place_forget()
                image.place_forget()
                upload_button["state"] = "normal"
                tutorial_button["state"] = "normal"
                load_previous_graph_button["state"] = "normal"
                exit_button["state"] = "normal"
                return -1

            try:
                x_axis_values, x_axis_title, x_axis_value_medians = get_xdata(crop_img, y_pixel_line, x_pixel_line,
                    x_axis_exists, y_axis_values, longest_yline_size, longest_xline_size)
            except:
                t2.cancel()
                print("The x-axis data could not be found.")
                messagebox.showerror(
                    title="AGR:Error", message="The x-axis data could not be found.")
                os.chdir('..')
                shutil.rmtree(path)
                print("Bad image directory deleted")
                proc_label.place_forget()
                prog_bar.place_forget()
                image.place_forget()
                upload_button["state"] = "normal"
                tutorial_button["state"] = "normal"
                load_previous_graph_button["state"] = "normal"
                exit_button["state"] = "normal"
                return -1

            try:
                line_data, num_lines, line_colors_dict = get_datapoints(crop_img, x_axis_exists, 
                    longest_xline_size, x_axis_values, x_axis_value_medians, y_pixel_line, y_axis_values)
            except:
                t2.cancel()
                print("The datapoints could not be found.")
                messagebox.showerror(
                    title="AGR:Error", message="The datapoints could not be found.")
                os.chdir('..')
                shutil.rmtree(path)
                print("Bad image directory deleted")
                proc_label.place_forget()
                prog_bar.place_forget()
                image.place_forget()
                upload_button["state"] = "normal"
                tutorial_button["state"] = "normal"
                load_previous_graph_button["state"] = "normal"
                exit_button["state"] = "normal"
                return -1

            # ASSIGN VARIABLES
            for i in range(len(x_axis_title)):
                xAxis_title = ''
                xAxis_title += x_axis_title[i] + ' '

            for i in range(len(y_axis_title)):
                yAxis_title = ''
                yAxis_title += y_axis_title[i] + ' '

            # X_AXIS_MIN = 0
            J_GRAPH_TITLE = str(get_graph_title(
                (str(name_no_ext[0]) + '.png')))
            J_X_AXIS_TITLE = xAxis_title
            J_Y_AXIS_TITLE = yAxis_title
            J_X_AXIS_VALUES = x_axis_values
            J_Y_AXIS_VALUES = y_axis_values
            J_ORIGIN = str(origin)
            J_NUM_LINES = str(num_lines)
            J_FOUND_COLORS = line_colors_dict
            J_DATA_POINTS = line_data

            all_text = J_X_AXIS_TITLE + J_Y_AXIS_TITLE + J_GRAPH_TITLE

            try:
                # custom_config = r'-l grc+tha+eng --psm 6'
                # my_string = pytesseract.image_to_string(crop_img, config=custom_config)
                # pytesseract.image_to_string(crop_img)#, lang='eng')
                # Language object Output: image4.gif langlist =  [en:0.5714262601246318, it:0.4285717316776206]
                lang_list = detect_langs(all_text)
                lang_found = False

                for item in lang_list:
                    if item.lang == 'en' and item.prob > 0.5:
                        lang_found = True

                if lang_found == False:
                    print("BAD INPUT: Language other than english is dominant language")
                    raise Exception("Language is not English")
                else:
                    print(" info: Found English text")
            except:
                t2.cancel()
                print("The most prominent language is not English.")
                messagebox.showerror(
                    title="AGR:Error", message="The most prominent language is not English.")
                os.chdir('..')
                shutil.rmtree(path)
                print(" info: Bad image directory deleted")
                proc_label.place_forget()
                prog_bar.place_forget()
                image.place_forget()
                upload_button["state"] = "normal"
                tutorial_button["state"] = "normal"
                load_previous_graph_button["state"] = "normal"
                exit_button["state"] = "normal"
                return -1

            # pass dict of points
            trend_line_dict, slope_strings, intersections_dict = getIntersections(
                line_data, x_axis_values, num_lines, biggest_max)

            prog_bar.step(10)  # 40%
            background.update()

            x = {
                "image_name": new_file_name,
                "main_title": J_GRAPH_TITLE,  # STRING
                "x_axis_title": J_X_AXIS_TITLE,  # STRING
                "x_axis_values": J_X_AXIS_VALUES,  # LIST
                "y_axis_title": J_Y_AXIS_TITLE,  # STRING
                "y_axis_values": J_Y_AXIS_VALUES,  # LIST
                "num_lines": J_NUM_LINES,   
                "found_colors": J_FOUND_COLORS,  # LIST OF RGB
                "data_points": J_DATA_POINTS,  # LIST OF TUPLES
                "origin": J_ORIGIN  # TUPLE
            }

            try:
                f = open(path + "graph.json", 'w')  # Create .json file
            except:
                print(" Error: JSON file creation failed")
            else:
                print(" info: Successfully created .json")

            try:
                jsonData = json.dumps(x,  indent=2)  # with newline
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

            aud_text = ''
        
            if J_GRAPH_TITLE == 'None':
                aud_text += "The graph title could not be found. \n"
            else:
                aud_text += "The graph is titled " + J_GRAPH_TITLE + ". \n"

            if J_X_AXIS_TITLE == 'None':
                aud_text += "The x-axis title could not be found. \n"
            else:
                aud_text += "The x-axis is titled "
                for i in range(len(x_axis_title)):
                    aud_text += x_axis_title[i] + ' '
                aud_text += ". \n"

            if J_X_AXIS_VALUES == None:
                aud_text += "The x-axis values could not be found. \n"
            else:
                aud_text += "The x-axis values are "
                for i in range(len(x_axis_values)):
                    aud_text += x_axis_values[i] + ', '
                aud_text += ". \n"

            if J_Y_AXIS_TITLE == 'None':
                aud_text += "The y-axis title could not be found. \n"
            else:
                aud_text += "The y-axis is titled "
                for i in range(len(y_axis_title)):
                    aud_text += y_axis_title[i] + ' '
                aud_text += ". \n"

            if J_Y_AXIS_VALUES == None:
                aud_text += "The y-axis values could not be found. \n"
            else:
                aud_text += "The y-axis values are "
                for i in range(len(y_axis_values)):
                    aud_text += y_axis_values[i] + ', '
                aud_text += ". \n"

            if J_NUM_LINES == None:
                aud_text += "The number of lines on the graph could not be found. \n"
            else:
                aud_text += "There are " + J_NUM_LINES + " lines on the graph. \n"

            print()  # Formatting in console...

            # Create the tonal description of the lines

            # Create mixers, set sample rate and amplitude
            mixer = Mixer(48000, 0.5)
            mixer2 = Mixer(48000, 0.5)
            mixer3 = Mixer(48000, 0.5)
            mixer4 = Mixer(48000, 0.5)
            mixer5 = Mixer(48000, 0.5)
            mixer6 = Mixer(48000, 0.5)
            mixer7 = Mixer(48000, 0.5)
            mixer8 = Mixer(48000, 0.5)

            smallest_min = 0
            biggest_max = float(biggest_max)

            max_frequency = 600  # D5
            min_frequency = 200  # G3

            lines_vals = line_data.items()
            mixer.create_track(1, SINE_WAVE, attack=0.005)
            mixer2.create_track(1, SINE_WAVE, attack=0.005)
            mixer3.create_track(1, SINE_WAVE, attack=0.005)
            mixer4.create_track(1, SINE_WAVE, attack=0.005)
            mixer5.create_track(1, SINE_WAVE, attack=0.005)
            mixer6.create_track(1, SINE_WAVE, attack=0.005)
            mixer7.create_track(1, SINE_WAVE, attack=0.005)
            mixer8.create_track(1, SINE_WAVE, attack=0.005)
            for key, values in lines_vals:
                for i in range(len(values)):
                    if key == 1:
                        x = values[i][0]
                        y = values[i][1]
                        print("key: " + str(key) + " x: " +
                              str(x) + " y: " + str(y))
                        if y == None:
                            mixer.add_silence(1, duration=0.4)
                        else:
                            tone_frequency = (
                                (max_frequency - min_frequency)*(y/(biggest_max - smallest_min))) + min_frequency
                            mixer.add_tone(
                                1, frequency=tone_frequency, duration=0.25)
                            mixer.add_silence(1, duration=0.15)
                    if key == 2:
                        x = values[i][0]
                        y = values[i][1]
                        print("key: " + str(key) + " x: " +
                              str(x) + " y: " + str(y))
                        if y == None:
                            mixer.add_silence(1, duration=0.4)
                        else:
                            tone_frequency = (
                                (max_frequency - min_frequency)*(y/(biggest_max - smallest_min))) + min_frequency
                            mixer2.add_tone(
                                1, frequency=tone_frequency, duration=0.25)
                            mixer2.add_silence(1, duration=0.15)
                    if key == 3:
                        x = values[i][0]
                        y = values[i][1]
                        print("key: " + str(key) + " x: " +
                              str(x) + " y: " + str(y))
                        if y == None:
                            mixer.add_silence(1, duration=0.4)
                        else:
                            tone_frequency = (
                                (max_frequency - min_frequency)*(y/(biggest_max - smallest_min))) + min_frequency
                            mixer3.add_tone(
                                1, frequency=tone_frequency, duration=0.25)
                            mixer3.add_silence(1, duration=0.15)
                    if key == 4:
                        x = values[i][0]
                        y = values[i][1]
                        print("key: " + str(key) + " x: " +
                              str(x) + " y: " + str(y))
                        if y == None:
                            mixer.add_silence(1, duration=0.4)
                        else:
                            tone_frequency = (
                                (max_frequency - min_frequency)*(y/(biggest_max - smallest_min))) + min_frequency
                            mixer4.add_tone(
                                1, frequency=tone_frequency, duration=0.25)
                            mixer4.add_silence(1, duration=0.15)
                    if key == 5:
                        x = values[i][0]
                        y = values[i][1]
                        print("key: " + str(key) + " x: " +
                              str(x) + " y: " + str(y))
                        if y == None:
                            mixer.add_silence(1, duration=0.4)
                        else:
                            tone_frequency = (
                                (max_frequency - min_frequency)*(y/(biggest_max - smallest_min))) + min_frequency
                            mixer5.add_tone(
                                1, frequency=tone_frequency, duration=0.25)
                            mixer5.add_silence(1, duration=0.15)
                    if key == 6:
                        x = values[i][0]
                        y = values[i][1]
                        print("key: " + str(key) + " x: " +
                              str(x) + " y: " + str(y))
                        if y == None:
                            mixer.add_silence(1, duration=0.4)
                        else:
                            tone_frequency = (
                                (max_frequency - min_frequency)*(y/(biggest_max - smallest_min))) + min_frequency
                            mixer6.add_tone(
                                1, frequency=tone_frequency, duration=0.25)
                            mixer6.add_silence(1, duration=0.15)
                    if key == 7:
                        x = values[i][0]
                        y = values[i][1]
                        print("key: " + str(key) + " x: " +
                              str(x) + " y: " + str(y))
                        if y == None:
                            mixer.add_silence(1, duration=0.4)
                        else:
                            tone_frequency = (
                                (max_frequency - min_frequency)*(y/(biggest_max - smallest_min))) + min_frequency
                            mixer7.add_tone(
                                1, frequency=tone_frequency, duration=0.25)
                            mixer7.add_silence(1, duration=0.15)
                    if key == 8:
                        x = values[i][0]
                        y = values[i][1]
                        print("key: " + str(key) + " x: " +
                              str(x) + " y: " + str(y))
                        if y == None:
                            mixer.add_silence(1, duration=0.4)
                        else:
                            tone_frequency = (
                                (max_frequency - min_frequency)*(y/(biggest_max - smallest_min))) + min_frequency
                            mixer8.add_tone(
                                1, frequency=tone_frequency, duration=0.25)
                            mixer8.add_silence(1, duration=0.15)
            num_lines = len(line_data)

            if num_lines == 1:
                mixer.write_wav('tonal_1.wav')
            if num_lines == 2:
                mixer.write_wav('tonal_1.wav')
                mixer2.write_wav('tonal_2.wav')
            if num_lines == 3:
                mixer.write_wav('tonal_1.wav')
                mixer2.write_wav('tonal_2.wav')
                mixer3.write_wav('tonal_3.wav')
            if num_lines == 4:
                mixer.write_wav('tonal_1.wav')
                mixer2.write_wav('tonal_2.wav')
                mixer3.write_wav('tonal_3.wav')
                mixer4.write_wav('tonal_4.wav')
            if num_lines == 5:
                mixer.write_wav('tonal_1.wav')
                mixer2.write_wav('tonal_2.wav')
                mixer3.write_wav('tonal_3.wav')
                mixer4.write_wav('tonal_4.wav')
                mixer5.write_wav('tonal_5.wav')
            if num_lines == 6:
                mixer.write_wav('tonal_1.wav')
                mixer2.write_wav('tonal_2.wav')
                mixer3.write_wav('tonal_3.wav')
                mixer4.write_wav('tonal_4.wav')
                mixer5.write_wav('tonal_5.wav')
                mixer6.write_wav('tonal_6.wav')
            if num_lines == 7:
                mixer.write_wav('tonal_1.wav')
                mixer2.write_wav('tonal_2.wav')
                mixer3.write_wav('tonal_3.wav')
                mixer4.write_wav('tonal_4.wav')
                mixer5.write_wav('tonal_5.wav')
                mixer6.write_wav('tonal_6.wav')
                mixer7.write_wav('tonal_7.wav')
            if num_lines == 8:
                mixer.write_wav('tonal_1.wav')
                mixer2.write_wav('tonal_2.wav')
                mixer3.write_wav('tonal_3.wav')
                mixer4.write_wav('tonal_4.wav')
                mixer5.write_wav('tonal_5.wav')
                mixer6.write_wav('tonal_6.wav')
                mixer7.write_wav('tonal_7.wav')
                mixer8.write_wav('tonal_8.wav')

            line_string = 'No line data'
            # This section populates the string for each line that is converted to the wave file to be read aloud to the user
            for key, values in lines_vals:
                # lines_vals = [(xy), (xy), ....]
                ys = []
                for y in range(len(values)):
                    ys.append(values[y][1])
                m = best_fit_slope(ys)
                for i in range(len(values) - 1):
                    if i == 0:
                        j_array = []
                        if len(intersections_dict) > 0:
                            for j in range(len(intersections_dict[key])):
                                if intersections_dict[key][j][1] != None and intersections_dict[key][j][1] >= 1 and intersections_dict[key][j][1] <= 2:
                                    j_array.append(j)
                        line_string = "The general trend of line " + \
                            str(key) + " has a slope of " + str(m) + ".\n"
                        line_string += "Line " + str(key) + " starts at the x value of " + str(x_axis_values[i]) + " and the y value of " + str(values[i][1]) + " and " \
                            + slope_strings[key][i] + " " + \
                            str(values[i + 1][1]) + " with the x value of " + \
                            str(x_axis_values[i + 1])
                        if len(j_array) == 0:
                            line_string += ".\n"
                        else:
                            line_string += ", intersecting "
                            for j in j_array:
                                line_string += "with line " + \
                                    str(intersections_dict[key][j][0]) + " at " + str(
                                        intersections_dict[key][j][2]) + " between " + str(x_axis_values[i]) + " and " + str(x_axis_values[i + 1]) + " and "
                            line_string += ".\n"
                    elif i > 0 and i < len(values) - 2:
                        j_array = []
                        if len(intersections_dict) > 0:
                            for j in range(len(intersections_dict[key])):
                                if intersections_dict[key][j][1] != None and intersections_dict[key][j][1] >= (i + 1) and intersections_dict[key][j][1] <= (i + 2):
                                    j_array.append(j)
                        line_string += "Line " + \
                            str(key) + " then " + \
                            slope_strings[key][i] + " " + \
                            str(values[i + 1][1]) + " at the x value of " + \
                            str(x_axis_values[i + 1])
                        if len(j_array) == 0:
                            line_string += ".\n"
                        else:
                            for j in j_array:
                                line_string += "and intersects with line " + \
                                    str(intersections_dict[key][j][0]) + " at " + str(
                                        intersections_dict[key][j][2]) + " "
                            line_string += " between " + \
                                str(x_axis_values[i]) + " and " + \
                                str(x_axis_values[i + 1]) + ".\n"
                    else:
                        j_array = []
                        if len(intersections_dict) > 0:
                            for j in range(len(intersections_dict[key])):
                                if intersections_dict[key][j][1] != None and intersections_dict[key][j][1] >= (i + 1) and intersections_dict[key][j][1] <= (i + 2):
                                    j_array.append(j)
                        line_string += "Finally, line " + \
                            str(key) + " " + \
                            slope_strings[key][i] + " " +\
                            str(values[i + 1][1]) + " " + \
                            " at the x value of " + str(x_axis_values[i + 1])
                        if len(j_array) == 0:
                            line_string += ".\n"
                        else:
                            for j in j_array:
                                line_string += "and intersects with line " + \
                                    str(intersections_dict[key][j][0]) + " at " + str(
                                        intersections_dict[key][j][2]) + " "
                            line_string += " between " + \
                                str(x_axis_values[i]) + " and " + \
                                str(x_axis_values[i + 1]) + ".\n"

                # create .wav file for each line
                print(line_string)
                try:
                    tts = gTTS(line_string)
                    tts.save(str(key) + '.mp3')
                except:
                    messagebox.showerror(title='Error Creating Audible Line Description',
                                         message='ERROR: Unable to create individual line string audible narration files... \n Please ensure that gTTS is installed.')
                    print(
                        " ERROR: Unable to create individual line string audible narration files")

                aud_text += line_string  # adds line information to complete text file

            aud_text_file_name = new_file_name + '.txt'

            prog_bar.step(10)  # 50%
            background.update()

            try:
                f = open(aud_text_file_name, "w+")  # create read/write
                print(" info: Successfully created text file")
                try:
                    f.write(aud_text)
                    print(" info: Successfully wrote text data")
                    try:
                        os.chmod(aud_text_file_name, S_IREAD | S_IRGRP |
                                 S_IROTH)  # lock file to read-only
                        print(" info: Successfully write locked text file")
                    except:
                        print(" Error: Unable to lock file to read only")
                except:
                    print(" Error: Unable to write text data")
                f.close
            except:
                print(" Error: Unable to create file")

            try:
                #print('attempting to gTTS')
                tts = gTTS(aud_text)
                tts.save('audTex.mp3')
                print(' info: Saved audTex.mp3')
            except:
                messagebox.showerror(title='Error Creating Audible Sound Description',
                                     message='ERROR: Unable to create complete audible narration file... \n Please ensure that gTTS is installed.')
                print(
                    " ERROR: Unable to create complete audible narration file")

            prog_bar.step(10)  # 60%
            background.update()

            src_mp3 = '"' + path + "audTex.mp3" + '"'
            des_wav = ' "' + path + "everything.wav" + '"'
            ffmpeg_path = '"' + desktop + "\\AGR\\ffmpeg.exe" + ' "'
            my_command = ffmpeg_path + " -i " + src_mp3 + des_wav
            proc = subprocess.Popen(
                my_command, shell=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(" info: Created everything.wav")

            # Convert each line mp3 to wav..
            for key, values in lines_vals:
                #print("creating " + str(key) + ".wav")
                src_mp3 = '"' + path + str(key) + ".mp3" + '"'
                # print("srcmp3: " + src_mp3)
                dest_wav = ' "' + path + str(key) + ".wav" + '"'
                # print("destwav: " + dest_wav)
                ffmpeg_path = '"' + desktop + "\\AGR\\ffmpeg.exe" + ' "'
                my_command = ffmpeg_path + " -i " + src_mp3 + dest_wav
                proc = subprocess.Popen(
                    my_command, shell=key, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print(" info: Created " + str(key) + ".wav")

            prog_bar.step(30)  # 90%
            background.update()

            if pause_play_button["state"] == "disabled":
                pause_play_button["state"] = "normal"
            if replay_button["state"] == "disabled":
                replay_button["state"] = "normal"
            if upload_button["state"] == "disabled":
                upload_button["state"] = "normal"
            if play_entire_graph_desc_button["state"] == "disabled":
                play_entire_graph_desc_button["state"] = "normal"
            if tutorial_button["state"] == "disabled":
                tutorial_button["state"] = "normal"
            if load_previous_graph_button["state"] == "disabled":
                load_previous_graph_button["state"] = "normal"
            if exit_button["state"] == "disabled":
                exit_button["state"] = "normal"

            everything_path = path + 'everything.wav'
            everything_path = os.path.normpath(everything_path)

            # Check if ffmpeg is done processing the everything.mp3 -> .wav
            # Wait if file does not exist
            while(os.path.isfile(everything_path) == False):
                time.sleep(0.05)

            proc_label.place_forget()
            prog_bar.place_forget()

            place_line_desc_buttons(num_lines)
            t2.cancel()
            play_entire_graph_desc_fn(path)

    elif (file_path == ""):
        # If empty string: dialog returns with no selection, ie user pressed cancel
        print(" info: User cancelled upload image")
    else:
        print("error with file submission")


def load_previous_graph_fn():
    global file_path
    global play_entire_graph_desc_button
    global playing_bool

    if stream.is_active():
        print(' info: stream paused for load previous')
        stream.stop_stream()
        playing_bool = False

    AGR_FOLDER = os.path.normpath(os.path.expanduser("~/Desktop/AGR/Graphs/"))
    file_path = filedialog.askopenfilename(
        initialdir=AGR_FOLDER, title="Select Previous Graph Image", filetypes=[
            ("Image Files", ".png .jpg .gif .img .jpeg")])

    if os.path.isfile(file_path):
        remove_line_desc_buttons(8)
        img = Image.open(file_path)
        if img.size[0] > 690 or img.size[1] > 545:
            img = img.resize((690, 545), Image.ANTIALIAS)

        openImg = ImageTk.PhotoImage(img)
        image = tk.Label(master=background, width=690,
                         height=505, image=openImg)
        image.image = openImg
        image.place(x=160, y=120)

        print(' info: ' + os.path.normpath(file_path) +
              " has been opened in the preview window")

        # load json find num lines, load each aud file
        dir_path = os.path.dirname(os.path.realpath(file_path))

        os.chdir(dir_path)
        count = 0
        for file in glob.glob("*.wav"):
            count += 1

        prev_num_lines = (count - 1)/2

        place_line_desc_buttons(prev_num_lines)

        if play_entire_graph_desc_button["state"] == "disabled":
            play_entire_graph_desc_button["state"] = "normal"

        play_entire_graph_desc_fn(dir_path)

        if pause_play_button["state"] == "disabled":
            pause_play_button["state"] = "normal"
        if replay_button["state"] == "disabled":
            replay_button["state"] = "normal"
        if upload_button["state"] == "disabled":
            upload_button["state"] = "normal"
        if play_entire_graph_desc_button["state"] == "disabled":
            play_entire_graph_desc_button["state"] = "normal"
        if tutorial_button["state"] == "disabled":
            tutorial_button["state"] = "normal"
        if load_previous_graph_button["state"] == "disabled":
            load_previous_graph_button["state"] = "normal"
        if exit_button["state"] == "disabled":
            exit_button["state"] = "normal"

    elif (file_path == ""):
        # If empty string: dialog returns with no selection, ie user pressed cancel
        print(" info: User cancelled upload previous image")
    else:
        print("error with file submission")


def play_entire_graph_desc_fn(path):
    global playing_bool
    global stream
    global p
    global wf
    global sound_file

    if (os.path.isdir(path)):

        if playing_bool or stream.is_active():
            stream.stop_stream()
        
        sound_file = os.getcwd() + r'\everything.wav'
        sound_file = os.path.normpath(sound_file)
        wf = wave.open(sound_file, 'rb')
        print(' info: ', sound_file, " loaded")

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        stream_callback=callback)
        return stream

    else:
        print("Path not yet defined, cant find sound file..")
        return False


def play_tutorial():
    global playing_bool
    global stream
    global p
    global wf
    global sound_file
    global program_path

    if (os.path.isdir(program_path)):
        if playing_bool or stream.is_active():
            stream.stop_stream()
        if pause_play_button["state"] == "disabled":
            pause_play_button["state"] = "normal"
        # os.chdir(path)
        sound_file = program_path + r'\tutorial.wav'
        sound_file = os.path.normpath(sound_file)

        wf = wave.open(sound_file, 'rb')
        print(' info: ', sound_file, " loaded")

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        stream_callback=callback)
        return stream

    else:
        print(" ERROR: bad path for tutorial.wav file")
        return False


def play_line_desc(line_number):
    global playing_bool
    global stream
    global p
    global wf
    global sound_file
    global program_path
    global tonal_enabled

    if playing_bool or stream.is_active():
        stream.stop_stream()

    if tonal_enabled == True:
        sound_file = str(program_path) + r'\tonal_intro.wav'
        wf = wave.open(sound_file, 'r')
        print(' info: ', sound_file, " loaded")

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        stream_callback=callback)

        while(stream.is_active()):
            time.sleep(1)
            print('waiting')

        sound_file = "tonal_" + str(line_number) + ".wav"
        wf = wave.open(sound_file, 'r')
        print(' info: ', sound_file, " loaded")

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        stream_callback=callback)

        while(stream.is_active()):
            time.sleep(1)
            print('waiting')

    sound_file = str(line_number) + ".wav"
    wf = wave.open(sound_file, 'r')

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
            print(' info: ', sound_file, " loaded")

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


def play_pause():
    global playing_bool
    global stream
    if stream.is_stopped():
        print(' info: play pressed')
        stream.start_stream()
        playing_bool = True
        return False
    elif stream.is_active():
        print(' info: pause pressed')
        stream.stop_stream()
        playing_bool = False
        return False
    return False


def key(event):
    global line_1_button
    global line_2_button
    global line_3_button
    global line_4_button
    global line_5_button
    global line_6_button
    global line_7_button
    global line_8_button
    global path
    global tonal_enabled

    if event.keysym == 'space':
        if pause_play_button["state"] == "normal":
            play_pause()
        else:
            print(" Error: Pause/Play Button not enabled")
    elif event.keysym == '1':
        if line_1_button["state"] == "normal":
            play_line_desc(1)
        else:
            print(" Error: Line desc not enabled")
    elif event.keysym == '2':
        if line_2_button["state"] == "normal":
            play_line_desc(2)
        else:
            print(" Error: Line desc not enabled")
    elif event.keysym == '3':
        if line_3_button["state"] == "normal":
            play_line_desc(3)
        else:
            print(" Error: Line desc not enabled")
    elif event.keysym == '4':
        if line_4_button["state"] == "normal":
            play_line_desc(4)
        else:
            print(" Error: Line desc not enabled")
    elif event.keysym == '5':
        if line_5_button["state"] == "normal":
            play_line_desc(5)
        else:
            print(" Error: Line desc not enabled")
    elif event.keysym == '6':
        if line_6_button["state"] == "normal":
            play_line_desc(6)
        else:
            print(" Error: Line desc not enabled")
    elif event.keysym == '7':
        if line_7_button["state"] == "normal":
            play_line_desc(7)
        else:
            print(" Error: Line desc not enabled")
    elif event.keysym == '8':
        if line_8_button["state"] == "normal":
            play_line_desc(8)
        else:
            print(" Error: Line desc not enabled")
    elif event.keysym == 'h':
        if tutorial_button["state"] == "normal":
            play_tutorial()
        else:
            print(" Error: Tutorial button not enabled")
    elif event.keysym == 'r':
        if replay_button["state"] == "normal":
            replay()
    elif event.keysym == 'u':
        if upload_button["state"] == "normal":
            upload()
        else:
            print(" Error: Upload button not enabled")
    elif event.keycode == 27:
        # On Escape Key press
        if exit_button["state"] == "normal":
            ok = messagebox.askokcancel(
                message="Are you sure you want to exit?")
            if ok:
                exitAGR()
        else:
            print(" Error: Exit button not enabled")
    elif event.keysym == 'i':
        if load_previous_graph_button["state"] == "normal":
            load_previous_graph_fn()
        else:
            print(" Error: Open prev graph not enabled")
    elif event.keycode == 192:
        # On '`' key press (aka tilde key)
        if play_entire_graph_desc_button["state"] == "normal":
            play_entire_graph_desc_fn(path)
        else:
            print(" Error: Explain Graph button not enabled")
    elif event.keycode == 52:  # dollar sign, $
        if tonal_enabled == True:
            tonal_enabled = False
            print(' info: Tonal Description DISABLED')
        elif tonal_enabled == False:
            print(' info: Tonal Descriptions ENABLED *GUI may become momentarily unresponsive*')
            tonal_enabled = True


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
    print(" Terminating...")
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
            if x1 == None or x2 == None or y1 == None or y2 == None:
                slope = None
                if key in relative_slopes:
                    relative_slopes[key].append("None")
                else:
                    relative_slopes[key] = ["None"]
            else:
                slope = round((y2 - y1) / (x2 - x1), 2)
                if slope > 0:
                    if slope/MAX_Y_VAL > 0.5:
                        if key in relative_slopes:
                            relative_slopes[key].append("goes up sharply to")
                        else:
                            relative_slopes[key] = ["goes up sharply to"]
                    elif slope/MAX_Y_VAL > 0.3:
                        if key in relative_slopes:
                            relative_slopes[key].append(
                                "goes up significantly to")
                        else:
                            relative_slopes[key] = ["goes up significantly to"]
                    elif slope/MAX_Y_VAL > 0.1:
                        if key in relative_slopes:
                            relative_slopes[key].append(
                                "goes up moderately to")
                        else:
                            relative_slopes[key] = ["goes up moderately to"]
                    else:
                        if key in relative_slopes:
                            relative_slopes[key].append("goes up slightly to")
                        else:
                            relative_slopes[key] = ["goes up slightly to"]
                elif slope < 0:
                    if slope/MAX_Y_VAL < -0.5:
                        if key in relative_slopes:
                            relative_slopes[key].append("goes down sharply to")
                        else:
                            relative_slopes[key] = ["goes down sharply to "]
                    elif slope/MAX_Y_VAL < -0.3:
                        if key in relative_slopes:
                            relative_slopes[key].append(
                                "goes down significantly to")
                        else:
                            relative_slopes[key] = [
                                "goes down significantly to"]
                    elif slope/MAX_Y_VAL < -0.1:
                        if key in relative_slopes:
                            relative_slopes[key].append(
                                "goes down moderately to")
                        else:
                            relative_slopes[key] = ["goes down moderately to"]
                    else:
                        if key in relative_slopes:
                            relative_slopes[key].append(
                                "goes down slightly to")
                        else:
                            relative_slopes[key] = ["goes down slightly to"]
                elif slope == 0:
                    if key in relative_slopes:
                        relative_slopes[key].append("stays the same at")
                    else:
                        relative_slopes[key] = ["stays the same at"]
            if key in slopes:
                slopes[key].append(slope)
            else:
                slopes[key] = [slope]
    print("slopes: ", slopes)
    print("relative_slopes: ", relative_slopes)
    return slopes, relative_slopes


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
            if m1 == None or x == None or y == None:
                b1 = None
            else:
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
                if m1 == None or m2 == None or b1 == None or b2 == None:
                    m3 = None
                    b3 = None
                else:
                    b3 = b2 - b1
                    m3 = m1 - m2

                if m3 == 0:  # means the lines are parallel and will never intersect or are the same line
                    continue

                if b3 == None or m3 == None:
                    x_i = None
                    y_i = None
                else:
                    x_i = b3/m3
                    if x_i > x_max or x_i < X_MIN:
                        continue

                if x_i != None and y_i != None:
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
    # crop_img[mask] = (204, 119, 0)

    gray = cv2.cvtColor(cropped_y_axis, cv2.COLOR_BGR2GRAY)

    # set threshold level
    threshold_level = 120

    # find coordinates of all pixels below threshold
    ycoords = np.column_stack(np.where(gray < threshold_level))

    # create mask of all pixels lower than threshold level
    mask = gray < threshold_level

    # color the pixels in the mask
    # crop_img[mask] = (204, 119, 0)

    return xcoords, ycoords


def store_coords(crop_img, xcoords, ycoords, x_pixels_width, y_pixels_height, x_axis_exists, y_axis_exists):
    global ref_points
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
        0] + round(y_pixels_height*0.7)

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
    # print(list(sorted_ydict.values())[1])
    x_pixel_line = list(sorted_ydict.keys())[0]

    origin = (x_pixel_line, y_pixel_line)

    print(" info: origin: ", origin)

    # if the longest line is bigger than half the width of the page it is the x-axis
    if longest_yline_size > 0.5*x_pixels_width:
        print("The x-axis is at y pixel ", y_pixel_line)
        print("The x-axis is ", longest_yline_size, " pixels long")
    else:
        messagebox.showinfo(
            title="Get x-axis", message="Click at the top of the y-axis and drag to the right of the x-axis.")
        click_img_axes()
        y_pixel_line = ref_points[1][1]
        longest_yline_size = ref_points[1][0] - ref_points[0][0]
        print("The x-axis is at y pixel ", y_pixel_line)
        print("The x-axis is ", longest_yline_size, " pixels long")
        x_axis_exists = True

    if longest_xline_size > 0.5*y_pixels_height:
        print("The y-axis is at x pixel ", x_pixel_line)
        print("The y-axis is ", longest_xline_size, " pixels long")

    else:
        if len(ref_points) > 0:
            pass
        else:
            messagebox.showinfo(
                title="Get y-axis", message="Click at the top of the y-axis and drag to the right of the x-axis.")
            click_img_axes()
        x_pixel_line = ref_points[0][0]
        longest_xline_size = ref_points[1][1] - ref_points[0][1]
        print("The y-axis is at x pixel ", x_pixel_line)
        print("The y-axis is ", longest_xline_size, " pixels long")
        y_axis_exists = True

    # makes a text file with all the y and x coordinates of the pixels under the threshold
    # with open('listfile.txt', 'w') as filehandle:
    #     for listitem in ylist:
    #         filehandle.write('%s\n' % listitem)
    # print(x_axis_exists)
    return y_pixel_line, x_pixel_line, longest_yline_size, longest_xline_size, x_axis_exists, y_axis_exists, origin


def click_img_axes():
    global ref_points
    global draw_axes_img
    global draw_axes_img_redo
    draw_axes_img = draw_axes_img_redo.copy()
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', get_axes)
    cv2.imshow('image', draw_axes_img)
    cv2.waitKey(0)


def get_axes(event, x, y, flags, param):
    # grab references to the global variables
    global ref_points
    global draw_axes_img

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates 

    if event == cv2.EVENT_LBUTTONDOWN:
        ref_points = [(x, y)]
        print(ref_points)

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates
        ref_points.append((x, y))
        # draw a rectangle around the region of interest
        cv2.rectangle(
            draw_axes_img, ref_points[0], ref_points[1], (255, 0, 0), 1)
        cv2.imshow("image", draw_axes_img)
        t3 = threading.Thread(target=redraw, args=())
        t3.start()
        cv2.waitKey(0)


def redraw():
    global ref_points
    if len(ref_points) == 2:
        ans = messagebox.askyesno(
            title="Redraw?", message="Would you like to redraw the rectangle?")
        if ans == True:
            click_img_axes()
        else:
            cv2.destroyAllWindows()


def get_xdata(crop_img, y_pixel_line, x_pixel_line, x_axis_exists, y_axis_values, longest_yline_size, longest_xline_size):
    y_pixels_height = crop_img.shape[0]
    x_pixels_width = crop_img.shape[1]

    x_axis_img = crop_img[y_pixel_line +
                             5: y_pixels_height, 0: x_pixels_width]

    # gets data from image
    d2 = pytesseract.image_to_data(x_axis_img, output_type=Output.DICT)
    text = d2['text']
    left = d2['left']
    width = d2['width']

    # list that holds the x axis values
    x_axis_values = []

    # list that holds the x axis title
    x_axis_title = []

    # list that holds the pixel value of the median of the box that surrounds each x-axis value
    x_axis_value_medians = []

    

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

    if len(x_axis_title) == 0:
        x_axis_title.append('None')

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

    # the data from the graph has boxes created around it
    n_boxes2 = len(d2['level'])
    for i in range(n_boxes2):
        (x, y, w, h) = (d2['left'][i], d2['top']
                        [i], d2['width'][i], d2['height'][i])
        cv2.rectangle(x_axis_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return x_axis_values, x_axis_title, x_axis_value_medians


def get_ydata(crop_img, x_pixel_line, y_pixel_line, y_axis_exists, longest_xline_size):
    y_axis_img = crop_img[0: y_pixel_line + 10, 0: x_pixel_line-5]

    
    # gets data from image
    d2 = pytesseract.image_to_data(y_axis_img, output_type=Output.DICT)
    text = d2['text']
    top = d2['top']
    width = d2['width']

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
            if separated_text[i][j].isdigit():
                y_axis_values.append("".join(separated_text[i]))
            else:
                y_axis_title.append(separated_text[i][j])

    # all the values that are not a space that occur after the x axis values
    for i in text:
        if i != ''and i.isalpha():
            y_axis_title.append(i)

    if len(y_axis_title) == 0:
        y_axis_title.append('None')
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

    biggest_max = y_axis_values[0]
    smallest_min = y_axis_values[-1]
    if type(smallest_min) != float:
        smallest_min = 0

    return y_axis_values, biggest_max, smallest_min, y_axis_title

def get_datapoints(crop_img, x_axis_exists, longest_xline_size, x_axis_values, x_axis_value_medians, y_pixel_line, y_axis_values):
    # dictionary that holds the lines and the positions of the datapoints that exist on the graph
    line_data = {}

    # holds the minimum point for each line
    min_points = {}

    # holds the maximum point for each line
    max_points = {}

    # holds the coordinates of the x-axis values in pixels
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

    # holds the x pixel value for the median of each x-axis value box
    x_axis_points = 0

    # adds the median x pixel values for each x-axis value box to x_axis_value_datapoints
    if len(x_axis_value_medians) > 0:
        x_axis_points = x_axis_value_medians[0]
        x_axis_value_datapoints.append(x_axis_points)

   # for each line the coordinates and the colors at those coordinates are saved in new_datapoints and new_datapoints_colors
    for i in range(len(x_axis_value_medians)):
        x_axis_points = x_axis_value_medians[i]
        try:
            res, col, top_of_graph, fin_col = get_line_positions(
                crop_img, x_axis_exists, y_pixel_line, longest_xline_size, x_axis_points)
        except:
            print('Error')
            return
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
    if len(most_common_list) > 0:
        most_common = max(set(most_common_list), key=most_common_list.count)
        num_lines = most_common

    if num_lines > 8:
        raise Exception("Too many lines")

    # colors are being stored in this dict. If the colors at the first x-axis value are not equal to the actual number
    # of lines, eg if a datapoint is covered by another, check several lines
    line_colors_dict = {}
    line = 1
    for i in range(num_lines):
        if len(new_datapoints_colors[0]) == num_lines and new_datapoints_colors[0][i][0] != None:
            line_colors_dict[line] = new_datapoints_colors[0][i].tolist()
            line += 1
        elif len(new_datapoints_colors[1]) == num_lines and new_datapoints_colors[1][i][0] != None:
            line_colors_dict[line] = new_datapoints_colors[1][i].tolist()
            line += 1
        elif len(new_datapoints_colors[2]) == num_lines and new_datapoints_colors[2][i][0] != None:
            line_colors_dict[line] = new_datapoints_colors[2][i].tolist()
            line += 1

    colors = list(line_colors_dict.values())
    buffer = 10
    for i in range(len(colors)):
        num_colors = len(colors)
        for j in range(num_colors):
            if j == i:
                pass
            else:
                if colors[i][0] in range(colors[j][0]-buffer, colors[j][0]+buffer) \
                        and colors[i][1] in range(colors[j][1]-buffer, colors[j][1]+buffer) \
                        and colors[i][2] in range(colors[j][2]-buffer, colors[j][2]+buffer):
                    raise Exception(
                        "You cannot have multiple lines with the same color")
                

    print('Line Colours: ', line_colors_dict)  # LINE COLORS

    # if there are less values in the new_datapoints list than there are lines, append "None" to the list to show the
    # system could not get any data
    for i in range(len(new_datapoints)):
        if len(new_datapoints[i]) < num_lines:
            diff = num_lines - len(new_datapoints[i])
            for j in range(diff):
                new_datapoints[i].append([None, None])
                final_colors[i].append([[None, None], [None, None, None]])
                new_datapoints_colors[i].append([None, None, None])

    buffer = 50
    correct_final_colors = [[] for k in range(num_lines)]
    # iterate over the number of x-axis values
    for i in range(len(final_colors)):

        # iterate over the number of points on the graph per x-axis value
        for j in range(num_lines):
            first_val = list(line_colors_dict.values())[j]
            if None in final_colors[i][j][1]:
                correct_final_colors[j].append(
                    [[None, None], [None, None, None]])

            else:
                color_index = 0
                # iterate over each datapoint and corresponding color to see if the color matches one in line_colors_dict
                for k in range(num_lines):
                    if None in final_colors[i][k][1]:
                        pass
                    else:
                        # if the colors match a color in the line_colors_dict then append them to their own sublist
                        if int(final_colors[i][k][1][0]) in range(int(first_val[0]-buffer), int(first_val[0]+buffer)) \
                                and int(final_colors[i][k][1][1]) in range(int(first_val[1]-buffer), int(first_val[1]+buffer)) \
                                and int(final_colors[i][k][1][2]) in range(int(first_val[2]-buffer), int(first_val[2]+buffer)):
                            correct_final_colors[j].append(final_colors[i][k])
                            color_index += 1
                if color_index == 0:

                    correct_final_colors[j].append(
                        [[None, None], [None, None, None]])

    # a list with sublists. number of sublists is determined by the number of lines
    line_positions = [[] for k in range(num_lines)]
    yAxis_values = []
    yAxis_values = calculate_yAxis_values(
        crop_img, y_pixel_line, new_datapoints, correct_final_colors, num_lines, y_axis_values, top_of_graph)

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
            if y != None:
                max_position[i].append((y))
        min_val = min(min_position[i])
        max_val = max(max_position[i])
        for n in range(len(line_positions[i])):
            if line_positions[i][n][1] == min_val:
                min_points[i+1] = (line_positions[i][n])
            elif line_positions[i][n][1] == max_val:
                max_points[i+1] = (line_positions[i][n])
    print("Minimum points: ", min_points)
    print("Maximum points: ", max_points)

    return line_data, num_lines, line_colors_dict

def get_line_positions(crop_img, x_axis_exists, y_pixel_line, longest_xline_size, x_axis_points):
    colors = []
    color_positions = []
    final_colors = []
    datapoints = []

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
        pix = crop_img[i, x_axis_points]
        if pix[0] > 230 and pix[1] > 230 and pix[2] > 230 or pix[0] < 30 and pix[1] < 30 and pix[2] < 30:
            continue
        else:
            color_positions.append([x_axis_points, i])
            colors.append(list(pix))

    # finds the consecutive y pixel values and groups them into lists
    for i in range(len(color_positions)):
        if color_positions[i-1][1] + 1 == color_positions[i][1]:
            datapoints[-1].append(color_positions[i][1])

        else:
            datapoints.append([color_positions[i][1]])

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
        d = crop_img[new_datapoints[i][1], x_axis_points]
        if d[0] > 230 and d[1] > 230 and d[2] > 230:
            continue
        else:
            new_datapoints_colors.append(d)

    for i in range(len(new_datapoints)):

        final_colors.append(
            [new_datapoints[i], new_datapoints_colors[i]])

    return new_datapoints, new_datapoints_colors, top_of_graph, final_colors


def calculate_yAxis_values(crop_img, y_pixel_line, new_datapoints, correct_final_colors, num_lines, y_axis_values, top_of_graph):
    y_pixels_height = crop_img.shape[0]

    top_of_graph = y_pixels_height - top_of_graph
    y_pixel_line = y_pixels_height - y_pixel_line
    datapoints = [[] for k in range(num_lines)]
    distance_from_top_to_x_axis = top_of_graph - y_pixel_line
    top_y_axis_val = y_axis_values[0]

    pixels_divider = distance_from_top_to_x_axis / \
        (float(top_y_axis_val) - 0)

    print(len(new_datapoints), len(new_datapoints[0]))
    for i in range(len(new_datapoints)):
        for j in range(len(new_datapoints[0])):
            y_axis_datapoint_pixel = correct_final_colors[j][i][0][1]
            if y_axis_datapoint_pixel == None:
                datapoints[j].append(None)
            else:
                yAxis_values = round(
                    ((y_pixels_height - float(y_axis_datapoint_pixel)) - y_pixel_line) / pixels_divider, 2)

                datapoints[j].append(yAxis_values)
    return datapoints


def get_graph_title(image_path):
    try:
        input_image = Image.open(str(image_path))
        cropped_input_image = input_image.crop((
            0, 0, (input_image.size[0]), (.14*input_image.size[1])))  # crop the image to top 1/3
        # allow sharpness enhancement on cropped image
        enh_sha_obj = ImageEnhance.Sharpness(
            cropped_input_image.convert('RGB'))
        image_sharped = enh_sha_obj.enhance(3.0)  # shapness factor of 3
        # Extract Text
        image_text = pytesseract.image_to_string(image_sharped, lang='eng')
        # Assign graph title
        graph_title = ""
        iterator = 0
        while iterator < len(image_text):  # and image_text[iterator] != '\n':
            if image_text[iterator] == '\n':
                if image_text[iterator+1] == '\n' or image_text[iterator+1] == ' ':
                    iterator += len(image_text)
                graph_title += ' '
                iterator += 1
            elif image_text[iterator] == '\'':
                graph_title += ','
                iterator += 1
            else:
                graph_title += image_text[iterator]
                iterator += 1
        return(graph_title)
    except:
        print("Error with input >> " + str(sys.exc_info()[1]))
        graph_title = 'None'
        return graph_title


def best_fit_slope(ys):
    ys = [x for x in ys if x != None]
    xs = []
    if len(ys) != 0:
        for i in range(len(ys)):
            xs.append(i+1)
    x = np.array(xs)
    y = np.array(ys)
    m, b = np.polyfit(x, y, 1)
    # print(m, b)
    return(round(m, 2))



def locate_tesseract():
    global err_count    # Tracks amount of failures when locating tesseract
    err_count += 1
    if err_count >= 5:
        ans = messagebox.askyesno(title='Exit?',
                                  message='It appears we are having trouble locating tesseract.exe. \n Would you like to exit the program?')
        if ans == True:
            sys.exit()
    if os.path.exists(program_path+'\\config.txt'):
        print(" info: tesser location defined")
        config_filestream = open("config.txt", "r")
        tesser_location = config_filestream.readline()
        # print(tesser_location)
        config_filestream.close()
        if os.path.exists(tesser_location):
            if 'tesseract.exe' in tesser_location:
                return tesser_location
        else:
            os.remove("config.txt")
            return(locate_tesseract())
    else:
        print(" info: tesser location unknown")
        messagebox.showwarning(title="Welcome to the Audible Graph Reader",
                               message="Firstly, we must locate your tesseract executable. \n Please locate the executable after pressing ok.")
        tesser_location = filedialog.askopenfilename(title="Point me to your tesseract.exe", filetypes=[
            ("Executable File", ".exe")])
        if tesser_location == '':
            messagebox.showerror(title='Error locating tesseract.exe',
                                 message='ERROR: Unable to retrieve location of tesseract.')
            print(" ERROR: Unable to retrieve location of tesseract")
            return(locate_tesseract())
        elif 'tesseract.exe' in tesser_location:
            tesser_location = os.path.normpath(tesser_location)
            config_filestream = open("config.txt", "w+")
            config_filestream.write(str(tesser_location))
            config_filestream.close()
            return(tesser_location)
        else:
            messagebox.showerror(title='Error Locating tesseract.exe',
                                 message='ERROR: Unable to retrieve location of tesseract \n Please try again')
            print(" ERROR: Unable to retrieve location of tesseract")
            return(locate_tesseract())


## End oF Functions ##

GUI.option_add("*Button.Background", "light blue")
GUI.option_add("*Button.Foreground", "black")
GUI.option_add("*Button.Font", ("Impact", 10))
GUI.option_add("*Label.Font", ("Impact", 13))

GUI.title('Audible Graph Reader')
GUI.geometry("900x700")
GUI.resizable(0, 0)  # Don't allow resizing in the x or y direction

background = tk.Frame(master=GUI, bg='white')
# Don't allow the widgets inside to determine the frame's width / height
background.pack_propagate(0)
# Expand the frame to fill the root window
background.pack(fill=tk.BOTH, expand=1)

logo_image = PhotoImage(file='AGRHorizontalLogo.png')
logo_label = tk.Label(master=background, image=logo_image, bg='white')
logo_label.pack()

upload_button = tk.Button(master=background, text='Upload Graph',
                          width=19, command=upload)

play_entire_graph_desc_button = tk.Button(master=background, text='Explain Graph',
                                          width=19, command=lambda: play_entire_graph_desc_fn(path))

tutorial_button = tk.Button(master=background, text='Tutorial',
                            width=19, command=play_tutorial)

load_previous_graph_button = tk.Button(master=background, text='Load Previous Graph',
                                       width=19, command=load_previous_graph_fn)

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
play_entire_graph_desc_button.place(x=30, y=180)
tutorial_button.place(x=30, y=240)
load_previous_graph_button.place(x=30, y=300)
pause_play_button.place(x=30, y=360)
replay_button.place(x=30, y=420)
exit_button.place(x=30, y=640)

prog_bar = Progressbar(background, style="light_blue.Horizontal.TProgressbar", orient=HORIZONTAL, length=200,
                       mode="determinate", takefocus=True, maximum=100)
proc_label = Label(background, bg='white',
                   text="Processing...")  # fg='#ADD8E6'
copy_write_label = Label(background, bg='white',
                         text="Copyright 2020 Missouri State University", font=('Helvetica', 10))
copy_write_label.place(x=330, y=675)


replay_button["state"] = "disabled"
play_entire_graph_desc_button["state"] = "disabled"

if os.path.exists(os.path.normpath(os.path.expanduser("~/Desktop/AGR/Graphs/"))) == False:
    load_previous_graph_button["state"] = "disabled"
else:
    load_previous_graph_button["state"] = "normal"

pause_play_button["state"] = "disabled"

GUI.bind("<Key>", key)  # calls key (function above) on Keyboard input
GUI.resizable(False, False)

err_count = 0
pytesseract.pytesseract.tesseract_cmd = locate_tesseract()
print(" info: tesseract location set: ", pytesseract.pytesseract.tesseract_cmd)

GUI.mainloop()

# stop and close stream
stream.stop_stream()
stream.close()
wf.close()

# close PyAudio
p.terminate()