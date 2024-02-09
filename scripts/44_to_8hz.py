from pydub import AudioSegment


def convert_sample_rate(input_path, output_path, target_rate):
    audio = AudioSegment.from_file(input_path)
    converted_audio = audio.set_frame_rate(target_rate)
    converted_audio.export(output_path, format="wav")


# Пример использования
input_file_path = "/home/m/works/pykaldi_docker/wav_audio/example.wav"
output_file_path = "../wav_audio/55342_8hz.wav"
target_sample_rate = 8000

convert_sample_rate(input_file_path, output_file_path, target_sample_rate)