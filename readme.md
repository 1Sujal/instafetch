Markdown
# Instagram Video Downloader CLI

A simple Python command-line utility to scrape and download high-quality videos and reels from Instagram using raw requests and parsing mechanisms.

## Installation

1. Clone the repository:
```bash
   git clone [https://github.com/1sujal/instafetch.git](https://github.com/1sujal/instafetch.git)
   cd instafetch
```
2. Install the dependencies:

```bash
pip install -r requirements.txt
```
      
3. Run the program from your terminal by passing the Instagram URL as an argument:

```bash
python main.py "https://www.instagram.com/p/DTN22HmiHjs/"
```
4. You can specify a custom output filename using the -o or --output flag:

```bash
python main.py "https://www.instagram.com/p/DTN22HmiHjs/" -o my_favorite_reel.mp4
```
