Japanese Audiobook Alignment
=============================

Trying to do [force-align](https://github.com/pettarin/forced-alignment-tools#definition-of-forced-alignment)
a Japanese audiobook with the book's text.

The basic idea is to match each sentence in the book's text with its utterance in the audiobook.
I am interested in doing so to easily get the audio corresponding to Anki card I mine for a book,
or even generate an Anki deck with both the text and audio for every sentence in the book.

As a simple benchmark, I try to perform the same alignment using the methods described below.

To install the required dependencies:
```bash
pip3 install -r requirements.txt
```

Aeneas
-------

Code: [test_aeneas.sh](./test_aeneas.sh)

[aeneas](https://github.com/readbeyond/aeneas) is a Python/C library that perform forced-alignment
by generating speech from the text, and comparing this
audio with the original audio (using the DTW algorithm to compute an alignment between the two sequences).

Using my [furiganalyse](https://github.com/itsupera/furiganalyse) tool,
I converted the EPUB file's chapters to TXT files and took a sample to feed aeneas with.

Performance completely depends on the TTS (text-to-speech) engine used internally:
- AWS Polly: the alignment is perfect ! Just a few silences remaining at the beginning of some sentences, 
  but that can be easily dealt with.
- espeak-ng (open-source TTS suggested in aeneas sample codes): did not work at all, this might be due
  to [phonemes that are recognized](https://github.com/espeak-ng/espeak-ng/issues/566#issuecomment-880100908)

Afaligner
----------

Code: [test_afaligner.py](./test_afaligner.py)

[Afaligner](https://github.com/r4victor/afaligner) is a library for forced-alignment of books with audiobooks.
It uses aeneas under the hood, so it worked equally well as the standalone aeneas.

The only difference is that it is using fragments from an XHTML as the sentences to align.
I had to add those fragment ids to the XHTML, as the original files did not have them.


Julius / pyjuliusalign
-----------------------

Code: [test_pyjuliusalign.py](./test_pyjuliusalign.py)

[pyjuliusalign](https://github.com/timmahrt/pyJuliusAlign) is a library that performs forced alignment
specifically for Japanese, using speech recognition engine [Julius](https://github.com/julius-speech/julius).
It takes the opposite approach as aeneas:
it recognized the phonemes in the audio (using Julius), then compares them to the
phonemes extracted from the text to get the alignment.

Something is not working, need to debug it...
