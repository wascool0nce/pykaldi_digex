from pydub import AudioSegment

def convert_mp3_to_wav(input_file, output_file):
    # Загрузка MP3 файла
    audio = AudioSegment.from_mp3(input_file)

    # Сохранение в WAV формате
    audio.export(output_file, format="wav")

if __name__ == "__main__":
    input_mp3_file = "../wav_audio/MIC008_test.mp3"
    output_wav_file = "../wav_audio/MIC008_test.wav"

    convert_mp3_to_wav(input_mp3_file, output_wav_file)

    print(f"Конвертация завершена. Файл сохранен как {output_wav_file}")