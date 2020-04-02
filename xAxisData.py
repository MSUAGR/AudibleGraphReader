# -*- coding: utf-8 -*-
"""
Created on Sun Feb 16 12:47:16 2020

@author: Josh Hilger
"""

import cv2
import numpy as np
import os
from PIL import Image, ImageEnhance 
from collections import OrderedDict
from operator import itemgetter
import pytesseract
from pytesseract import Output
import re
import statistics
import math
import itertools
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def find_coords(cropped_x_axis, cropped_y_axis):
    gray = cv2.cvtColor(cropped_x_axis, cv2.COLOR_BGR2GRAY)
    
    # set threshold level
    threshold_level = 120
    
    # find coordinates of all pixels below threshold
    xcoords = np.column_stack(np.where(gray < threshold_level))
    
    # create mask of all pixels lower than threshold level
    mask = gray < threshold_level
    
    # color the pixels in the mask
    #cropped_img[mask] = (204, 119, 0)
    
    gray = cv2.cvtColor(cropped_y_axis, cv2.COLOR_BGR2GRAY)
    
    # set threshold level
    threshold_level = 120
    
    # find coordinates of all pixels below threshold
    ycoords = np.column_stack(np.where(gray < threshold_level))
    
    # create mask of all pixels lower than threshold level
    mask = gray < threshold_level
    
    # color the pixels in the mask
    #cropped_img[mask] = (204, 119, 0)
    
    return xcoords, ycoords

def store_coords(xcoords, ycoords, cropped_x_pixels_width, cropped_y_pixels_height, x_axis_exists, y_axis_exists):
    # dictionary stores the y coordinates of pixels along with how many times they appear at one y position
    y_values = {}
    
    # coordinate values are added to this list to iterate through
    ylist = []
    
    #stores the y coordinates of each pixel under the threshold into the dictionary y_values
    for i in range(len(xcoords)):
        ylist.append(xcoords[i])
        if xcoords[i][0] not in y_values:
            y_values[xcoords[i][0]] = 1
        else:
            y_values[xcoords[i][0]] += 1
        
    # sorts the dicctionary based on the number of times a pixel appears at one y coordinate
    sorted_xdict = OrderedDict(sorted(y_values.items(), key=itemgetter(1), reverse=True))

    # the longest line is the first in the sorted dictionary
    longest_yline_size = list(sorted_xdict.values())[0]
    y_pixel_line = list(sorted_xdict.keys())[0] + round(cropped_y_pixels_height*0.7)
    
    x_values = {}
    
    # coordinate values are added to this list to iterate through
    xlist = []
    
    #stores the y coordinates of each pixel under the threshold into the dictionary y_values
    for i in range(len(ycoords)):
        xlist.append(ycoords[i])
        if ycoords[i][1] not in x_values:
            x_values[ycoords[i][1]] = 1
        else:
            x_values[ycoords[i][1]] += 1
        
    # sorts the dicctionary based on the number of times a pixel appears at one y coordinate
    sorted_ydict = OrderedDict(sorted(x_values.items(), key=itemgetter(1), reverse=True))

    # the longest line is the first in the sorted dictionary
    longest_xline_size = list(sorted_ydict.values())[0]
    print(list(sorted_ydict.values())[1], 'gggg')
    x_pixel_line = list(sorted_ydict.keys())[0]
    
    origin = (x_pixel_line, y_pixel_line)
    
    print(origin, 'aaaaa')

    # if the longest line is bigger than half the width of the page it is the x-axis
    if longest_yline_size > 0.5*cropped_x_pixels_width:
        print("The x-axis is at y pixel ", y_pixel_line)
        print("The x-axis is ", longest_yline_size, " pixels long")
    else:
        y_pixel_line = round(cropped_y_pixels_height*0.9)
        longest_yline_size = cropped_x_pixels_width
        x_axis_exists = False
        print("There is no x-axis")
        
    if longest_xline_size > 0.5*cropped_y_pixels_height:
        print("The y-axis is at x pixel ", x_pixel_line)
        print("The y-axis is ", longest_xline_size, " pixels long")
    else:
        x_pixel_line = round(cropped_x_pixels_width*0.06)
        longest_xline_size = cropped_y_pixels_height
        y_axis_exists = False
        print("There is no y-axis")
    
    
    # makes a text file with all the y and x coordinates of the pixels under the threshold
    with open('listfile.txt', 'w') as filehandle:
        for listitem in ylist:
            filehandle.write('%s\n' % listitem)
    print("ffff", x_axis_exists)
    return y_pixel_line, x_pixel_line, longest_yline_size, longest_xline_size, x_axis_exists, y_axis_exists

