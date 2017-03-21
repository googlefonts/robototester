import unittest
import hashlib
import os
from glob import glob
import ntpath
import requests


class TestFonts(unittest.TestCase):

    def setUp(self):
        """Create two dictionaries, one for our hosted font family, stored
        at ./www/roboto_web_v2.136 and the other for the family we pr'd
        to google/fonts.

        Each font name will be the key, whilst the value will be the sha256
        checksum value.

        ---
        {"Roboto-Regular.ttf": "checksum value",
        "Roboto-Bold.ttf": "checksum value"}
        ...
        """

        # Dictionary for hosted fonts
        hosted_fonts = glob('./www/roboto_web_v2.136/*.ttf')

        self.hosted_fonts_sha256 = {}
        for font in hosted_fonts:
            font_name = ntpath.basename(font)
            h = hashlib.sha256(open(font, 'rb').read()).digest()
            self.hosted_fonts_sha256[font_name] = h

        # Download url for family prd to github
        git_fam_dl_url = "https://raw.githubusercontent.com/" + \
        "m4rc1e/fonts/roboto/apache/roboto/"

        # Dictionary for pr'd git fonts
        self.git_fonts_sha256 = {}
        for font_name in self.hosted_fonts_sha256:
            dl_font_url = os.path.join(git_fam_dl_url, font_name)
            r = requests.get(dl_font_url)
            h = hashlib.sha256(r.content).digest()
            self.git_fonts_sha256[font_name] = h


    def test_hosted_fonts_match_git_pr_checksum(self):
        """Check hosted fonts match google/fonts pr checksum"""
        for font in self.hosted_fonts_sha256:
            self.assertEqual(
                self.hosted_fonts_sha256[font],
                self.git_fonts_sha256[font]
            )


if __name__ == '__main__':
    unittest.main()
