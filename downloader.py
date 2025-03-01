import argparse
import os
import sys
import subprocess
import platform
import logging
from colorama import init, Fore, Style
from tqdm import tqdm
import tkinter as tk
from tkinter import filedialog

# Initialize colorama for colored terminal output
init()

# Set up logging
logging.basicConfig(filename="download_log.txt", level=logging.ERROR, 
                    format="%(asctime)s - %(message)s")

def check_dependencies():
    """Check if yt-dlp is installed, install if not"""
    try:
        subprocess.run(["yt-dlp", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print(f"{Fore.YELLOW}yt-dlp not found. Installing it now...{Style.RESET_ALL}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=True)
            print(f"{Fore.GREEN}yt-dlp installed successfully!{Style.RESET_ALL}")
            return True
        except subprocess.SubprocessError as e:
            print(f"{Fore.RED}Failed to install yt-dlp: {e}{Style.RESET_ALL}")
            logging.error(f"Failed to install yt-dlp: {e}")
            print(f"{Fore.YELLOW}Please install it manually with: pip install yt-dlp{Style.RESET_ALL}")
            return False

def get_video_info(url):
    """Get video title and available formats"""
    try:
        result = subprocess.run(
            ["yt-dlp", "--skip-download", "--print", "title", url],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        title = result.stdout.strip()
        print(f"{Fore.GREEN}Title: {title}{Style.RESET_ALL}")
        return title
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error retrieving info: {e}{Style.RESET_ALL}")
        logging.error(f"Error retrieving info for {url}: {e}")
        return None

def interactive_mode():
    """Run in interactive mode, prompting user for all options"""
    print(f"{Fore.CYAN}=== Interactive Media Downloader ==={Style.RESET_ALL}")
    
    url = input(f"{Fore.YELLOW}Enter URL: {Style.RESET_ALL}")
    if not url.strip():
        print(f"{Fore.RED}No URL provided. Exiting.{Style.RESET_ALL}")
        return False
    
    title = get_video_info(url)
    if not title:
        return False

    # Playlist option
    playlist_choice = input(f"{Fore.YELLOW}Download playlist (if applicable)? (y/n): {Style.RESET_ALL}")
    download_playlist = playlist_choice.lower() == 'y'

    # Format preference
    print(f"{Fore.CYAN}\nSelect format:{Style.RESET_ALL}")
    print(f"1. {Fore.GREEN}Video (MP4){Style.RESET_ALL}")
    print(f"2. {Fore.GREEN}Audio (MP3){Style.RESET_ALL}")
    format_choice = input(f"{Fore.YELLOW}Enter choice (1-2): {Style.RESET_ALL}")
    output_format = "mp4" if format_choice == "1" else "mp3" if format_choice == "2" else "mp4"

    # Quality preference
    print(f"{Fore.CYAN}\nSelect quality:{Style.RESET_ALL}")
    print(f"1. {Fore.GREEN}High{Style.RESET_ALL}")
    print(f"2. {Fore.GREEN}Medium{Style.RESET_ALL}")
    print(f"3. {Fore.GREEN}Low{Style.RESET_ALL}")
    quality_choice = input(f"{Fore.YELLOW}Enter choice (1-3): {Style.RESET_ALL}")
    quality = "high" if quality_choice == "1" else "medium" if quality_choice == "2" else "low"

    # Subtitles
    subtitle_choice = input(f"{Fore.YELLOW}Download subtitles (if available)? (y/n): {Style.RESET_ALL}")
    subtitles = subtitle_choice.lower() == 'y'

    # Trimming
    trim_section = None
    trim_choice = input(f"{Fore.YELLOW}Trim media? (y/n): {Style.RESET_ALL}")
    if trim_choice.lower() == 'y':
        start = input(f"{Fore.YELLOW}Start time (e.g., 00:10): {Style.RESET_ALL}")
        end = input(f"{Fore.YELLOW}End time (e.g., 01:30): {Style.RESET_ALL}")
        trim_section = f"*{start}-{end}"

    # Output directory
    default_path = os.getcwd()
    print(f"{Fore.CYAN}\nSpecify download location:{Style.RESET_ALL}")
    print(f"Default: {default_path}")
    custom_path = input(f"{Fore.YELLOW}Custom path (or Enter for default): {Style.RESET_ALL}")
    output_path = custom_path if custom_path.strip() else default_path

    # Custom filename
    custom_name = input(f"{Fore.YELLOW}Custom filename (or Enter for default '%(title)s.%(ext)s'): {Style.RESET_ALL}")
    filename = custom_name if custom_name.strip() else "%(title)s.%(ext)s"

    print(f"{Fore.CYAN}\nStarting download...{Style.RESET_ALL}")
    return download_video(url, output_format, quality, output_path, download_playlist, subtitles, trim_section, filename)

def download_video(url, output_format="mp4", quality="high", output_path=None, 
                  download_playlist=False, subtitles=False, trim_section=None, filename="%(title)s.%(ext)s"):
    """Download media using yt-dlp"""
    if not output_path:
        output_path = os.getcwd()
    os.makedirs(output_path, exist_ok=True)

    cmd = ["yt-dlp"]
    if not download_playlist:
        cmd.append("--no-playlist")
    else:
        filename = "%(playlist_index)s - " + filename  # Add numbering for playlists

    if output_format.lower() == "mp4":
        if quality.lower() == "high":
            cmd.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"])
        elif quality.lower() == "medium":
            cmd.extend(["-f", "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best"])
        else:
            cmd.extend(["-f", "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best"])
    elif output_format.lower() == "mp3":
        cmd.extend(["-x", "--audio-format", "mp3", 
                    "--audio-quality", "0" if quality.lower() == "high" else "5" if quality.lower() == "medium" else "7"])
    else:
        print(f"{Fore.RED}Invalid format.{Style.RESET_ALL}")
        return False

    if subtitles:
        cmd.extend(["--write-subs", "--sub-langs", "en"])
    if trim_section:
        cmd.extend(["--download-sections", trim_section])

    cmd.extend(["-o", os.path.join(output_path, filename)])
    cmd.append(url)

    # Progress bar
    print(f"{Fore.YELLOW}Format: {output_format.upper()}, Quality: {quality.capitalize()}{Style.RESET_ALL}")
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        with tqdm(total=100, desc="Downloading", unit="%") as pbar:
            for line in process.stdout:
                if "[download]" in line and "%" in line:
                    percent = float(line.split("%")[0].split()[-1])
                    pbar.n = percent
                    pbar.refresh()
        success = process.wait() == 0
        if success:
            print(f"{Fore.GREEN}Download complete! File saved to {output_path}{Style.RESET_ALL}")
            # Open folder based on OS
            if platform.system() == "Windows":
                os.startfile(output_path)
            elif platform.system() == "Darwin":
                subprocess.run(["open", output_path])
            elif platform.system() == "Linux":
                subprocess.run(["xdg-open", output_path])
        return success
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error during download: {e}{Style.RESET_ALL}")
        logging.error(f"Download failed for {url}: {e}")
        return False

def gui_mode():
    """Run in GUI mode using tkinter, centered on the screen"""
    root = tk.Tk()
    root.title("Media Downloader")

    # Set window size
    window_width = 400
    window_height = 300

    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate position to center the window
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # Set geometry with centered position
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # GUI elements
    tk.Label(root, text="URL").pack()
    url_entry = tk.Entry(root, width=50)
    url_entry.pack()

    tk.Label(root, text="Output Folder").pack()
    folder_var = tk.StringVar(value=os.getcwd())
    tk.Entry(root, textvariable=folder_var).pack()
    tk.Button(root, text="Browse", command=lambda: folder_var.set(filedialog.askdirectory())).pack()

    format_var = tk.StringVar(value="mp4")
    tk.Radiobutton(root, text="Video (MP4)", variable=format_var, value="mp4").pack()
    tk.Radiobutton(root, text="Audio (MP3)", variable=format_var, value="mp3").pack()

    quality_var = tk.StringVar(value="high")
    tk.Radiobutton(root, text="High", variable=quality_var, value="high").pack()
    tk.Radiobutton(root, text="Medium", variable=quality_var, value="medium").pack()
    tk.Radiobutton(root, text="Low", variable=quality_var, value="low").pack()

    def start_download():
        download_video(url_entry.get(), format_var.get(), quality_var.get(), folder_var.get())

    tk.Button(root, text="Download", command=start_download).pack()
    root.mainloop()

def main():
    parser = argparse.ArgumentParser(description="Media Downloader (using yt-dlp)")
    parser.add_argument("url", nargs="?", help="Media URL")
    parser.add_argument("-f", "--format", choices=["mp3", "mp4"], default="mp4")
    parser.add_argument("-q", "--quality", choices=["high", "medium", "low"], default="high")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument("-i", "--interactive", action="store_true")
    parser.add_argument("--gui", action="store_true", help="Run in GUI mode")
    parser.add_argument("--batch-file", help="Path to a text file with URLs")
    parser.add_argument("--playlist", action="store_true", help="Download playlist")
    parser.add_argument("--subtitles", action="store_true", help="Download subtitles")
    
    args = parser.parse_args()

    print(f"{Fore.BLUE}=" * 60)
    print("MEDIA DOWNLOADER (Powered by yt-dlp)".center(60))
    print("=" * 60 + Style.RESET_ALL)

    if not check_dependencies():
        return

    if args.gui:
        gui_mode()
        return

    if args.batch_file:
        with open(args.batch_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        for url in urls:
            title = get_video_info(url)
            if title:
                success = download_video(url, args.format, args.quality, args.output, args.playlist, args.subtitles)
    elif args.interactive:
        success = interactive_mode()
    else:
        if not args.url:
            print(f"{Fore.RED}Error: URL required in non-interactive mode.{Style.RESET_ALL}")
            parser.print_help()
            return
        title = get_video_info(args.url)
        if title:
            success = download_video(args.url, args.format, args.quality, args.output, args.playlist, args.subtitles)

    if success:
        print(f"{Fore.GREEN}Download complete!{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Download failed.{Style.RESET_ALL}")

    another = input(f"{Fore.YELLOW}Download another? (y/n): {Style.RESET_ALL}")
    if another.lower() == 'y':
        success = interactive_mode() if args.interactive or not args.url else download_video(args.url, args.format, args.quality, args.output, args.playlist, args.subtitles)
        print(f"{Fore.GREEN if success else Fore.RED}Download {'complete' if success else 'failed'}!{Style.RESET_ALL}")

    print(f"{Fore.BLUE}=" * 60 + Style.RESET_ALL)

if __name__ == "__main__":
    main()