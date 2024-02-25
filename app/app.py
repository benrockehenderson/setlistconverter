import spotipy.oauth2
from flask import Flask, redirect, render_template, request

import setlistfm
from setlistfm import get_setlist_songs, extract_setlist_id
from spotify import create_spotify_playlist, search_spotify_songs, spotify_auth_url_builder, get_access_token

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        setlist_id_or_url = request.form.get('setlist_id')
        setlist_id = extract_setlist_id(setlist_id_or_url)
        spotify_auth_url = spotify_auth_url_builder(setlist_id)
        return redirect(spotify_auth_url)
    else:  # request.method == 'GET':
        if (code := request.args.get("code")) and (setlist_id := request.args.get("state")):
            try:
                token = get_access_token(code)
            except spotipy.oauth2.SpotifyOauthError as e:
                return render_template(
                    'success_or_error.html',
                    main_message=f'Failed to create the playlist',
                    should_show_error=True,
                    error_description=(
                        f"Couldn't authenticatce with Spotify: {e.error_description}."
                        "Try refreshing the page."
                    )
                )

            try:
                artist, songs = get_setlist_songs(setlist_id.strip())
            except setlistfm.SetlistFMQueryException:
                return render_template(
                    'success_or_error.html',
                    main_message=f"Couldn't retrieve Setlist.fm songs.",
                    should_show_error=True,
                    error_description=f"You might have entered an incorrect setlist.fm URL or setlist ID."
                )

            tracks, unmatched_songs = search_spotify_songs(artist, songs, token)

            # noinspection PyBroadException
            try:
                create_spotify_playlist(tracks, f'Setlist {artist}')
            except Exception as e:
                return render_template(
                    'success_or_error.html',
                    main_message=f"Couldn't create the playlist.",
                    should_show_error=True,
                    error_description=str(e)
                )

            return render_template(
                'success_or_error.html',
                main_message=f'Successfully added {len(songs)} songs to your playlist!',
                should_show_error=len(unmatched_songs) != 0,
                error_description=f"Couldn't add the songs {', '.join(unmatched_songs)}."
            )
        else:
            return render_template('index.html')


if __name__ == "__main__":
    app.run("0.0.0.0")
