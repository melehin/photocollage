# Flickr.com photo collage maker
## Install
```sh
git clone https://github.com/melehin/photocollage.git
cd photocollage
pip install -r requirements.txt
```

## Usage
```sh
python photocollage.py --count=50 --cell_size=100 --login=userlogin --ratio=10x5 --procs=2 --out=result-image.jpg
```

## Example
### Recent photos
```sh
python photocollage.py --count=50 --cell_size=100 --ratio=10x5 --procs=2
```
### by Flickr.com login to save to file result-image.jpg
```sh
python photocollage.py --count=50 --cell_size=100 --login=tekfx --ratio=10x5 --procs=2 --out=result-image.jpg
```
![Final result](examples/result-image.jpg)