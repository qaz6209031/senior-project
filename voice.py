# import aiy.voice.tts
# from aiy.board import Board
# from aiy.cloudspeech import CloudSpeechClient

from data import getData
def main():
    data = getData()
    print(data)
#    client = CloudSpeechClient()
#    with Board() as board:
#        while True:
#            print('Say something or repeat after me or bye')
#            text = client.recognize()
#            if text is None:
#                print('You said nothing.')
#                continue
#            print('You said', text)
#            text = text.lower()
#            if 'repeat after me' in text:
#                # Remove "repeat after me" from the text to be repeated
#                to_repeat = text.replace('repeat after me', '', 1)
#                aiy.voice.tts.say(to_repeat)
#            elif 'goodbye' in text:
#                break


if __name__ == '__main__':
    main()
