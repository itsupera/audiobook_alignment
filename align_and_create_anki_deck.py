import os
import argparse
import json
import logging
import re
import subprocess
from pathlib import Path
from os import listdir
from os.path import isfile, join, basename
import xml.etree.ElementTree as ET
from typing import List, Iterator, Dict

import genanki

from test_afaligner import align


def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("botocore").setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
        description='Align a Japanese audiobook with its text, using afaligner, '
                    'and create an Anki deck from it (sentence text -> sentence audio).'
    )
    parser.add_argument('data_folder', type=str,
                        help='Folder containing the data, and where to write the results to')
    parser.add_argument('book_name', type=str,
                        help='Name of the book, will be used as filename prefix and in Anki')
    parser.add_argument('--anki-deck-filepath', type=str,
                        help='Filepath to write the Anki deck to (must have .apkg extension). '
                             'Default: {book_name}.apkg')
    args = parser.parse_args()
    data_folder = args.data_folder
    book_name = args.book_name
    anki_deck_filepath = args.anki_deck_filepath
    if anki_deck_filepath is None:
        anki_deck_filepath = book_name + ".apkg"
    elif not anki_deck_filepath.endswith(".apkg"):
        raise ValueError("Anki deck filepath must have the .apkg extension !")

    # Check data folder that should exist
    if not Path(join(data_folder, "text")).exists():
        raise ValueError(f'Your data folder {data_folder} should contain a "text" sub-folder')
    if not Path(join(data_folder, "audio")).exists():
        raise ValueError(f'Your data folder {data_folder} should contain a "audio" sub-folder')

    # afaligner expects XHTML files in input
    logging.info(f"Convert TXT files to XHTML...")
    convert_text_files_to_xhtml(
        join(data_folder, 'text'),
        join(data_folder, 'xhtml'),
    )

    logging.info(f"Perform the forced alignment. This can take a while...")
    output_format = 'json'
    sync_map = align(
        join(data_folder, 'xhtml'),
        join(data_folder, 'audio'),
        output_dir=join(data_folder, output_format),
        output_format=output_format,
        sync_map_text_path_prefix=join(data_folder, "xhtml/"),
        sync_map_audio_path_prefix=join(data_folder, "audio/"),
    )

    logging.info(f"Cut audio fragments into mp3 files...")
    cut_audio_fragments(
        join(data_folder, "json"),
        join(data_folder, "audio_fragments"),
        book_name,
    )

    generate_anki_deck(data_folder, book_name, anki_deck_filepath)


def generate_anki_deck(data_folder: str, book_name: str, anki_deck_filepath: str):
    model = genanki.Model(
        1607392319,
        'Audiobook Cards',
        fields=[
            {'name': 'Sentence-Transcript'},
            {'name': 'Sentence-Audio'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Sentence-Transcript}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Sentence-Audio}}',
            },
        ])

    deck = genanki.Deck(
        2059400110,
        f'Audiobook: {book_name}'
    )

    package = genanki.Package(deck)
    package.media_files = []

    json_files_folder = join(data_folder, "json")
    json_files = list_files_with_extension(json_files_folder, "json")
    idx = 0
    for json_filename in json_files:
        part = basename(json_filename).rstrip('.json')
        sentences_by_fragment = get_sentences_by_fragment(data_folder, part)

        for fragment, sentence in sentences_by_fragment.items():
            audio_filename = generate_audio_cut_filename(part, fragment)
            audio_filepath = join(data_folder, "audio_fragments", audio_filename)

            note = genanki.Note(
                model=model,
                fields=[sentence, f"[sound:{audio_filename}]"],
                due=idx,
            )
            deck.add_note(note)

            package.media_files.append(audio_filepath)

            logging.debug(f"* Generated note for file {part}, fragment {fragment}: {sentence}")

            idx += 1

    package.write_to_file(anki_deck_filepath)


def get_sentences_by_fragment(data_folder: str, part: str) -> Dict[str, str]:
    xhtml_filepath = join(data_folder, "xhtml", f"{part}.xhtml")
    tree = ET.parse(xhtml_filepath)

    sentences_by_fragment = {}
    # ps = tree.findall(f'.//{XMLNS}p')
    ps = tree.findall(f'.//p')
    for p in ps:
        fragment = p.attrib["id"]
        sentence = p.text
        sentences_by_fragment[fragment] = sentence

    return sentences_by_fragment


