<h1 align="center">fzseries-api</h1>

<p align="center">
<a href="#"><img alt="Python version" src="https://img.shields.io/pypi/pyversions/fzseries-api"/></a>
<a href="https://github.com/Simatwa/fzseries-api/actions/workflows/python-test.yml"><img src="https://github.com/Simatwa/fzseries-api/actions/workflows/python-test.yml/badge.svg" alt="Python Test"/></a>
<a href="LICENSE"><img alt="License" src="https://img.shields.io/static/v1?logo=GPL&color=Blue&message=GPLv3&label=License"/></a>
<a href="https://pypi.org/project/fzseries-api"><img alt="PyPi" src="https://img.shields.io/pypi/v/fzseries-api"></a>
<a href="https://github.com/Simatwa/fzseries-api/releases"><img src="https://img.shields.io/github/v/release/Simatwa/fzseries-api?label=Release&logo=github" alt="Latest release"></img></a>
<a href="https://github.com/Simatwa/fzseries-api/releases"><img src="https://img.shields.io/github/release-date/Simatwa/fzseries-api?label=Release date&logo=github" alt="release date"></img></a>
<a href="https://github.com/psf/black"><img alt="Black" src="https://img.shields.io/badge/code%20style-black-000000.svg"/></a>
<a href="https://github.com/Simatwa/fzseries-api/actions/workflows/python-publish.yml"><img src="https://github.com/Simatwa/fzseries-api/actions/workflows/python-publish.yml/badge.svg" alt="Python-publish"/></a>
<a href="https://pepy.tech/project/fzseries-api"><img src="https://static.pepy.tech/personalized-badge/fzseries-api?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Downloads" alt="Downloads"></a>
<a href="https://github.com/Simatwa/fzseries-api/releases/latest"><img src="https://img.shields.io/github/downloads/Simatwa/fzseries-api/total?label=Asset%20Downloads&color=success" alt="Downloads"></img></a>
<a href="https://hits.seeyoufarm.com"><img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com/Simatwa/fzseries-api"/></a>
</p>

> Unofficial Python SDK/API for fztvseries.live

```python
from fzseries_api import Auto

Auto(
    query="Mr. Robot",
).run()

# Will show download progressbar
"""
[T 1/10] Mr. Robot - S01E01 - eps1.0_hellofriend.mov
179 MB ████████████████████                     47%|
"""
```

## Installation

```sh
$ pip install fzseries-api[cli]
```

Alternatively, you can download standalone executable for your system from [here](https://github.com/Simatwa/fzseries-api/releases/latest).

## Usage 

```sh
$ fzseries download <QUERY>
# e.g fzseries download "Mr. Robot"
```

<h2>
<code>$ fzseries download --help</code>
</h2>

```
Usage: fzseries download [OPTIONS] QUERY

  Download a whole series|seasons|episodes automatically

Options:
  -b, --by [series|episodes]      Query category
  -so, --season-offset INTEGER    Season number to start downloading from
  -eo, --episode-offset INTEGER   Episode number to start downloading from
  -l, --limit INTEGER             Number of proceeding episodes to download
                                  before stopping
  -t, --download-trials INTEGER   Number of trials before giving up on
                                  downloading an episode
  -r, --request-timeout INTEGER   Http request timeout while downloading
                                  episodes in seconds.
  -f, --format [High MP4|WEBM]    Preffered movie download format
  -d, --directory DIRECTORY       Parent directory for saving the downloaded
                                  contents
  --enable-progressbar / --disable-progressbar
                                  Show or hide downloading progress bar
  --quiet                         Do not stdout any interactive messages
  --include_metadata              Add series title and episode-id in filename
  --one-season-only               Download only one season and stop.
  --ignore-errors                 Ignore exceptions raised while downloading
                                  episode
  --confirm                       Confirm episodes before downloading them
  --help                          Show this message and exit.
```

<details>
<summary>
<code>$ fzseries --help</code>
</summary>


```
Usage: fzseries [OPTIONS] COMMAND [ARGS]...

  Unofficial Python SDK/API for fztvseries.live

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  discover  Search TV series using title or filter
  download  Download a whole series|seasons|episodes automatically
  metadata  Access particular series metadata - seasons and episodes

  Repository : https://github.com/Simatwa/fzseries-api
```
</details>

> [!NOTE]
> **fzseries_api** provides a lot more than what you've just gone through here. Documenting isn't my thing, but I will try to update it as time goes by. Additionally, I cannot document this any better than the code itself; therefore, consider going through it.

## Disclaimer

This project is not affiliated with or endorsed by fztvseries.live or its owners. The API may change without notice, and this project does not guarantee compatibility with all future updates. The developers of this project are not responsible for any damages or losses resulting from the use of this API. This project is provided AS IS, without warranty of any kind, express or implied.