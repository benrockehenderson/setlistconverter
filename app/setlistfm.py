import os
from urllib.parse import urlparse

from requests import get


class SetlistFMQueryException(Exception):
    """
    The exception that's raised when SetlistFM API query results in an error.
    """


def extract_setlist_id(input_link_or_id: str) -> str:
    if '://' in input_link_or_id:
        path = urlparse(input_link_or_id).path
        extracted_id = path.split('-')[-1].replace('.html', '')
    else:
        extracted_id = input_link_or_id

    return extracted_id


def get_setlist_songs(setlist_id: str) -> tuple[str, list[str]]:
    """
    Return the list of each song from a SetlistFM setlist by querying the setlistfm API.
    Reads the SETLIST_FM_API_KEY variable from .env.
    :param setlist_id: The setlist id from SetlistFM to query.
    :return: Tuple of the name of each song as a list and the artist.
    """
    response = get(
        f"https://api.setlist.fm/rest/1.0/setlist/" + setlist_id,
        headers={
            "x-api-key": os.environ["SETLIST_FM_API_KEY"],
            "Accept": "application/json"
        }
    )

    if response.status_code != 200:
        raise SetlistFMQueryException("Cannot reach setlist.fm")

    setlists = response.json()
    all_songs = []

    for set_info in setlists["sets"]["set"]:
        # if "song" in set_info:
        all_songs.extend([song["name"] for song in set_info["song"]])

    artist = setlists['artist']['name']

    return artist, all_songs
