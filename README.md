# Create audiobooks from text files

- This program is written in Python and is using
  [UnrealSpeech](https://unrealspeech.com/) under the hood for TTS.
- Check out an [audio sample of a paragraph](./samples/paragraph.mp3) to see the
  quality of audio.

## What does it do?

- Converts text files into MP3 audiobook.
- Bakes ID3 tags and cover image to MP3 file.
- Has a really awesome reading voice provided by
  [UnrealSpeech](https://unrealspeech.com/).

## Installation

**Program uses [virtual
environments](https://docs.python.org/3/library/venv.html) so make sure that you
have Python, Pip and virtual environments installed properly.**

```sh
git clone git@github.com:mitjafelicijan/abtts.git
cd abtts

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## How to use it

- First you need to create [UnrealSpeech](https://unrealspeech.com/) account.
- Create an API Token and store. You will need it for this.
- Generate first book that is provided with this repository. Use the API token
  in `US_BEARER` variable like in example below.

```sh
US_BEARER="CW5RhoOX..." python3 abtts.py --book-folder=books/armageddon-2419/
```

- This will generate MP3 file in `out` directory (provided you didn't mess with
  `OUT_DIR` variable).
- A JSON report file with the same slug name as MP3 file will also be generated
  for you so you can see if all went well.

> This example book was taken from [Standard
> Ebooks](https://standardebooks.org/ebooks/philip-francis-nowlan/armageddon-2419-a-d). They
> have an amazing assortment of books. You should definitely check them out. All
> of their material is available on [GitHub](https://github.com/standardebooks)
> as well.

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
- Each book should have it's own directory to itself. Do not mix and match
  multiple books together.
- Books should be split into chapters, but also only one chapter is sufficient.

And example of TOC file.

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
- Lines starting with `--` are special meta tags and (title, author, year,
  cover, words, length) are all required. They can be empty, but they must be
  provided.
- Cover images are baked into the MP3 file. Cover image MUST be a JPEG.

## Included books

- [Armageddon 2419 A.D., Philip Francis Nowlan, 1929](./books/armageddon-2419)
- [Flatland, Edwin A. Abbott, 1884](./books/flatland)
- [The Airlords of Han, Philip Francis Nowlan, 1929](./books/the-airlords-of-han)
- [The Strange Case of Dr. Jekyll and Mr. Hyde, Robert Louis Stevenson, 1886](./books/the-strange-case-of-dr-jekyll-and-mr-hyde)
- [The Time Machine, H. G. Wells, 1895](./books/the-time-machine)

## Libraries used

- https://github.com/psf/requests
- https://github.com/jiaaro/pydub
- https://github.com/quodlibet/mutagen
- https://github.com/un33k/python-slugify

## License

[abtts](https://github.com/mitjafelicijan/abtts) was written by [Mitja
Felicijan](https://mitjafelicijan.com) and is released under the BSD two-clause
license, see the LICENSE file for more information.
