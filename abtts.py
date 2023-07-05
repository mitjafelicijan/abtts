import os
import sys
import json
import base64
import argparse
import subprocess
import requests

from slugify import slugify
from mutagen.oggvorbis import OggVorbis
from mutagen.flac import Picture

TMP_DIR = os.environ.get("TMP_DIR", "tmp/")
OUT_DIR = os.environ.get("OUT_DIR", "out/")
US_BEARER = os.environ.get("US_BEARER", None)
US_VOICE_ID = os.environ.get("US_VOICE_ID", "male-4")
START_END_SILENCE = os.environ.get("START_END_SILENCE", "2")

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "{:.1f} {}{}".format(num, unit, suffix)
        num /= 1024.0
    return "{:.1f} {}{}".format(num, "Yi", suffix)

def generate_folder_or_exit(folder: str):
    if not os.path.exists(folder):
        print("> Creating `{}` directory...".format(folder))
        try:
            os.makedirs(folder)
        except OSError as e:
            print("ERROR: Directory creation failed: {}".format(e))
            sys.exit(1)

def parse_toc_file(folder: str) -> object:
    print("> Parsing table of contents...")

    # Check if `toc.txt` file exists in that folder.
    toc_filepath = os.path.join(args.book, "toc.txt")
    if not os.path.exists(toc_filepath):
        print("ERROR: This is not valid book. File {} does not exist.".format(toc_path))
        sys.exit(1)

    # Some general variables.
    book = {
        "title": None,
        "author": None,
        "year": None,
        "cover": None,
        "words": None,
        "length": None,
    }

    chapters = []
    paragraphs = []
    audio_files = []

    # Read TOC file and parse the data.
    with open(toc_filepath, "r") as file:
        for line in file:
            tline = line.strip()
            if tline.startswith("--"):
                sline = tline.split(maxsplit=2)
                op = sline[1].replace(":", "")
                if op in book:
                    book[op] = sline[2]
            else:
                if len(tline) > 0 and not tline.startswith("#"):
                    chapters.append(tline)

    # Check if none of the attributes are empty.
    if any(value is None for value in book.values()):
        print("ERROR: Missing values in TOC file. Check documentation.")
        for key in book.keys():
            if book[key] is None:
                print("- attribute `{}` is missing".format(key))
        sys.exit(1)

    # Appends book title slug to `book` object.
    book["slug"] = slugify(book["title"])

    # Check if chapters are provided in TOC file.
    if len(chapters) == 0:
        print("ERROR: No chapters provided in the TOC file.")
        sys.exit(1)

    book["characters"] = 0
    # Convert all chapters to paragraphs.
    print("> Parsing chapters and paragraphs...")
    for chapter in chapters:
        chapter_filepath = os.path.join(folder, chapter)
        with open(chapter_filepath, "r") as file:
            for line in file:
                line = line.strip()
                if len(line) > 0:
                    paragraphs.append(line)
                    book["characters"] += len(line) 

    # Check if there are any paragraphs.
    if len(paragraphs) == 0:
        print("ERROR: No paragraphs found for the current book.")
        sys.exit(1)

    # Check if cover file exists in that folder.
    cover_filepath = os.path.join(args.book, "toc.txt")
    if not os.path.exists(cover_filepath):
        print("ERROR: Cover file {} does not exist.".format(cover_filepath))
        sys.exit(1)


    return { "book": book, "chapters": chapters, "paragraphs": paragraphs }

