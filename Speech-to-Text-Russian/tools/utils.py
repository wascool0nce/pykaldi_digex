import json
import os
import glob
import shutil
import logging
from pathlib import Path
import pandas as pd
import wave
import pysubs2
import librosa
import soundfile

def clear_folder(folder):
    """
    Удаление всех файлов из директории
    
    Аргументы:
        folder: путь к директории
    """
    files = glob.glob(str(Path(folder) / '*'))
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            print(e)

def delete_folder(folder):
    """
    Удаление директории
    
    Аргументы:
        folder: путь к директории
    """
    try:
        shutil.rmtree(folder, ignore_errors=True)
    except Exception as e:
        print(e)

def prepare_wav(wav):
    """
    Конвертация аудио файла

    Аргументы:
        wav: путь к .WAV файлу аудио

    Результат:
        wav: путь к конвертированному .WAV файлу аудио
    """
    parts = wav.split('.')
    try:
        wave.open(wav, 'r')
    except:
        old_wav = wav + ""
        try:
            wav_file, sr = librosa.load(wav, sr=None, mono=False)
        except:
            return wav
        parts[-1] = "wav"
        wav = '.'.join(parts)
        try:
            soundfile.write(wav, wav_file.T, sr, format='WAV')
        except:
            return old_wav
        if old_wav != wav:
            os.remove(old_wav)
    return wav

def make_wav_scp(wav, scp):
    """
    Формирование .SCP файла для аудио
    
    Аргументы:
        wav: путь к .WAV файлу аудио
        scp: путь к .SCP файлу с аудио
    """
    with open(scp, 'w') as f:
        wav_file = wave.open(wav, 'r')
        if wav_file.getnchannels() == 1:
            f.write(str(Path(wav).stem) + '.0\t' + 'sox ' + wav + ' -t wav - remix 1 |\n')
        else:
            f.write(str(Path(wav).stem) + '.0\t' + 'sox ' + wav + ' -t wav - remix 1 |\n')
            f.write(str(Path(wav).stem) + '.1\t' + 'sox ' + wav + ' -t wav - remix 2 |\n')          

def make_spk2utt(utt2spk):
    """
    Формирование spk2utt файла
    
    Аргументы:
        utt2spk: путь к файлу сопоставления сегментов и говорящих

    Результат:
        spk2utt: путь к файлу перечисления сегментов для каждого говорящего
    """
    spk2utt = str(Path(utt2spk).parents[0] / 'spk2utt')
    utt2spk_df = pd.read_csv(utt2spk, sep='\t', header=None, names=['utt_id', 'speaker_id'])
    spk2utt_df = utt2spk_df.groupby('speaker_id')['utt_id'].apply(lambda x: ' '.join(x)).reset_index()
    spk2utt_df.to_csv(spk2utt, sep='\t', index=False, header=False)
    return spk2utt


def convert_time_to_str(milliseconds):
    """
    Преобразование времени в строковый формат (чч:мм:сс.мс)
    """
    total_seconds = milliseconds / 1000
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{int(hours):02}:{int(minutes):02}:{seconds:06.3f}'


def make_subtitles_data(segments, transcriptions, utt2spk, json_file):
    """
    Generate subtitles data in the desired format

    Arguments:
       wav: audio file name
       segments: path to the segments description file
       transcriptions: path to the transcriptions file
       utt2spk: path to the speaker mapping file

    Returns:
       subtitles_data: list of dictionaries containing subtitles data
    """
    segments_df = pd.read_csv(segments, header=None, sep=' ', names=['utt_id', 'wav', 'start', 'end'])
    transcriptions_df = pd.read_csv(transcriptions, sep='\t', header=None, names=['utt_id', 'text'])
    utt2spk_df = pd.read_csv(utt2spk, sep='\t', header=None, names=['utt_id', 'speaker'])
    events = segments_df.merge(transcriptions_df, how='left', on='utt_id').merge(utt2spk_df, how='left',
                                                                                 on='utt_id').fillna('')
    json_data = []
    for row in events.values:
        start_time = pysubs2.make_time(s=float(row[2]))
        end_time = pysubs2.make_time(s=float(row[3]))

        segment_info = {
            'speaker': row[5],
            'start': convert_time_to_str(start_time),
            'end': convert_time_to_str(end_time),
            'text': row[4]
        }
        json_data.append(segment_info)

    with open(json_file, 'w', encoding='utf-8') as json_output:
        json.dump(json_data, json_output, indent=2, ensure_ascii=False)


# def make_ass(wav, segments, transcriptions, utt2spk, ass, json_file):
#     """
#     Формирование .ASS файла из транскрибаций и JSON файла с информацией о сегментах
#
#     Аргументы:
#        wav: наименование аудио файла
#        segments: путь к файлу описания сегментов
#        transcriptions: путь к файлу транскрибации
#        utt2spk: путь к файлу сопоставления сегментов и говорящих
#        ass: путь к .ASS файлу субтитров
#        json_file: путь к JSON файлу с информацией о сегментах
#     """
#     sub = pysubs2.SSAFile()
#     sub.info['Title'] = 'Default Aegisub file'
#     sub.info['YCbCr Matrix'] = 'None'
#     sub.aegisub_project['Audio File'] = wav
#     sub.aegisub_project['Scroll Position'] = 0
#     sub.aegisub_project['Active Line'] = 0
#     segments_df = pd.read_csv(segments, header=None, sep=' ', names=['utt_id', 'wav', 'start', 'end'])
#     transcriptions_df = pd.read_csv(transcriptions, sep='\t', header=None, names=['utt_id', 'text'])
#     utt2spk_df = pd.read_csv(utt2spk, sep='\t', header=None, names=['utt_id', 'speaker'])
#     events = segments_df.merge(transcriptions_df, how='left', on='utt_id').merge(utt2spk_df, how='left', on='utt_id').fillna('')
#     json_data = []
#     for row in events.values:
#         start_time = pysubs2.make_time(s=float(row[2]))
#         end_time = pysubs2.make_time(s=float(row[3]))
#         event = pysubs2.SSAEvent(start=start_time, end=end_time, text=row[4], name=row[5])
#         sub.events.append(event)
#
#         segment_info = {
#             'speaker': row[5],
#             'start': convert_time_to_str(start_time),
#             'end': convert_time_to_str(end_time),
#             'text': row[4]
#         }
#         json_data.append(segment_info)
#
#     sub.sort()
#     sub.save(ass, format_='ass')
#
#     with open(json_file, 'w', encoding='utf-8') as json_output:
#         json.dump(json_data, json_output, indent=2, ensure_ascii=False)

def create_logger(logger_name, logger_type, logger_level, filename=None):
    """
    Создание логгера
    
    Аргументы:
        logger_name: название логгера
        logger_type: тип логгера
        logger_level: уровень логирования
        filename: название файла лога

    Результат:
        logger: объект логгера        
    """    
    logger = logging.getLogger(logger_name)
    if logger_type == 'file':
        file_handler = logging.FileHandler(filename=filename)
        formatter = logging.Formatter(fmt='%(asctime)s \t %(levelname)s \t %(message)s',
                                            datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.setLevel(logger_level)
        logger.propagate = False
    elif logger_type == 'stream':
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter(fmt='%(levelname)s: %(message)s (%(asctime)s)')
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        logger.setLevel(logger_level)       
    return logger



