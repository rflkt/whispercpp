import argparse
from whispercpp import Whisper

def transcribe_file(file_path):
    w = Whisper.from_pretrained("tiny.en")
    res = w.transcribe_from_file(file_path)
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", default="../../samples/jfk.wav", help="Path to the audio file", nargs='?')
    args = parser.parse_args()

    res = transcribe_file(args.file_path)
    print(res)