def convert_text_files_to_xhtml(input_folder: str, output_folder: str):
    Path(output_folder).mkdir(exist_ok=True, parents=True)
    cleanup_folder(output_folder)

    txt_files = list_files_with_extension(input_folder, "txt")
    for txt_file in txt_files:
        logging.debug(f"* Converting {txt_file} to XHTML...")
        txt_filepath = join(input_folder, txt_file)
        xhtml_filepath = join(output_folder, txt_file.rstrip("txt") + "xhtml")
        convert_text_file_to_xhtml(txt_filepath, xhtml_filepath)


def cleanup_folder(folder: str):
    """
    Delete all the files in the given folder
    """
    for filename in listdir(folder):
        os.remove(join(folder, filename))


def convert_text_file_to_xhtml(txt_filepath: str, xhtml_filepath: str):
    """
    Create and dump a simple HTML document with each sentence within a <p> tag,
    and with a fragment id to identify it, e.g.,
    <p id="f00042">例えです。</p>
    """
    # Generate the HTML tree
    tree = ET.Element('html')
    for idx, sentence in enumerate(extract_sentences_from_txt_file(txt_filepath)):
        fragment_id = f"f{str(idx).zfill(5)}"
        elem = ET.TreeBuilder()
        elem.start('p', {"id": fragment_id})
        elem.data(sentence)
        elem.end('p')
        tree.append(elem.close())
        idx += 1

    if len(tree) == 0:
        logging.debug(f"* Skipping part with no sentences")
        return

    # Dump the file
    root = ET.ElementTree(tree)
    root.write(xhtml_filepath, encoding="utf-8")


def extract_sentences_from_txt_file(txt_filepath: str) -> Iterator[str]:
    with open(txt_filepath) as fd:
        for line in fd:
            line = line.lstrip().rstrip()
            if line:
                sentences = line.split("。")
                for sentence in sentences:
                    sentence = sentence.lstrip().rstrip()
                    if sentence:
                        yield sentence


def list_files_with_extension(folder: str, extension: str) -> List[str]:
    return [
        f for f in listdir(folder)
        if isfile(join(folder, f)) and f.lower().endswith(f".{extension}")
    ]


def cut_audio_fragments(json_files_folder: str, dst_folder: str, book_name: str):
    Path(dst_folder).mkdir(exist_ok=True, parents=True)
    cleanup_folder(dst_folder)

    json_files = list_files_with_extension(json_files_folder, "json")
    for json_file in json_files:
        json_filepath = join(json_files_folder, json_file)
        with open(json_filepath) as fd:
            data = json.load(fd)
        for fragment, fragment_data in data.items():
            logging.debug(f"* Cutting audio fragment {fragment} from {json_file}...")
            begin_ts = fragment_time_to_float(fragment_data["begin_time"])
            end_ts = fragment_time_to_float(fragment_data["end_time"])
            part = json_file.rstrip('.json')
            dst_filename = generate_audio_cut_filename(book_name, part, fragment)
            dst_filepath = join(dst_folder, dst_filename)
            crop_audio(fragment_data["audio_file"], dst_filepath, begin_ts, end_ts)


def generate_audio_cut_filename(book_name: str, part: str, fragment: str) -> str:
    return f"{book_name.replace('_', '')}_{part}_{fragment}.mp3"


def fragment_time_to_float(fragment_time: str) -> float:
    """
    :param fragment_time: for example 0:00:14.920
    :return: number of seconds
    """
    m = re.match("^(\d+):(\d+):(\d+).(\d+)$", fragment_time)
    if not m:
        raise ValueError(f"Failed to parse fragment time {fragment_time} !")
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4)) / 1000


def crop_audio(src_filename: str, dst_filename: str, begin_ts: float, end_ts: float):
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", str(begin_ts), "-to", str(end_ts), "-i", src_filename, dst_filename
    ]
    p = subprocess.Popen(cmd)
    p.wait()
    if p.returncode:
        raise ValueError(f"When cropping audio, got return code {p.returncode}. "
                         f"Cmd: {' '.join(cmd)}")

if __name__ == '__main__':
    main()
