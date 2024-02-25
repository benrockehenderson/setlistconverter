import concurrent
import os
from typing import Optional

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from concurrent import futures

from track import Track, create_track_from_api_response


class SpotifyAPIException(Exception):
    """
    The exception that's raised when Spotify API query results in an error.
    """


def create_spotify_playlist(tracks: list[Track], playlist_name: str):
    sp = spotipy.Spotify(auth_manager=spotify_auth_manager())

    user_id = sp.me()['id']

    playlist = sp.user_playlist_create(user_id, playlist_name, public=False)

    track_uris = [track.uri for track in tracks]

    sp.playlist_add_items(playlist['id'], track_uris)


def spotify_auth_manager(state: Optional[str] = None):
    """
    Creates and returns a Spotify auth manager for handling OAuth.
    """
    return SpotifyOAuth(
        client_id=os.environ['SPOTIFY_CLIENT_ID'],
        client_secret=os.environ['SPOTIFY_CLIENT_SECRET'],
        redirect_uri=os.environ['REDIRECT_URI'],
        state=state,
        scope="playlist-modify-private"
    )


def spotify_auth_url_builder(setlist_id: Optional[str] = None) -> str:
    """
    Builds the Spotify authorization URL using SpotifyOAuth.
    """
    auth_manager = spotify_auth_manager(setlist_id)
    auth_url = auth_manager.get_authorize_url()
    return auth_url


def get_access_token(code: str) -> str:
    """
    Use the SpotifyOAuth object to get an access token.
    """
    auth_manager = spotify_auth_manager()
    token_info = auth_manager.get_access_token(code, as_dict=False, check_cache=False)
    return token_info


def search_spotify_song_wrapper(args):
    return get_spotify_song(*args)


def search_spotify_songs(artist: str, songs: list[str], token: str) -> tuple[list[Track], list[str]]:
    tracks = []
    unmatched_songs = []
    song_to_future = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for song in songs:
            args = (f'track:"{song}" artist:{artist}', artist, token)
            future = executor.submit(search_spotify_song_wrapper, args)
            song_to_future[song] = future

        for song, future in song_to_future.items():
            track = future.result()
            if track is not None:
                tracks.append(track)
            else:
                total_searches = 0
                while total_searches < 60:
                    re_search = get_spotify_song(song, artist, access_token=token, limit=20, offset=total_searches + 10)
                    total_searches += 20
                    if re_search is not None:
                        tracks.append(re_search)
                        break
                else:
                    unmatched_songs.append(song)
    return tracks, unmatched_songs


def get_spotify_song(query: str, artist_name: str, access_token: str, offset: int = 0, limit: int = 10) -> Optional[
    Track
]:
    """
    Searches for a song on Spotify and returns a Track object if the artist name matches.
    :param query: Name of the song to search for.
    :param artist_name: The exact name of the artist to match.
    :param access_token: Spotify API access token.
    :param offset: The Spotify search offset.
    :param limit: The Spotify search limit.
    :return: The first matching Track object if an artist name matches; otherwise, None.
    """
    spotify = spotipy.Spotify(auth=access_token)
    results = spotify.search(q=query, type='track', market='CA', limit=limit, offset=offset)

    for track in results['tracks']['items']:
        for artist in track['artists']:
            if artist['name'].lower() == artist_name.lower():
                return create_track_from_api_response(track)
    return None
