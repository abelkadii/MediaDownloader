# Media Downloader

Asynchronous Python tool for extracting HLS playlists, selecting a target stream quality, downloading media segments concurrently, and assembling them into a final video file.

## Overview

Media Downloader is a technical project built to explore browser automation and asynchronous media download workflows.

The pipeline is simple:

1. Open a media page in a headless browser
2. Intercept the HLS playlist URL (`.m3u8`)
3. Parse available stream resolutions
4. Select the desired quality
5. Download media segments concurrently
6. Merge the segments into a final output file

This project focuses on:
- asynchronous programming
- browser-driven URL extraction
- HTTP playlist parsing
- concurrent downloads
- modular Python design

## Features

- Headless browser extraction of HLS playlist URLs
- Resolution discovery from master playlists
- Async segment downloading with `aiohttp`
- Bounded concurrency using semaphores
- Automatic assembly of downloaded segments into a single media file
- Modular code structure separating extraction, download, and utility logic

## Tech Stack

- Python
- asyncio
- aiohttp
- Pyppeteer
- tqdm

## Project Structure

```text
.
├── main.py         # Main orchestration flow
├── downloads.py    # Playlist parsing, segment download, and file assembly
├── fmoviez.py      # Browser automation and playlist interception
├── intercept.py    # Response interception experiments
├── utils.py        # Helper functions for naming and resolution handling
├── log.py          # Logging utilities
├── config.json     # Local configuration
└── downloads/      # Output directory
