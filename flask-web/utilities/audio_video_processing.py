## Basics ##
import time
import pandas as pd
import os

## Audio Preprocessing ##
import librosa
from pydub import AudioSegment as audsg

def extract_audio_pydub(video_path,file_name,patient_name,session,extension = "mp3"):
    rel_path, name = os.path.split(video_path)
    output_name = patient_name + "_source_"+ session + "." + extension
    try:
        print("Exporting..")
        audsg.from_file(video_path).export(os.path.join(rel_path,output_name), format=extension)
        print("Export complete!")
    except FileNotFoundError:
        audsg.from_file(os.path.join(video_path)).export(os.path.join(rel_path,output_name), format=extension)
        print("Export complete!")
    return os.path.join(rel_path,output_name)

def convertSeconds(seconds):
    h = int(seconds//(60*60))
    m = int((seconds-h*60*60)//60)
    s = int(seconds-(h*60*60)-(m*60))
    if h < 10:
        h = "0" + str(h)
    if m < 10:
        m = "0" + str(m)
    if s < 10:
        s = "0" + str(s)
    return str(h) +":"+str(m)+":"+str(s)

def split_audio_to_segments(audio_path,patient,session,audio_filename):
    name = []
    paths = []
    time_intervals = []
    rms = []
    filepath = os.path.join(audio_path,audio_filename)
    audio_file = audsg.from_mp3(filepath)
    n = len(audio_file)
    interval = 3 * 1000
    overlap = 0 * 1000

    # Initialize start and end seconds to 0 
    start = 0
    end = 0

    # Flag to keep track of end of file. 
    # When audio reaches its end, flag is set to 1 and we break 
    flag = False
    counter = 1
    # Iterate from 0 to end of the file, 
    # with increment = interval 
    for i in range(0, n, interval): 
        
        # During first iteration, 
        # start is 0, end is the interval 
        if i == 0: 
            start = 0
            end = interval 
    
        # All other iterations, 
        # start is the previous end - overlap 
        # end becomes end + interval 
        else: 
            start = end - overlap 
            end = start + interval  
    
        # When end becomes greater than the file length, 
        # end is set to the file length 
        # flag is set to 1 to indicate break. 
        if end >= n: 
            end = n 
            flag = True
    
        # Storing audio file from the defined start to end 
        chunk = audio_file[start:end] 
    
        # Filename / Path to store the sliced audio
        file_name = "_".join([patient,session,"seg",str(counter)]) + '.mp3'
        path = os.path.join(audio_path,"chunks",file_name)
        # Store the sliced audio file to the defined path 
        try:
            chunk.export(path, format ="mp3") 
        except OSError:
            new_dir = os.path.join(audio_path,"chunks")
            os.makedirs(new_dir)
            chunk.export(path, format ="mp3")

        # Print information about the current chunk 
        # rms.append(mp.get_rms_value(path))
        name.append(file_name)
        time_intervals.append(convertSeconds(start/1000) + " - " + convertSeconds(end/1000))
        paths.append(path)
        # Increment counter for the next chunk 
        counter = counter + 1

        if flag: 
            break
    print("\nCompleted chunk segmentation!")
    name_df = pd.DataFrame(name,columns = ["filename"])
    time_df = pd.DataFrame(time_intervals,columns = ["intervals"])
    path_df = pd.DataFrame(paths,columns = ["path"])
    # rms_df = pd.DataFrame(rms,columns=["rmse"])
    df = pd.concat([name_df,time_df,path_df],axis=1)
    return df
