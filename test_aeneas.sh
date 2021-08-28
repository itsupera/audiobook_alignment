#!/bin/bash

python3 -m aeneas.tools.execute_task \
    "$PWD/samples/sample1.wav" \
    "$PWD/samples/sample1_phonemes.txt" \
    "task_language=JA|os_task_file_format=aud|is_text_type=plain" -r="tts=espeak-ng|allow_unlisted_languages=True" \
    "$PWD/markers.txt" \
    --output-html

firefox "$PWD/markers.txt.html"
