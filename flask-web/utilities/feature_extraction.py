# feature_extracting
import librosa
import pandas as pd
import numpy as np

def get_audio_features(audio_path, sampling_rate, offset = 0.5,audio_duration = 2.5, mfcc = True, noise=False, shift=False):
    X, sample_rate = librosa.load(audio_path ,res_type='kaiser_fast',duration=audio_duration,sr=sampling_rate,offset=offset)
    rms = librosa.feature.rms(y=X,pad_mode='constant')
    final_rms = np.mean(rms)
    X = apply_padding(X,sample_rate,audio_duration,offset)
    if noise:
        pass
        # X = aug.noise(X)
    if shift:
        pass
        # X = aug.shift(X)
    mel_feq_spec = get_logmel_spectrogram(X,sample_rate)    
    if mfcc:
        mfccs = librosa.feature.mfcc(S=mel_feq_spec,sr=sample_rate)
        return mfccs, final_rms
    return mel_feq_spec, final_rms

def apply_padding(data,sampling_rate,audio_duration,offset):
    input_length = sampling_rate * audio_duration
    if len(data) > input_length:
        max_offset = len(data) - input_length
        offset = np.random.randint(max_offset)
        data = data[offset:(input_length+offset)]
    else:
        if input_length > len(data):
            max_offset = input_length - len(data)
            offset = np.random.randint(max_offset)
        else:
            offset = 0
        data = np.pad(data, (offset, int(input_length) - len(data) - offset), "constant")
    return data

def get_logmel_spectrogram(signal, sampling_rate):
    spectrogram = librosa.feature.melspectrogram(signal,sr=sampling_rate)
    mel_feq_spec = librosa.power_to_db(S=spectrogram,ref=np.max)
    return mel_feq_spec

def get_pitch_mag(spectrogram,sampling_rate):
    pitch, mag = librosa.core.piptrack(S=spectrogram,sr=sampling_rate)
    return pitch, mag

def load_signal(audio_path, sampling_rate, offset = 0.5,audio_duration = 2.5):
    signal, sample_rate = librosa.load(audio_path ,res_type='kaiser_fast',duration=audio_duration, sr=sampling_rate,offset=offset)
    return signal, sample_rate

def get_rms(path):
    signal, _ = load_signal(path,44100)
    rms = librosa.feature.rms(y=signal,pad_mode='constant')
    return rms