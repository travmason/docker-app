import os
import numpy as np
import pandas as pd

def load_csv_dir(path,name):
    try:
        df = pd.read_csv(os.path.join(path, name + ".csv"))
        return df
    except FileNotFoundError:
        return None

def load_data_np(path,filename):
    data_array = np.load(os.path.join(path, filename + ".npy"))
    return data_array

def directorylist(sourcepath):
    dir_list = os.listdir(sourcepath)
    dir_list.sort()
    counter = 0
    for item in dir_list:
        if item.startswith('.') and os.path.isfile(os.path.join(sourcepath, item)):
            del dir_list[counter]
            return dir_list
        counter +=1
    return dir_list

def save_processed_data_np(path,name,data):
    directory = path
    if not os.path.exists(directory):
        os.makedirs(directory)
    np.save(os.path.join(directory,name),data)    

def combine_arrays(arr_1, arr_2):
    return np.concatenate((arr_1,arr_2))

# To strip any hidden files
def strip_hidden(list_dir):
    return [i for i in list_dir if not i.startswith(".")]

def convert_name(name):
    string_name = list(map(str.capitalize,name.split("_")))
    return " ".join(string_name)

def get_name(name):
    file_name = filter(None,name.lower().split(" "))
    return "_".join(file_name)

def write_status(name,session,status):
    with open(os.path.join('instance','patients',name,session,'.status'), 'w') as file:
        file.write(str(status))

def read_status(name,session):
    with open(os.path.join('instance','patients',name,session,'.status'), 'r') as file:
        status = file.read()
    return status