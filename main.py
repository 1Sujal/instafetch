import argparse
import sys
from scraper import InstagramParser

def main():
    parser = argparse.ArgumentParser(description="Download Instagram videos/reels easily via CLI.")
    parser.add_argument("url", help="The full URL of the Instagram post or reel.")
    parser.add_argument("-o", "--output", default="instagram_reel.mp4", help="Output filename (default: instagram_reel.mp4)")
    
    args = parser.parse_args()

    scraper = InstagramParser()
    try:
        video_url = scraper.get_video_url(args.url)
        if video_url:
            print(f"\nFound Direct Video URL:\n{video_url}\n")
            scraper.download_video(video_url, args.output)
        else:
            print("Error: Could not extract a valid video URL from this post.")
            sys.exit(1)
            
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()