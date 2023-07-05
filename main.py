# Import necessary libraries
from asyncio.windows_events import NULL
from rich.console import Console
import numpy as np
import cv2
import math
import time
import sys

# Create a console object for pretty printing
c = Console()

# Open the video file
vidcap = cv2.VideoCapture('IMG_4215.MOV')

# Read the first frame from the video file
success, image = vidcap.read()

# Initialize frame counter
count = 0

# Clear the console window
c.clear()

# Get the total number of frames in the video
total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

# Define photometric brightness function
photometric_brightness = lambda li: 0.2126 * li[0] + 0.7152 * li[1] + 0.0722 * li[2]

# Define frame to time conversion function (assuming video is 29.92 fps)
frame_conversion = lambda c: math.floor(c / 29.92)

# Initialize dictionary to hold frame brightness values
frame_brightness_values = {}

# Initialize list to hold image frames
image_frames = []

# Initialize count of detected lightnings
lightning_found = 0

# Start timing for performance measurement
start_time = time.time()

# Set threshold value for brightness that indicates lightning
brightness_thresshold = 20

skip_frames = 2 # number of frames to skip
sample_pixels = 300 # number of pixels to sample for brightness

while success:
    brightness_values_for_frame = []

    # Skip frames
    if count % skip_frames == 0:
        # Get the shape of the half frame
        half_frame_shape = (image.shape[0] // 2) * image.shape[1]
        
        # Sample pixels for brightness calculation
        indices = np.random.randint(0, half_frame_shape, size=sample_pixels)
        sampled_pixels = image[:image.shape[0] // 2].reshape(-1, 3)[indices]
        brightness_values_for_frame = photometric_brightness(sampled_pixels.T)
        
        # Compute average brightness for the frame
        avg = np.average(brightness_values_for_frame)


        # Append tuple (average brightness, frame number) to list
        image_frames.append((avg, count))

        # If the average brightness exceeds the threshold, it's considered as lightning
        if avg > brightness_thresshold:
            lightning_found += 1

        # Calculate the time elapsed and time per frame
        elapsed_time = time.time() - start_time
        time_per_frame = elapsed_time / count if count > 0 else 0
        
        # Estimate the time remaining (in seconds)
        remaining_frames = total_frames - count
        estimated_time_remaining = time_per_frame * remaining_frames
        
        # Convert to minutes and seconds for easier readability
        minutes, seconds = divmod(estimated_time_remaining, 60)
        
        # Print the updated progress statement
        print(f"[*] Estimated time remaining: {'0' if math.floor(minutes) < 10 else ''}{math.floor(minutes)}:{'0' if math.floor(seconds) < 10 else ''}{math.floor(seconds)}   : Lightning count {lightning_found:<3} : Frame {count:<5} : Average value {'' if avg > brightness_thresshold else ''}{avg:<5.2f} : Progress {100 * count / total_frames:<5.2f}%", end="\r")
        sys.stdout.flush()
    # Read the next frame
    success,image = vidcap.read()

    # Increase the frame count
    count += 1


# Initialize set to hold finished clip seconds
finished_clip_seconds = set()

video_count = 0

# Post-process the frames to combine into clips when lightning is detected
for k, item in enumerate(image_frames):
    brightness_val = item[0]
    frame_number = item[1]

    # If the frame is within +/- 2 seconds of a finished clip, skip it
    if frame_conversion(frame_number) - 2 in finished_clip_seconds or frame_conversion(frame_number) + 2 in finished_clip_seconds:
        continue

    # If brightness exceeds threshold (lightning detected)
    if brightness_val > brightness_thresshold:

        c.print(f"\n[white][*] Lightning frame found at {k} : Average frame brightness {brightness_val} : {video_count}")

        # Initialize list to store frames for the current clip
        video_frames = []

        # Loop through frames from 120 frames before to 120 frames after the lightning
        total_iterations = 240  # Total number of iterations in the loop

        for idx, i in enumerate(range(-120, 120)):
            if (i + k) < 0 or (i + k) > len(image_frames) - 1:
                continue
        
            # Set the video capture to the correct frame
            vidcap.set(cv2.CAP_PROP_POS_FRAMES, i + k)
            res, cv_image = vidcap.read()
        
            # Add the current second to the finished seconds to prevent overlapping clips
            finished_clip_seconds.add(frame_conversion(i + k))
        
            # Add the image frame to the video_frames list
            video_frames.append(cv_image)
            
            # Calculate the percentage progress
            progress = (idx + 1) / total_iterations * 100
        
            # Print the percentage progress
            print(f"[*] Frame processing progress: {progress:.2f}%", end="\r")
            sys.stdout.flush()


        # Attempt to save the video
        c.print("\n[white][*] [yellow]Attemping video saving")

        # Write the frames to a video file
        out = cv2.VideoWriter(f'vids/test frame middle {frame_number}.avi', cv2.VideoWriter_fourcc(*'DIVX'), 29, (1920, 1080))
        for frame in (video_frames):
            out.write(frame)

        # Close the video file
        out.release()

        # Delete the VideoWriter object
        del out

        # Confirm video saving
        c.print("[white][*] [green]Video saved")
