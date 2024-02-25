# Setlist.fm to Spotify Playlist Converter

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Use now at [setlistconverter.com](https://setlistconverter.com)!

Want to be prepared for your next concert? Use this tool to convert any setlist from setlist.fm to a spotify playlist; automatically added to your library.

## Getting Started

### Prerequisites

- Docker
- Yarn

### Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/benrockehenderson/setlistconverter
   ```

2. Navigate to the project folder and generate the Tailwind CSS styles:
   ```sh
   yarn tailwindcss -o static/dist/css/output.css
   ```

3. Create a `.env` file based on `.env.example`:
   
   Copy the `.env.example` file to a new file named `.env` and fill in the values:
   ```
   SETLIST_FM_API_KEY=...
   SPOTIFY_CLIENT_ID=...
   SPOTIFY_CLIENT_SECRET=...
   REDIRECT_URI=...
   ```
   Make sure to set the `REDIRECT_URI` in your Spotify developer console to match the one specified in your `.env` file. Otherwise Spotify will not permit the redirect.

4. Build the Docker image:
   ```sh
   docker build -t setlistfm-spotify-converter .
   ```

5. Run the Docker container:
   ```sh
   docker run -p 5000:5000 --env-file .env setlistfm-spotify-converter
   ```

## Deployment

[setlistconverter.com](https://setlistconverter.com) is deployed on Google Cloud Run, however you may choose to deploy your container on any platform you wish. Make sure 

## Contributing

Feel free to create pull requests! I would love to make the converter more accurate over time - especially improved Spotify song searching algorithms.

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE).
