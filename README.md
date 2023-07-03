# Create audiobook from text files

This program is written in Python and is using
[UnrealSpeech](https://unrealspeech.com/) under the hood for TTS.

<audio src="https://github.com/mitjafelicijan/abtts/raw/master/samples/25.mp3"></audio>

## What does it do?

- Converts text files into MP3 audiobook.
- Baked ID3 tags and cover image to MP3 file.
- Has a really awesome reading voice provided by
  [UnrealSpeech](https://unrealspeech.com/).

## Install

```sh
git clone git@github.com:mitjafelicijan/abtts.git
cd abtts
```

## How to use it

- First you need to create [UnrealSpeech](https://unrealspeech.com/) account.
- Create an API Token and store. You will need it for this.
- Generate first book that is provided with this repository.

```sh
US_BEARER="CW5RhoOX..." python3 abtts.py --book-folder=books/armageddon-2419/
```

- This will generate MP3 file in `out` directory (provided you didn't mess with
  `OUT_DIR` variable).
- A JSON report file with the same slug name as MP3 file will also be generated
  for you so you can see if all went well.

## Environmental variables

Environmental variables can prefix python command like in the example above with
`US_BEARER`.

| Variable          | Default value | Description                                      |
|-------------------|---------------|--------------------------------------------------|
| TMP_DIR           | tmp/          | Paragraph MP3's are put                          |
| OUT_DIR           | out/          | Final audiobook location                         |
| OMIT_US           | 0             | If 0 API will not get called                     |
| US_BEARER         | None          | Bearer token for UnrealSpeech                    |
| US_VOICE_ID       | male-4        | Selected voice ID (male-0..male-4)               |
| US_AUDIO_FORMAT   | mp3           | Leave to MP3!                                    |
| US_BIT_RATE       | 192k          | Leave to default value!                          |
| START_END_SILENCE | 2000          | How many seconds get added at beginning and end. |

## Create new audiobooks

- Books have a specific filesystem structure. Each book needs to have `toc.txt`
file and cover image in the same directory.
- Books should be split into chapters, but also only one chapter is sufficient.

And example of TOC file.

```
-- title: Armageddon 2419 A.D.
-- author: Philip Francis Nowlan
-- year: 1929
-- cover: cover.jpg
-- words: 27337
-- length: 1 hour 40 minutes

# foreword.txt

chapter1.txt
chapter2.txt
chapter3.txt
chapter4.txt
```

- Chapter files like `chapter1.txt` must be all in the same folder as `toc.txt`.
- You can comment lines if you want with `#`. These files will be omitted.
- Lines starting with `--` are special meta tags and (title, author, year,
  cover, words, length) are all required. They can be empty, but they must be
  provided.
- Cover images are baked into the MP3 file. Cover image MUST be a JPEG.

## Libraries used

- https://github.com/psf/requests
- https://github.com/jiaaro/pydub
- https://github.com/quodlibet/mutagen
- https://github.com/un33k/python-slugify
