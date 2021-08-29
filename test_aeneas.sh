#!/bin/bash
# Testing aeneas ( https://github.com/readbeyond/aeneas )

# Using espeak-ng for TTS => performs really badly :(
#python3 -m aeneas.tools.execute_task \
#    "$PWD/samples/sample1.wav" \
#    "$PWD/samples/sample1_phonemes.txt" \
#    "task_language=JA|os_task_file_format=aud|is_text_type=plain" -r="tts=espeak-ng|allow_unlisted_languages=True" \
#    "$PWD/markers.txt" \
#    --output-html

# Testing with AWS Polly => working perfectly !
# (you need to set up AWS credentials and give permissions to the user to use this service)
python3 -m aeneas.tools.execute_task \
    "$PWD/samples/sample1.wav" \
    "$PWD/samples/sample1_kanji.txt" \
    "task_language=Takumi|os_task_file_format=aud|is_text_type=plain" \
    -r="allow_unlisted_languages=True|tts=aws" \
    "$PWD/markers.txt" \
    --output-html \
    -vv

firefox "$PWD/markers.txt.html"
