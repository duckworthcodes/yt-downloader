# Media Downloader

A versatile Python-based media downloader that supports both command-line and GUI interfaces for downloading videos and audio from various online sources.

## Features

- Multiple interface options:
  - Command-line interface
  - Interactive terminal mode
  - GUI mode
- Support for various media formats:
  - Video downloads (MP4)
  - Audio extraction (MP3)
- Quality options:
  - High
  - Medium
  - Low
- Additional features:
  - Subtitle downloading
  - Media trimming
  - Playlist support
  - Progress tracking
  - Cross-platform compatibility

## Prerequisites

- Python 3.x
- Required Python packages:
  - yt-dlp
  - colorama
  - tqdm
  - tkinter (usually comes with Python)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install required packages:
```bash
pip install yt-dlp colorama tqdm
```

## Usage

### Command Line Interface

Basic usage:
```bash
python hi.py [URL]
```

Options:
```bash
python hi.py [URL] [options]

Options:
  -f, --format {mp3,mp4}    Output format (default: mp4)
  -q, --quality {high,medium,low}  Quality setting (default: high)
  -o, --output OUTPUT       Output directory
  -i, --interactive        Run in interactive mode
  --gui                    Run in GUI mode
  --batch-file BATCH_FILE  Path to a text file with URLs
  --playlist              Download playlist
  --subtitles             Download subtitles
```

### Interactive Mode

Run the script in interactive mode:
```bash
python hi.py -i
```

### GUI Mode

Launch the graphical interface:
```bash
python hi.py --gui
```

## Examples

1. Download a video in MP4 format:
```bash
python hi.py https://example.com/video -f mp4
```

2. Download audio in MP3 format with high quality:
```bash
python hi.py https://example.com/video -f mp3 -q high
```

3. Download with subtitles:
```bash
python hi.py https://example.com/video --subtitles
```

4. Download a playlist:
```bash
python hi.py https://example.com/playlist --playlist
```

## Error Handling

- The application includes comprehensive error handling
- Failed downloads are logged in `download_log.txt`
- Automatic dependency checking and installation

## Contributing

Feel free to submit issues and enhancement requests!

## License

[Add your license information here]

## Acknowledgments

- Built with yt-dlp
- Uses colorama for terminal colors
- Progress bars powered by tqdm
