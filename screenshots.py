"""Generate gifs for before and after previews or the Robotoweb fonts.

Browserstack has been used and a list of operating systems based on their
different text rendering engines have been chosen.
"""
import sys
from PIL import Image
import browserstack_screenshots
import requests
import os
from glob import glob
from ntpath import basename
import time
import json

ROBOTO_OLD_SITE = "http://robototester.appspot.com/old.html"
ROBOTO_NEW_SITE = "http://robototester.appspot.com/new.html"

CONFIG = 'config.json'


def _build_filename_from_browserstack_json(j):
    """Build useful filename for an image from the screenshot json metadata"""
    filename = ''
    device = j['device'] if j['device'] else 'Desktop'
    if j['state'] == 'done' and j['image_url']:
        detail = [device, j['os'], j['os_version'],
                  j['browser'], j['browser_version'], '.jpg']
        filename = '_'.join(item.replace(" ", "_") for item in detail if item)
    else:
        print 'screenshot timed out, ignoring this result'
    return filename


def _download_file(uri, filename):
    try:
        with open(filename, 'wb') as handle:
            request = requests.get(uri, stream=True)
            for block in request.iter_content(1024):
                if not block:
                    break
                handle.write(block)
    except IOError, e:
        print e


def _read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (EOFError, IOError), e:
        print e
        return {}

def _mkdir(path):
    if not os.direxists(path):
        os.mkdir(path)


def get_browserstack_imgs(auth, website, out_dir):
    _mkdir(out_dir)

    config = _read_json(CONFIG)
    config['url'] = website

    bstack = browserstack_screenshots.Screenshots(auth=auth, config=config)
    generate_resp_json = bstack.generate_screenshots()
    job_id = generate_resp_json['job_id']
    print "http://www.browserstack.com/screenshots/{0}".format(job_id)
    screenshots_json = bstack.get_screenshots(job_id)
    print 'Generating images, be patient'
    while screenshots_json == False: # keep refreshing until browerstack is done
        time.sleep(3)
        screenshots_json = bstack.get_screenshots(job_id)
    for screenshot in screenshots_json['screenshots']:
        filename = _build_filename_from_browserstack_json(screenshot)
        base_image = os.path.join(out_dir, filename)
        if filename:
            _download_file(screenshot['image_url'], base_image)


def before_and_after_gifs(new_img_dir, old_img_dir):
    gif_path = os.path.join(os.getcwd(), 'gifs')
    _mkdir(gif_path)

    old_imgs = {basename(n): n for n in glob('%s/*.jpg' % old_img_dir)}
    new_imgs = {basename(n): n for n in glob('%s/*.jpg' % new_img_dir)}

    shared_platforms = set(old_imgs) & set(new_imgs)

    for platform in shared_platforms:
        gif_filename = platform[:-4] + '.gif'
        before_img = Image.open(old_imgs[platform])
        after_img = Image.open(new_imgs[platform])

        before_img.save(
            os.path.join(gif_path, gif_filename),
            save_all=True,
            append_images=[after_img],
            loop=10000,
            duration=1000
        )
        print 'Generating %s' % gif_filename


def main(auth):
    old_imgs_dir = 'screenshots_roboto_v2.000'
    new_imgs_dir = 'screenshots_roboto_v2.137'

    print 'Getting old version samples'
    get_browserstack_imgs(auth, ROBOTO_OLD_SITE, old_imgs_dir)

    print 'Getting new version samples'
    get_browserstack_imgs(auth, ROBOTO_NEW_SITE, new_imgs_dir)

    print 'Generating gifs'
    before_and_after_gifs(old_imgs_dir, new_imgs_dir)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        main((sys.argv[1], sys.argv[2]))
    else:
        print 'ERROR: please provide BrowserStack username and auth key' + \
        '\n$ python screenshots.py <username> <key>'
