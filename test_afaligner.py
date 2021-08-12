import shutil
from pathlib import Path

from afaligner import align

import add_fragments_to_html

Path("afaligner_data/audio").mkdir(exist_ok=True, parents=True)
shutil.copy("samples/sample1.wav", "afaligner_data/audio/sample1.wav")
add_fragments_to_html.main()

sync_map = align(
    'afaligner_data/text',
    'afaligner_data/audio',
    output_dir='afaligner_data/smil/',
    output_format='smil',
    sync_map_text_path_prefix='../text/',
    sync_map_audio_path_prefix='../audio/'
)
