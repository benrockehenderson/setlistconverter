import os
import secrets

import spotipy.oauth2
from flask import Flask, redirect, render_template, request, session

import setlistfm
from setlistfm import get_setlist_songs, extract_setlist_id
from spotify import create_spotify_playlist, search_spotify_songs, spotify_auth_url_builder, get_access_token

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        setlist_id_or_url = (
            request.form.get('setlist_id') or ''
        ).strip()
        
        if not setlist_id_or_url:
            return render_template(
                'success_or_error.html',
                main_message='Missing setlist URL',
                should_show_error=True,
                error_description='Please enter a setlist.fm URL or ID.'
            ), 400

        setlist_id = extract_setlist_id(setlist_id_or_url)
        state = secrets.token_urlsafe(32)
        spotify_auth_url = spotify_auth_url_builder(state)
        session['oauth_state'] = state
        session['setlist_id'] = setlist_id
        return redirect(spotify_auth_url)
    
    else:  # request.method == 'GET':
        if any(key in request.args for key in ('code', 'state', 'error')):
            state = request.args.get('state', '')
            expected_state = session.get('oauth_state', '')
            if not expected_state or not secrets.compare_digest(
                state.encode(), expected_state.encode()
            ) or not session.get('setlist_id') or not (
                request.args.get('code') or request.args.get('error')
            ):
                return render_template(
                    'success_or_error.html',
                    main_message='Invalid Spotify authorization callback',
                    should_show_error=True,
                    error_description='Please start the conversion again.'
                ), 400

            session.pop('oauth_state')
            setlist_id = session.pop('setlist_id')

        if error := request.args.get("error"):
            return render_template(
                'success_or_error.html',
                main_message='Spotify authorization failed',
                should_show_error=True,
                error_description=(
                    f"Spotify returned '{error}'. "
                    "Check your app's settings in the Spotify Developer Dashboard."
                )
            )

        if code := request.args.get("code"):
            try:
                token = get_access_token(code)
            except spotipy.oauth2.SpotifyOauthError as e:
                return render_template(
                    'success_or_error.html',
                    main_message='Failed to create the playlist',
                    should_show_error=True,
                    error_description=(
                        f"Couldn't authenticate with Spotify: {e.error_description}."
                        "Try refreshing the page."
                    )
                ), 502

            try:
                artist, songs = get_setlist_songs(setlist_id.strip())
            except setlistfm.SetlistFMQueryException:
                return render_template(
                    'success_or_error.html',
                    main_message=f"Couldn't retrieve Setlist.fm songs.",
                    should_show_error=True,
                    error_description=f"You might have entered an incorrect setlist.fm URL or setlist ID."
                ), 502

            try:
                tracks, unmatched_songs = search_spotify_songs(artist, songs, token)
            except Exception as e:
                return render_template(
                    'success_or_error.html',
                    main_message=f"Couldn't search for songs.",
                    should_show_error=True,
                    error_description=str(e)
                ), 500

            # noinspection PyBroadException
            try:
                create_spotify_playlist(tracks, f'Setlist {artist}', token)
            except Exception as e:
                return render_template(
                    'success_or_error.html',
                    main_message=f"Couldn't create the playlist.",
                    should_show_error=True,
                    error_description=str(e)
                ), 500

            return render_template(
                'success_or_error.html',
                main_message=f'Successfully added {len(tracks)} songs to your playlist!',
                should_show_error=len(unmatched_songs) != 0,
                error_description=f"Couldn't add the songs {', '.join(unmatched_songs)}."
            )
        else:
            return render_template('index.html')


if __name__ == "__main__":
    app.run("0.0.0.0", port=5001)
