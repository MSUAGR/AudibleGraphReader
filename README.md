# The Audible Graph Reader Project 
Copyright 2020 Missouri State University

Readme updated: 5.7.2020  
The Audible Graph Reader is an application for the visually impaired that will audibly describe the contents of a line graph. Descriptions including, how many lines are on the graph, where the lines intersect, where the lines start/end and more.

The AGR project is built using Python 3. This version of python is available from the downloads section of Python’s website as linked here: https://www.python.org/download/releases/3.0/
The AGR project uses pytesseract v5.0.0 available here: https://github.com/UB-Mannheim/tesseract/wiki

Several additional libraries are required for the AGR.py script to function. These may be installed using their name and version as arguments for pip install. Ex. ‘pip install gtts==2.1.1’.
(gtts==2.1.1, langdetect==1.0.8, numpy==1.18.1, opencv-python==4.2.0.32, Pillow==7.0.0, PyAudio==0.2.11 (This may require a specific install)* see below, pytesseract==0.3.3, tones==1.0.1)

PyAudio does not currently have a release for the python3, however, a separate whl install file is available for python3 here, just verify your python version (x64 or 32) before downloading: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

The AGR.py program can be placed anywhere accessible to the user, such as the Desktop or any non restrictive folder on a physical drive. The AGR program should be placed in its own folder with the following contents (available from GitHub: https://github.com/MSUAGR/AudibleGraphReader):
 
●	AGR.py
●	AGRHorizontalLogo.png
●	agr.ico
●	blank.wav
●	Tutorial.wav
●	tonal_intro.wav
●	ffmpeg.exe 

# To Run:
 Install pytesseract v5.0.0
 Place the above files within their own directory
 Run AGR.py with no arguments:
 ./AGR.py
