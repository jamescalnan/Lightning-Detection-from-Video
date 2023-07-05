# Lightning Detection from Video
This project aims to detect lightning strikes in a video by analyzing brightness changes in the frames.

## Description
The program works by sampling pixels from each frame of a video and calculating the average brightness. When a sudden increase in brightness is detected, the program assumes that a lightning strike has occurred. Detected lightning strikes are logged, and a separate video clip around the time of the strike is saved for further analysis.

## Installation

### Prerequisites
```bash
Python 3.7 or later
OpenCV
NumPy
Rich
```
