from dataclasses import dataclass
from typing import Any, List


@dataclass
class ExternalURLs:
    spotify: str


@dataclass
class Image:
    height: int
    url: str
    width: int


@dataclass
class Artist:
    external_urls: ExternalURLs
    href: str
    id: str
    name: str
    type: str
    uri: str


@dataclass
class Album:
    album_type: str
    artists: List[Artist]
    external_urls: ExternalURLs
    href: str
    id: str
    images: List[Image]
    is_playable: bool
    name: str
    release_date: str
    release_date_precision: str
    total_tracks: int
    type: str
    uri: str


@dataclass
class ExternalIDs:
    isrc: str


@dataclass
class Track:
    album: Album
    artists: List[Artist]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: ExternalIDs
    external_urls: ExternalURLs
    href: str
    id: str
    is_local: bool
    is_playable: bool
    name: str
    popularity: int
    preview_url: str
    track_number: int
    type: str
    uri: str


def create_track_from_api_response(track_data: Any) -> Track:
    album_external_urls = ExternalURLs(spotify=track_data['album']['external_urls']['spotify'])
    track_external_urls = ExternalURLs(spotify=track_data['external_urls']['spotify'])

    images = [Image(height=img['height'], url=img['url'], width=img['width']) for img in track_data['album']['images']]

    artists = [Artist(external_urls=ExternalURLs(spotify=artist['external_urls']['spotify']),
                      href=artist['href'],
                      id=artist['id'],
                      name=artist['name'],
                      type=artist['type'],
                      # uri=artist['uri']) for artist in track_data['album']['artists']]
                      uri=artist['uri']) for artist in track_data['artists']]

    album = Album(album_type=track_data['album']['album_type'],
                  artists=artists,
                  external_urls=album_external_urls,
                  href=track_data['album']['href'],
                  id=track_data['album']['id'],
                  images=images,
                  is_playable=track_data['album']['is_playable'],
                  name=track_data['album']['name'],
                  release_date=track_data['album']['release_date'],
                  release_date_precision=track_data['album']['release_date_precision'],
                  total_tracks=track_data['album']['total_tracks'],
                  type=track_data['album']['type'],
                  uri=track_data['album']['uri'])

    external_ids = ExternalIDs(isrc=track_data['external_ids']['isrc'])

    return Track(album=album,
                 artists=artists,
                 disc_number=track_data['disc_number'],
                 duration_ms=track_data['duration_ms'],
                 explicit=track_data['explicit'],
                 external_ids=external_ids,
                 external_urls=track_external_urls,
                 href=track_data['href'],
                 id=track_data['id'],
                 is_local=track_data['is_local'],
                 is_playable=track_data['is_playable'],
                 name=track_data['name'],
                 popularity=track_data['popularity'],
                 preview_url=track_data['preview_url'],
                 track_number=track_data['track_number'],
                 type=track_data['type'],
                 uri=track_data['uri']
                 )
