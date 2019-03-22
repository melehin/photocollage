import os
import re
import cv2
import sys
import argparse
import logging
import requests
import numpy as np
from time import time
from multiprocessing import Pool as ThreadPool

from apis import api_factory
from apis.base import APIException

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

def service(data):
    url, w, h = data
    logging.debug("Download %s" % url)
    r = requests.get(url)
    if r.status_code == 200:
        img_orig = cv2.imdecode(np.fromstring(r.content, np.uint8), cv2.IMREAD_COLOR)
        src_h, src_w, colors = img_orig.shape
        if src_h > src_w:
            offset = int((src_h-src_w)/2)
            img = img_orig[offset:src_w+offset, 0:src_w]
        elif src_h < src_w:
            offset = int((src_w-src_h)/2)
            img = img_orig[0:src_h, offset:src_h+offset]
        else:
            img = img_orig
        
        img = cv2.resize(img, (w, h))
        return img

def printProgressBar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    if iteration == total: 
        print()

def getargs():
    parser = argparse.ArgumentParser(description='Фотоколлаж')
    parser.add_argument('--count', help='Число фотографий для обработки', type=int, required=True)
    parser.add_argument('--procs', help='Количество процессов', type=int, default=2)
    parser.add_argument('--cell_size', help='Размер ячейки в пикселях', type=int, required=True)
    parser.add_argument('--ratio', help='Соотношение сторон коллажа', required=True)
    parser.add_argument('--login', help='Логин пользователя со страницы которого будут загружаться фотографии')
    parser.add_argument('--out', help='Путь до файла с результатом (image.jpg), если не задан выводится в окне')
    args = parser.parse_args()
    
    m = re.search("^(\d+)x(\d+)$", args.ratio)
    if not m:
        logging.error("Format MxN expected (M - cols, N - rows)")
        sys.exit(1)
    
    args.cols = int(m.group(1))
    args.rows = int(m.group(2))

    if args.cols*args.rows < args.count:
        logging.error("cols*rows < count")
        sys.exit(2)
    
    return args

def main():
    args = getargs()
    
    w = h = args.cell_size
    start = time()

    printProgressBar(0, args.count)
    # Make pictures data generator (iterator)
    generator = api_factory.make(args.login, max_imgs=args.count, w=w, h=h)
    printProgressBar(1, args.count)
    
    # Make thread pool and run
    pool = ThreadPool(args.procs)
    results = pool.imap(service, generator)
    pool.close()
    
    # Generate blank white image
    img = np.zeros([args.rows*h, args.cols*w, 3],dtype=np.uint8)
    img.fill(255)

    # Draw images into cells
    i = 0
    j = 0
    drown = 0
    for result in results:
        if i >= args.cols:
            i = 0
            j += 1
        
        img[j*h:(j+1)*h, i*w:(i+1)*w] = result
        i += 1
        drown += 1
        printProgressBar(drown, args.count)
    
    logging.debug("Time: %.2fs" % (time() - start))
    
    # Write output
    if args.out:
        cv2.imwrite(args.out, img)
        logging.info("Saved to: %s", os.path.abspath(args.out))
    else:
        cv2.imshow('image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.RequestException as e:
        logging.error("Network error:\n %s" % e)
    except APIException as e:
        logging.error("API error: \n%s" % e)
    except Exception as e:
        logging.exception("Undefined error: \n%s" % e)