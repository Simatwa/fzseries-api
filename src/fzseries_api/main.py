"""
This module does the simple work
of linking the `handler` module (html)
with `hunter` (models) while providing
a higher level API.

It achieves this through 4 classes
- `Search` : Movie look-up
- `Navigate` : Progress to the targeted movie
- `DownloadLinks` : Links to the downloadable movie file
- `Download` : Download the movie file
- `Auto` : Ultimately download items of index 0.
"""