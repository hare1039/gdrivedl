# gdrivedl
A simple downloader to download PUBLIC google drive folder

# usage
```
usage: dl.py [-h] [-d [D]] [-s [S]] [url [url ...]]

positional arguments:
  url

optional arguments:
  -h, --help  show this help message and exit
  -d [D]      download directory, default: ${PWD}
  -s [S]      selenium driver host, default: http://127.0.0.1:4444/wd/hub
  ```
  
# Example
```
python3 dl.py -d ${PWD} \
              -s http://127.0.0.1:4444/wd/hub \
              https://drive.google.com/drive/folders/exampleexampleexample?usp=sharing
```

Sorry that I can only use selenium to simulate user clicks. Just can't find ANY google api for a PUBLIC google drive folder.
BTW, This is a tool of my animation auto updater. I'll writing a blog post about it after all tools are set and functioning.
