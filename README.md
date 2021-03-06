
[![Build Status](https://travis-ci.org/melehin/photocollage.svg?branch=master)](https://travis-ci.org/melehin/photocollage)
# Instagram and Flickr.com photo collage maker (public photos only)
## Install
```sh
git clone https://github.com/melehin/photocollage.git
cd photocollage
pip install -r requirements.txt
```

## Usage
```sh
python photocollage.py [-h] --count COUNT [--procs PROCS] --cell_size CELL_SIZE --ratio RATIO [--login LOGIN] [--out OUT]
```
LOGIN = @login for switch from Flickr to Instagram mode

## Example
### Recent photos from Flickr
```sh
python photocollage.py --count=50 --cell_size=100 --ratio=10x5 --procs=2
```
### by Instagram.com nickname to save to file result-insta.jpg
```sh
python photocollage.py --count=50 --cell_size=100 --login=@instagram --ratio=10x5 --procs=2 --out=result-insta.jpg
```
![Instagram result](examples/result-insta.jpg)
### by Flickr.com nickname to save to file result-image.jpg
```sh
python photocollage.py --count=50 --cell_size=100 --login=tekfx --ratio=10x5 --procs=2 --out=result-image.jpg
```
![Flickr result](examples/result-image.jpg)