def get_xdata(cropped_img, y_pixel_line, x_pixel_line, x_axis_exists, longest_yline_size, longest_xline_size, y_axis_values):
    cropped_y_pixels_height = cropped_img.shape[0]
    cropped_x_pixels_width = cropped_img.shape[1]
    
    if x_axis_exists == True:
        x_axis_img = cropped_img[y_pixel_line+5: cropped_y_pixels_height, 0: cropped_x_pixels_width]
    else:
        x_axis_img = cropped_img[round(cropped_y_pixels_height*0.82): round(cropped_y_pixels_height*0.8)+40, 0: cropped_x_pixels_width]
        print("The x-axis will be derived from the lowest y-axis value position")
    
    # gets data from image
    d2 = pytesseract.image_to_data(x_axis_img, output_type=Output.DICT)
    text = d2['text']
    top = d2['top']
    left = d2['left']
    width = d2['width']
    
    print(d2)
    # the most common value in the top list should be the number of pixels from the bounding box to x-axis values
    most_common = max(set(top), key = top.count)
    
    
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
    
    # sorts the colors 
    final_colors2 = []
    
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
                new = re.sub('[^a-zA-Z0-9_]','', xvalues_text[i])
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
    #key_x_axis_values = round(longest_line_size / len(x_axis_values))
    #print("Every ", key_x_axis_values, " pixels there is a key point")          
    
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
        datapoints, colors, top_of_graph = get_line_positions(cropped_img, x_axis_exists, y_pixel_line, longest_xline_size, x_axis_points)
        new_datapoints.append(datapoints)
        new_datapoints_colors.append(colors)

    # num_lines is found by getting the length of a sublist in new_datapoints
    # new_datapoints is a list made up of sublists containing the coordinates of a color pixel for each x-axis value
    # eg [[[73, 151], [73, 191]], [[103, 159], [103, 202]], [[133, 145], [133, 156]]] this list has two lines and 
    # 3 x-axis values
    for i in range(len(new_datapoints)):
        for j in range(len(new_datapoints[i])):
            num_lines = len(new_datapoints[i])
    
    # colors are added to final_colors in a sublist within a list so that for each line a color will correspond to the 
    # x,y coordinate at an x-axis value
    for i in range(len(new_datapoints)):
        for j in range(len(new_datapoints[i])):
            #print(new_datapoints[i][j])
            #print(new_datapoints_colors[i][j])
            print(new_datapoints[i][j])
            print(new_datapoints_colors[i][j])
            #cropped_img[new_datapoints[i][j][1], new_datapoints[i][j][0]] = (0, 0, 0)
            final_colors.append([new_datapoints[i][j], new_datapoints_colors[i][j]])
            
                    
            #final_colors2 = list(final_colors for final_colors,_ in itertools.groupby(final_colors))
    print(final_colors)
    #print('ese', final_colors)
    #print('dsd', final_colors2)
    yAxis_values = []
    yAxis_values = calculate_yAxis_values(cropped_img, y_pixel_line, new_datapoints, num_lines, y_axis_values, top_of_graph)
    # a list with sublists. number of sublists is determined by the number of lines
    line_positions = [[] for k in range(num_lines)]

    # each sublist in line_positions represents each line's y coordinates and a number from 1 to the number of x-axis values
    # eg [[(1, 213), (2, 222)], (1,124), (2, 211)] there are two lines and two x-axis values. the value on the right in 
    # the tuple indicates the y coordinate at the corresponding x-axis value
    for i in range(num_lines):
        val = 0
        # store positions for each line in line_data
        for j in range(len(new_datapoints)):
            val += 1  
            '''
            for k in range(len(new_datapoints_colors[0])):
                first_color_pixel = new_datapoints_colors[0][k][0]
                second_color_pixel = new_datapoints_colors[0][k][1]
                third_color_pixel = new_datapoints_colors[0][k][2]
                if first_color_pixel in range(first_color_pixel-50, first_color_pixel+50) \
                and second_color_pixel in range(second_color_pixel-50, second_color_pixel+50) \
                and third_color_pixel in range(third_color_pixel-50, third_color_pixel+50):
            '''
            line_positions[i].append((val, yAxis_values[i][j]))
        
    
    # line_data gets keys based on the number of lines and the values are line_positions values
    # min and max points are dictionaries containing the min and max value for each line
    for i in range(num_lines):
        line_data[i+1] = line_positions[i]
        min_points[i+1] = None
        max_points[i+1] = None
        
    print("Line data: ", line_data)
        
    
    min_position = [[] for k in range(num_lines)]
    print(min_position)
    max_position = [[] for k in range(num_lines)]
    for i in range(len(line_data)):
        for j in range(len(line_data[i+1])):
            y = line_data[i+1][j][1]
            min_position[i].append((y))
            max_position[i].append((y))
            min_points[i+1] = (min(min_position[i]))
            max_points[i+1] = (max(max_position[i]))
    print(line_data)
    print("min", min_points)
    print("max", max_points)
    biggest_max = max(max_points.values())
    print('big', biggest_max)
    '''
    print("The points where colors exist are at x, y pixel: ", new_datapoints)
    print("The colors at the corresponding positions are: ", new_datapoints_colors)
    '''
    # the data from the graph has boxes created around it
    n_boxes2 = len(d2['level'])
    for i in range(n_boxes2):
        (x, y, w, h) = (d2['left'][i], d2['top'][i], d2['width'][i], d2['height'][i])
        cv2.rectangle(x_axis_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    cv2.imshow('image', cropped_img)
    cv2.waitKey(0)
    
    return x_axis_values

def get_ydata(cropped_img, x_pixel_line, y_pixel_line, y_axis_exists, longest_xline_size):
    cropped_y_pixels_height = cropped_img.shape[0]
    cropped_x_pixels_width = cropped_img.shape[1]
    
    if y_axis_exists == True:
        y_axis_img = cropped_img[0: y_pixel_line + 10, 0: x_pixel_line-5]
    else:
        y_axis_img = cropped_img[0: y_pixel_line + 10, 0: x_pixel_line + 10]
        print("The y-axis will be derived from the leftmost x-axis datapoint")
    
    # gets data from image
    d2 = pytesseract.image_to_data(y_axis_img, output_type=Output.DICT)
    text = d2['text']
    top = d2['top']
    left = d2['left']
    width = d2['width']
    
    print(d2)
    
    # the most common value in the top list should be the number of pixels from the bounding box to x-axis values
    most_common = max(set(left), key = left.count)
    
    #list that holds the x axis values
    y_axis_values = []
    
    #list that holds the x axis title
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
            print("".join(separated_text[i]))
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
        (x, y, w, h) = (d2['left'][i], d2['top'][i], d2['width'][i], d2['height'][i])
        cv2.rectangle(y_axis_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    cv2.imshow('image', y_axis_img)
    cv2.waitKey(0)
    
    return y_axis_values
 
def get_line_positions(cropped_img, x_axis_exists, y_pixel_line, longest_xline_size, x_axis_points):
    colors = []
    color_positions = []
    datapoints = []
    datapoints_colors = []
    # new_datapoints holds the correct datapoints
    new_datapoints = []
    #new_datapoints_colors holds the correct datapoints colors
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
            #cropped_img[151, 73] = (0, 0, 0)
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
        if d[0] > 230 and d[1] > 230 and d[2] > 230 or d[0] < 30 and d[1] < 30 and d[2] < 30:
            continue
        else:
            new_datapoints_colors.append(d)

    #print("it starts ere", new_datapoints_colors)
    return new_datapoints, new_datapoints_colors, top_of_graph

def calculate_yAxis_values(cropped_img, y_pixel_line, new_datapoints, num_lines, y_axis_values, top_of_graph):
    cropped_y_pixels_height = cropped_img.shape[0]
    cropped_x_pixels_width = cropped_img.shape[1]
    
    top_of_graph = cropped_y_pixels_height - top_of_graph
    y_pixel_line = cropped_y_pixels_height - y_pixel_line
    datapoints = [[] for k in range(num_lines)]
    distance_from_top_to_x_axis = top_of_graph - y_pixel_line
    pixels_divider = distance_from_top_to_x_axis / float(y_axis_values[0])
    
    for i in range(len(new_datapoints)):
        for j in range(len(new_datapoints[0])):
            yAxis_values = math.ceil(((cropped_y_pixels_height - float(new_datapoints[i][j][1])) - y_pixel_line) / pixels_divider)
            
            
            datapoints[j].append(yAxis_values)
    return datapoints
    
    
    
    
    
def main():
    os.chdir('images')
    img = Image.open("image4.png")
    #img = ImageEnhance.Sharpness(img.convert('RGB'))
    #img = img.enhance(5.0).save('eimage2.png')
    img = cv2.imread('image4.png')
    
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
    
    cropped_x_axis = cropped_img[round(cropped_y_pixels_height*0.7): cropped_y_pixels_height, 0: cropped_x_pixels_width]
    cropped_y_axis = cropped_img[0: cropped_y_pixels_height, 0: round(cropped_x_pixels_width*0.3)]
    xcoords, ycoords = find_coords(cropped_x_axis, cropped_y_axis)
    y_pixel_line, x_pixel_line, longest_yline_size, longest_xline_size, x_axis_exists, y_axis_exists = store_coords(xcoords, ycoords, cropped_x_pixels_width, cropped_y_pixels_height, x_axis_exists, y_axis_exists)
    y_axis_values = get_ydata(cropped_img, x_pixel_line, y_pixel_line, y_axis_exists, longest_xline_size)
    x_axis_values = get_xdata(cropped_img, y_pixel_line, x_pixel_line, x_axis_exists, longest_yline_size, longest_xline_size, y_axis_values)
main()