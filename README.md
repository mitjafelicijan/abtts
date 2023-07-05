# Create audiobooks from text files

- This program is written in Python and is using
  [UnrealSpeech](https://unrealspeech.com/) under the hood for TTS.
- Check out an [audio sample of a paragraph](./samples/paragraph.mp3) to see the
  quality of audio.

## What does it do?

- Converts text files into OGG audiobook.
- Bakes metatags and cover image to OGG file.
- Has a really awesome reading voice provided by
  [UnrealSpeech](https://unrealspeech.com/).

## Installation

**Program uses [virtual
environments](https://docs.python.org/3/library/venv.html) so make sure that you
have Python, Pip and virtual environments installed properly.**

On macOS you will need [brew.sh](https://brew.sh/) installed.

- [SoX - Sound eXchange](https://sox.sourceforge.net/)
  - On Debian-like systems - `sudo apt install sox`
  - On macOS - `brew install sox`
- [Vorbis tools](https://github.com/xiph/vorbis-tools)
  - On Debian-like systems - `sudo apt install vorbis-tools`
  - On macOS - `brew install vorbis-tools`
- Then follow instructions below.

```sh
git clone git@github.com:mitjafelicijan/abtts.git
cd abtts

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## How to use it

Creating audiobooks is a two step process. First you prepare an audiobook and
then you export it.

Pre-requirements:

- First you need to create [UnrealSpeech](https://unrealspeech.com/) account.
- Create an API Token and store it somewhere safe. You will need it for this.
- Generate first book that is provided with this repository. Use the API token
  in `US_BEARER` environment variable like in example below.
- Be sure you are in Python virtual environment.

To see all the options you can do `python abtts.py --help`.

> This example book was taken from [Standard
> Ebooks](https://standardebooks.org/ebooks/philip-francis-nowlan/armageddon-2419-a-d). They
> have an amazing assortment of books. You should definitely check them out. All
> of their material is available on [GitHub](https://github.com/standardebooks)
> as well.

### Preparing audiobook

- This will parse TOC file and call TTS API and generate a bunch of WAV files
  for each paragraphs from the book in the `out` directory (provided you didn't
  mess with `OUT_DIR` variable). Mind the `--prepare` flag.
- A JSON report file will also be generated in the `out` directory for you so
  you can see if all went well.
- If by any chance this fails for a paragraph with 500 code you can execute the
  command again and it will skip already existing and generated
  paragraphs. Sometimes UnrealSpeech API can behave badly so don't worry about
  it and just re-run the script.

```sh
US_BEARER="CW5RhoOX..." python3 abtts.py --book=books/armageddon-2419/ --prepare
```

### Exporting audiobook

- This is a simpler process which combines all the WAV files that were outcome
  from prepare procedure and generates one WAV file.
- Then encoding happens where this WAV file is encoded to OGG file. This may
  take some time. These files can get gigabytes in size. Be patient.
- After that metatags and book cover are embedded in OGG file.
- Mind the `--export` flag.

```sh
US_BEARER="CW5RhoOX..." python3 abtts.py --book=books/armageddon-2419/ --export
```

## Environmental variables

Environmental variables can prefix python command like in the example above with
`US_BEARER`.

| Variable          | Default value | Description                                     |
|-------------------|---------------|-------------------------------------------------|
| TMP_DIR           | tmp/          | Paragraph WAV's files are put here              |
| OUT_DIR           | out/          | Final audiobook location                        |
| US_BEARER         | None          | Bearer token for UnrealSpeech                   |
| US_VOICE_ID       | male-4        | Selected voice ID (male-0..male-4)              |
| START_END_SILENCE | 2000          | How many seconds get added at beginning and end |

## Create new audiobooks

- Books have a specific filesystem structure. Each book needs to have `toc.txt`
  file and cover image in the same directory.
- Each book should have it's own directory to itself. Do not mix and match
  multiple books together.
- Books should be split into chapters, but also only one chapter is sufficient.

And example of a TOC file (`toc.txt`).

```sql
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
- Lines starting with `--` are special meta tags and ( author, year, cover,
  words, length) are all required. They can be empty, but they must be provided.
- Title (`title`) tag must not be empty. Filenames get generated from this value
  so make sure this tag is populated.
- Cover images are baked into the OGG file. Cover image MUST be a JPEG.

## Included books

- [Armageddon 2419 A.D., Philip Francis Nowlan, 1929](./books/armageddon-2419)
- [Flatland, Edwin A. Abbott, 1884](./books/flatland)
- [The Airlords of Han, Philip Francis Nowlan, 1929](./books/the-airlords-of-han)
- [The Strange Case of Dr. Jekyll and Mr. Hyde, Robert Louis Stevenson, 1886](./books/the-strange-case-of-dr-jekyll-and-mr-hyde)
- [The Time Machine, H. G. Wells, 1895](./books/the-time-machine)

## Libraries used

- https://github.com/psf/requests
- https://github.com/quodlibet/mutagen
- https://github.com/un33k/python-slugify

## License

[abtts](https://github.com/mitjafelicijan/abtts) was written by [Mitja
Felicijan](https://mitjafelicijan.com) and is released under the BSD two-clause
license, see the LICENSE file for more information.
