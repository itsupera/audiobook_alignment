from os.path import join
from pathlib import Path

from pyjuliusalign import alignFromTextgrid


path = join(".", "files")
cabochaOutput = join(path, "cabocha_output")
alignedOutput = join(path, "aligned_output")

# Clone https://github.com/julius-speech/segmentation-kit here
juliusScriptPath = join(".", "segmentation-kit")
soxPath = "/opt/local/bin/sox"
cabochaPath = "/usr/local/bin/cabocha"
perlPath = "/opt/local/bin/perl"

# One of: 'jis-shift', 'utf-8', or 'euc-jp'
# Whichever cabocha was installed with
cabochaEncoding = "utf-8"


# Use this to convert your textgrids to .txt files which are used by julius
# If you do not have textgrids or you already have text transcripts, skip this step
# print("\nSTEP 1: Generating transcripts")
# alignFromTextgrid.textgridToCSV(inputPath=path,
#                                 outputPath=path,
#                                 outputExt=".txt")

# Julius expects kana, so we must first convert kanji to kana
# If your transcripts are all in kana, skip this step
print("\nSTEP 2: Converting all text to kana")
alignFromTextgrid.convertCorpusToKanaAndRomaji(inputPath=path,
                                               outputPath=cabochaOutput,
                                               cabochaEncoding=cabochaEncoding,
                                               cabochaPath=cabochaPath,
                                               encoding="utf-8")

print("\nSTEP 3: Run the force aligner")
alignFromTextgrid.forceAlignCorpus(wavPath=path,
                                   txtPath=cabochaOutput,
                                   outputPath=alignedOutput,
                                   juliusScriptPath=juliusScriptPath,
                                   soxPath=soxPath,
                                   perlPath=perlPath)