def prepare_audiobook(folder: str):
    # First check if Bearer key is present.
    if not US_BEARER:
        print("ERROR: Environment variable US_BEARER not set.")
        sys.exit(1)

    meta = parse_toc_file(folder)
    
    # Generates nessesary folders.
    generate_folder_or_exit(os.path.join(TMP_DIR, meta["book"]["slug"]))
    
    # Storing JSON report for the created audiobook.
    project_filepath = os.path.join(TMP_DIR, meta["book"]["slug"], "meta.json")
    print("> Saving project file to `{}`...".format(project_filepath))
    with open(project_filepath, "w") as fp:
        json.dump(meta, fp)
        
    # Print out debug information.
    print("\nDetails found:")
    print(" - Title: {}".format(meta["book"]["title"]))
    print(" - Author: {}".format(meta["book"]["author"]))
    print(" - Year: {}".format(meta["book"]["year"]))
    print(" - Characters: {}".format(meta["book"]["characters"]))

    # Ask to continue before wasting credits.
    print("\nThis will use up ~{} characters on your account.".format(meta["book"]["characters"]))
    response = input("Continue? (y/n): ").strip().lower()
    if response != "y":
        print("Ok, bye!")
        sys.exit(0)

    # Generates wav files.
    print()
    for idx, paragraph in enumerate(meta["paragraphs"]):
        wav_filepath = os.path.join(TMP_DIR, meta["book"]["slug"] ,"{}.wav".format(idx))
        print("> Proccesing paragraphs: {}/{}".format(idx+1, len(meta["paragraphs"])), end="\r")

        # If paragraph WAV file already exists skip it.
        if os.path.exists(wav_filepath):
            continue

        # Try generating WAV audio file for the paragraph.
        try:
            response = requests.post(
                "https://api.v5.unrealspeech.com/speech",
                headers = {
                    "Authorization" : "Bearer {}".format(US_BEARER)
                },
                json = {
                    "Text": paragraph,
                    "VoiceId": US_VOICE_ID,
                    "AudioFormat": "wav",
                    }
            )

            if response.status_code != 200:
                print("ERROR: TTS failed with error {} on index {} on paragraph\n\n".format(
                    response.status_code,
                    idx,
                    paragraph
                ))
                sys.exit(1)

            with open(wav_filepath, 'wb') as fp:
                fp.write(response.content)
        except requests.exceptions.RequestException as e:
            print("ERROR: Request failed: {}".format(e))
            sys.exit(1)

    # Print report of generated files.
    print("\n\nGenerated files:")
    for idx, paragraph in enumerate(meta["paragraphs"]):
        wav_filepath = os.path.join(TMP_DIR, meta["book"]["slug"], "{}.wav".format(idx))
        if not os.path.exists(wav_filepath):
            print("ERROR: Audio file {} does not exist.".format(wav_filepath))
            sys.exit(1)
        file_size = os.path.getsize(wav_filepath)
        print(" - {}\t{}".format(wav_filepath, sizeof_fmt(file_size)))

# sox mp3.mp3 mp3withsilence.mp3 pad 0 1
def export_audiobook(folder: str):
    meta = parse_toc_file(folder)
    
    # Generates nessesary folders.
    generate_folder_or_exit(os.path.join(OUT_DIR))
    
    export_waw_filepath = os.path.join(OUT_DIR, "{}.wav".format(meta["book"]["slug"]))
    export_ogg_filepath = os.path.join(OUT_DIR, "{}.ogg".format(meta["book"]["slug"]))

    # Combine all WAV files together.
    print("> Generating file `{}`...".format(export_waw_filepath))
    sox_command = []
    sox_command.append("sox")
    for idx, paragraph in enumerate(meta["paragraphs"]):
        wav_filepath = os.path.join(TMP_DIR, meta["book"]["slug"], "{}.wav".format(idx))
        if not os.path.exists(wav_filepath):
            print("ERROR: Audio file {} does not exist.".format(wav_filepath))
            sys.exit(1)
        sox_command.append(wav_filepath)
    sox_command.append(export_waw_filepath)
    sox_command.append("pad")
    sox_command.append(START_END_SILENCE)
    sox_command.append(START_END_SILENCE)
    subprocess.call(sox_command, stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)

    # Encode WAV file to OGG file.
    print("> Encoding file `{}`...".format(export_ogg_filepath))
    ogg_command = ["oggenc", "-q", "3", "-o", export_ogg_filepath, export_waw_filepath]    
    subprocess.call(ogg_command, stdout=open(os.devnull, "w"), stderr=subprocess.STDOUT)
    
    # Add ID3 tags to the audiobook.
    print("> Adding metadata and cover...")
    audio = OggVorbis(export_ogg_filepath)
    audio["title"] = meta["book"]["title"]
    audio["artist"] = meta["book"]["author"]
    audio["albumartist"] = meta["book"]["author"]
    audio["album"] = meta["book"]["title"]
    audio["year"] = meta["book"]["year"]
    cover = Picture()
    cover.data = open(os.path.join(folder, meta["book"]["cover"]), mode="rb").read()
    cover.type = 3
    cover.mime = u"image/jpeg"
    cover_data = cover.write()
    encoded_data = base64.b64encode(cover_data)
    vcomment_value = encoded_data.decode("ascii")
    audio["metadata_block_picture"] = [vcomment_value]
    audio.save()

    print("> Done and done! Enjoy!")

if __name__ == "__main__":
    program_description = [
        "Converts books to audio format using UnrealSpeech <https://unrealspeech.com/>.",
    ]

    # Argument parsing.
    parser = argparse.ArgumentParser(description=" ".join(program_description))
    parser.add_argument("--book", help="specify folder of a book", required=True)
    parser.add_argument("--prepare", help="parses and generates processing file for audiobook", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--export", help="exports audiobook", action=argparse.BooleanOptionalAction, default=False)    
    args = parser.parse_args()

    if not args.prepare and not args.export:
        print("ERROR: you must provide at least one action.")
        sys.exit(1)

    # Prepare audiobook.
    if args.book and args.prepare:
        prepare_audiobook(args.book)

    # Export audiobook.
    if args.book and args.export:
        export_audiobook(args.book)
