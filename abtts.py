import os
import sys
import json
import argparse
import requests

from slugify import slugify
from pydub import AudioSegment

from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TYER, TENC, error

TMP_DIR = "tmp/"
OMIT_US = int(os.environ.get("OMIT_US", 0))
US_BEARER = os.environ.get("US_BEARER", None)
US_VOICE_ID = os.environ.get("US_VOICE_ID", "male-4")
US_AUDIO_FORMAT = os.environ.get("US_AUDIO_FORMAT", "mp3")
US_BIT_RATE = os.environ.get("US_BIT_RATE", "192k")
START_END_SILENCE = int(os.environ.get("START_END_SILENCE", 2000))

if __name__ == "__main__":
    program_description = [
        "Converts books to audio format using UnrealSpeech <https://unrealspeech.com/>.",
    ]

    # Argument parsing.
    parser = argparse.ArgumentParser(description=" ".join(program_description))
    parser.add_argument("--book-folder", help="specify folder of a book", required=True)
    args = parser.parse_args()

    # First check if Bearer key is present.
    if not US_BEARER:
        print("ERROR: Environment variable US_BEARER not set.")
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

    # Check if book exists. This checks if `toc.txt` file exists in that folder.
    toc_path = "{}/toc.txt".format(args.book_folder)
    if not os.path.exists(toc_path):
        print("! ERROR: This is not valid book. File {} does not exist.".format(toc_path))
        sys.exit(1)

    # Read TOC file and parse the data.
    with open(toc_path, "r") as file:
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
        print("! ERROR: Missing values in TOC file. Check documentation.")
        for key in book.keys():
            if book[key] is None:
                print("- attribute `{}` is missing".format(key))
        sys.exit(1)

    # Check if chapters are provided in TOC file.
    if len(chapters) == 0:
        print("! ERROR: No chapters provided in the TOC file.")
        sys.exit(1)

    # Check if chapter files exist.
    chapter_file_failure = False
    for chapter in chapters:
        chapter_path = "{}{}".format(args.book_folder, chapter)
        if not os.path.exists(chapter_path):
            print(" - file `{}` does not exist".format(chapter_path))
            chapter_file_failure = True
    if chapter_file_failure:
        sys.exit(1)        

    # Convert all chapters to paragraphs.
    for chapter in chapters:
        with open("{}/{}".format(args.book_folder, chapter), "r") as file:
            for line in file:
                line = line.strip()
                if len(line) > 0:
                    paragraphs.append(line)

    # Check if there are any paragraphs.
    if len(paragraphs) == 0:
        print("! ERROR: No paragrapgs found for the current book.")
        sys.exit(1)

    # Make temporary directory for audio files.
    if not os.path.exists(TMP_DIR):
        try:
            os.makedirs(TMP_DIR)
        except OSError as e:
            print("! ERROR: Directory creation failed: {}".format(e))

    # Convert all paragraphs to audio files.
    if not OMIT_US:
        print("> Requesting audio files...")
        for idx, paragraph in enumerate(paragraphs):
            print("> Proccesing paragraphs: {}/{}".format(idx+1, len(paragraphs)), end="\r")
            try:
                response = requests.post(
                    "https://api.v5.unrealspeech.com/speech",
                    headers = {
                        "Authorization" : "Bearer {}".format(US_BEARER)
                    },
                    json = {
                        "Text": paragraph,
                        "VoiceId": US_VOICE_ID,
                        "AudioFormat": US_AUDIO_FORMAT,
                        "BitRate": US_BIT_RATE,
                    }
                )
                
                with open("{}/{}.mp3".format(TMP_DIR, idx), 'wb') as fp:
                    fp.write(response.content)
            except requests.exceptions.RequestException as e:
                print("! ERROR: Request failed: {}".format(e))
                

    # Generate slug for book filename.
    audiobook_path = "{}.mp3".format(slugify(book["title"]))
    
    # Combine all audio paragraphs into one Mp3 file.
    print("> Combining all audio paragraphs into one audio file...")
    audio_segments = []
    audio_segments.append(AudioSegment.silent(duration=START_END_SILENCE))
    for idx, paragraph in enumerate(paragraphs):
        paragraph_audio_path = "{}/{}.mp3".format(TMP_DIR, idx)
        audio_segments.append(AudioSegment.from_file(paragraph_audio_path, format="mp3"))
    audio_segments.append(AudioSegment.silent(duration=START_END_SILENCE))
                              
    combined_audio = audio_segments[0]
    for segment in audio_segments[1:]:
        combined_audio += segment

    combined_audio.export(audiobook_path, format="mp3")

    # Edit tags and cover.
    print("> Adding metadata and cover...")
    audio = MP3(audiobook_path, ID3=ID3)
    audio.tags.add(TIT2(encoding=3, text=book["title"]))
    audio.tags.add(TPE1(encoding=3, text=book["author"]))
    audio.tags.add(TYER(encoding=3, text=book["year"]))
    audio.tags.add(TENC(encoding=3, text="https://github.com/mitjafelicijan/abtts"))
    audio.tags.add(
        APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc=u"Cover",
            data=open("{}/{}".format(args.book_folder, book["cover"]), mode="rb").read()
        )
    )
    audio.save()
    
    print("> Done and done...")
    
    # Parse all chapters into paragraphs
    with open("{}.json".format(slugify(book["title"])), "w") as file:
        json.dump({ "book": book, "chapters": chapters, "paragraphs": paragraphs }, file)
