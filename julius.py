import contextlib
import os
import shutil
from math import sqrt
from pathlib import Path

from PySegmentKit import PySegmentKit

TRANSCRIPT_FILEPATH = "samples/sample1_kanji.txt"
PHONEMES_TRANSCRIPT_FILEPATH = "samples/sample1_phonemes.txt"
AUDIO_FILEPATH = "samples/sample1.wav"
OUTPUT_FILEPATH = "samples/sample1_julius_markers.txt"
CORRECT_TIMINGS_FILEPATH = "samples/sample1_correct_markers.txt"

text = open(TRANSCRIPT_FILEPATH).read()

sentences = [s.strip() for s in text.rstrip().rstrip("。").split("。")]
print(f"sentences = {sentences}")

with open(PHONEMES_TRANSCRIPT_FILEPATH) as fd:
    transcripts = [line.rstrip() for line in fd]

assert len(sentences) == len(transcripts)

# To use PySegmentKit, must put both phonetic transcript and audio file in the

workdir = "julius/"
Path(workdir).mkdir(exist_ok=True, parents=True)

with open(os.path.join(workdir, "tmp.txt"), "w") as f:
    for transcript in transcripts:
        f.write("silB " + transcript + " silE \n")
        print(transcript + "\n")

shutil.copy(AUDIO_FILEPATH, os.path.join(workdir, "tmp.wav"))

sk = PySegmentKit(workdir,
                  disable_silence_at_ends=True,
                  leave_dict=False,
                  debug=True,
                  triphone=False,
                  input_mfcc=False)

# Hide the prints
with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
    segmented = sk.segment()

basenames = list(segmented.keys())
# We copied only one wav file and its transcript, so we should only get one result.
assert len(basenames) == 1, basenames


sentences_idx = 0
sentences_timing = []
for begin_time, end_time, unit in segmented[basenames[0]]:
    if unit == "silB":
        sentence_start = end_time
    elif unit == "silE":
        sentence_end = begin_time
        sentences_timing.append((sentences[sentences_idx], sentence_start, sentence_end))
        sentences_idx += 1

    print("{:.7f} {:.7f} {}".format(begin_time, end_time, unit))

with open(OUTPUT_FILEPATH, "w") as fd:
    for sentence, sentence_start, sentence_end in sentences_timing:
        fd.write(f"{sentence_start}\t{sentence_end}\t{sentence}\n")

print("--------------------------")

# Evaluate the result by computing the distance to the correct timings
with open(CORRECT_TIMINGS_FILEPATH) as fd:
    correct_timings = []
    for line in fd:
        begin_time, end_time, sentence = line.rstrip().split('\t')
        correct_timings.append((sentence, float(begin_time), float(end_time)))

distance = 0
for (sentence, begintime, endtime), (_sentence, begintime_correct, endtime_correct) in zip(sentences_timing, correct_timings):
    assert sentence == _sentence
    print("{:.7f} {:.7f} VS {:.7f} {:.7f} {}".format(begintime, endtime, begintime_correct, endtime_correct, sentence))
    distance += (begintime_correct - begintime) ** 2 + (endtime_correct - endtime) ** 2

print("--------------------------")
print(f"Distance: {sqrt(distance)}")
