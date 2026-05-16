# Ultra Fast Authorized Media Downloader

This repository provides a GitHub Actions workflow for downloading media that you own, are authorized to download, or that is publicly licensed.

> Do not use this tool for DRM-protected content, paywalled media, login bypass, or unauthorized downloads.

## How to run

1. Open the GitHub Actions tab.
2. Select the `Ultra Fast Authorized Media Downloader` workflow.
3. Click `Run workflow`.
4. Enter the media `url`.
5. Choose a `mode`.
6. Set `playlist` and `subtitles` if needed.
7. Optionally provide `extra_ytdlp_args`.
8. Start the job and wait for completion.
9. Download the `media-output` artifact from the workflow run.

## Workflow inputs

- `url`: The media URL to download.
- `mode`: One of `best-mp4`, `1080p-mp4`, `720p-mp4`, `audio-mp3`, `audio-m4a`.
- `playlist`: `true` to download playlists, `false` to download only the provided item.
- `subtitles`: `true` to download subtitles and convert them to SRT.
- `extra_ytdlp_args`: Optional additional yt-dlp arguments. Unsafe arguments are blocked.

## Cookie usage

If you need cookies for authorized sources, add a GitHub secret:

- Name: `YTDLP_COOKIES_TXT`
- Value: Raw cookies.txt content

The workflow creates `cookies.txt` with `chmod 600` and passes it safely to yt-dlp. Secrets are not printed.

## Artifact output

The workflow packages downloaded files into `artifact/media-output.zip` and uploads it as the `media-output` artifact.
After the job completes, download that artifact from the Actions run.

## Common modes

- `best-mp4`: Best available mp4 video plus m4a audio merged to mp4.
- `1080p-mp4`: Up to 1080p mp4.
- `720p-mp4`: Up to 720p mp4.
- `audio-mp3`: Extract audio to mp3.
- `audio-m4a`: Extract audio to m4a.

## Important notes

- This tool is only for authorized downloads.
- Very large files may hit GitHub Actions runtime limits or artifact size limits.
- The downloaded zip artifact is retained for 3 days.
