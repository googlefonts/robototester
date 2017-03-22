"""Generate a gifs for before and after previews or the Robotoweb fonts.

Browserstack has been used and a list of operating systems based on their
different text rendering engines have been chosen.
"""
from PIL import Image
import os
from glob import glob
from ntpath import basename

ROBOTO_OLD_SITE = "http://robototester.appspot.com/old.html"
ROBOTO_NEW_SITE = "http://robototester.appspot.com/new.html"


def main():

    # TODO: Get images via Browserstack's screenshot api (This is for paid
    # plans only)

    # Create gifs
    gif_path = os.path.join(os.getcwd(), 'gifs')
    roboto_old = {basename(n): n for n in glob('./screenshots_roboto_v2.000/*.png')}
    roboto_new = {basename(n): n for n in glob('./screenshots_roboto_v2.136/*.png')}

    shared_platforms = set(roboto_old) & set(roboto_new)

    for platform in shared_platforms:
        gif_filename = platform[:-4] + '.gif'
        before_img = Image.open(roboto_old[platform])
        after_img = Image.open(roboto_new[platform])

        before_img.save(
            os.path.join(gif_path, gif_filename),
            save_all=True,
            append_images=[after_img],
            loop=10000,
            duration=1000
        )
        print 'Generating %s' % gif_filename

if __name__ == '__main__':
    main()
