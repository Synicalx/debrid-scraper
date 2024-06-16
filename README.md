# debrid-scraper
For scraping out files from your *own* RD web directory

## Usage

Run it as-is, and pass in *your* RD directory and desired title as an argument. Currently supports media files but can be extended to anything.

```
python main.py https://my.real-debrid.com/<rd ID>/torrents/ "My home movies"
```

Select the content you want to download, and it will be saved in the same directory as the script.

## Notes

- The crawling part is multi-threaded, but the downloading part is not.
- You can adjust the number of threads by changing `max_workers`. If you don't know what that is, don't change it.
- The script will match content if half or more words in the file/directory name match the title you provided.
- You can adjust that threshold by tweaking the aptly named `threshold` variable.
- Some of this is written by ChatGPT, notably the GUI bit which I had zero interest in learning how to do.
