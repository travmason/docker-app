import numpy as np
import tensorflow as tf
import pandas as pd
import os
import pickle

from utilities import feature_extraction as fe

def get_labels(filename):
    infile = open(filename,'rb')
    lb = pickle.load(infile)
    infile.close()
    return lb

def predict(model,signal):
    prediction = model.predict(signal,batch_size=16)
    return prediction

def print_prediction(prediction,label):
    # Get the final predicted label
    final = prediction.argmax(axis=1)
    final = final.astype(int).flatten()
    final = (label.inverse_transform((final)))
    print(final) #emo(final)

def return_prediction(prediction,label):
    final = prediction.argmax(axis=1)
    percentage = round(prediction[0][int(final)],2)
    final = final.astype(int).flatten()
    final = (label.inverse_transform((final)))
    return final[0], percentage

def process_signal(filepath, sampling_rate, audio_duration):
    offset = 0.0

    signal, rms = fe.get_audio_features(filepath,sampling_rate, mfcc = True, audio_duration = audio_duration,offset=offset)
    signal = np.transpose(signal)

    # Used to reshape signal for LSTM
    signal = signal.reshape((signal.shape[0],signal.shape[1]))
    signal_np = signal.reshape((1,)+signal.shape)

    return signal_np, rms

def run_prediction(model,path,label):
    signal, rms = process_signal(path, 44100, 2.5)
    threshold = 0.01
    if rms < threshold:
        silence = "not_applicable"
        return silence , None
    else:
        pred = predict(model, signal)
        emotion, percent = return_prediction(pred,label)
        return emotion, percent

def process_dataframe(model,dataframe,label):
    pred_emotion = []
    confidence = []
    print("Inferencing..")
    for path in dataframe.path:
        emotion, percent = run_prediction(model,path,label)
        pred_emotion.append(emotion)
        confidence.append(percent)

    emotions_df = pd.DataFrame(pred_emotion,columns = ["predictions"])
    confidence_df = pd.DataFrame(confidence,columns = ["confidence"])
    final_df = pd.concat([emotions_df,confidence_df],axis=1)
    print("Inferencing completed!")
    return final_df