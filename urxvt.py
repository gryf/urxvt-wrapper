#!/usr/bin/env python

import argparse
import collections
import os
import subprocess
import sys


SIZE = os.environ.get('URXVT_SIZE', 14)
FIXED_SIZE = os.environ.get('URXVT_FIXED_SIZE', 16)
ICON = os.environ.get('URXVT_ICON', 'tilda.png')
ICON_PATH = os.environ.get('URXVT_ICON_PATH',
                           os.path.expanduser('~/GNUstep/Library/Icons'))
DEFAULT_TTF = os.environ.get('URXVT_TTF', 'DejaVuSansMono Nerd Font Mono')
DEFAULT_BITMAP = os.environ.get('URXVT_BMP', 'Misc Fixed')

# Arbitrary added fonts, that provides symbols, icons, emoji (besides those in
# Nerd Font)
_ADDITIONAL_FONTS = ['Symbola', 'Unifont Upper', 'DejaVu Sans']
_REGULAR = ['regular', 'normal', 'book', 'medium', 'bold']
_XFT_TEMPLATE = 'xft:%s:style=%s:pixelsize=%d'


def _get_all_suitable_fonts():
    """
    Scan all available in the system fonts, where every line have format:

    font_filename: font_name1[,font_name2,…]:style=style1[,style2,…]

    Font can have several names and several styles. Styles can be either
    single defined style or comma separated list of aliases or
    internationalized names for style, i.e.:

        filename1: font_name1:style=style
        filename2: font_name2,font_name3:style=style1,style2
        filename3: font_name4:style=style3,style4

    Return a dictionary of styles associated to the font name, i.e.:

        {font_name1: [style],
         font_name2: [style1, style2],
         font_name3: [style1, style2],
         font_name4: [style3, style4]}

    """
    fonts = collections.defaultdict(list)
    out = subprocess.check_output(['fc-list']).decode('utf-8')
    for line in out.split('\n'):
        if line and ': ' in line and ':style=' in line:
            line = line.split(': ')[1]
            font_names = line.split(':')[0].split(',')
            styles = line.split(':style=')[1].split(',')
            for name in font_names:
                for style in styles:
                    if style.lower().strip() in _REGULAR:
                        fonts[name.strip()].append(style.strip())

    out = {}
    for key, val in fonts.items():
        out[key] = list(set(val))

    return out


_AVAILABLE_FONTS = _get_all_suitable_fonts()


def _get_style(name, bold=False):
    try:
        styles = _AVAILABLE_FONTS[name]
    except KeyError:
        print(f'There is no matching font for name "{name}".')
        sys.exit(1)

    for style in styles:
        if bold and style.lower() == 'bold':
            return style

        if style.lower() in _REGULAR:
            return style


def _get_font_list(ff_list, bold=False, bmp_first=False):
    fonts = []

    for face in ff_list:
        fonts.append(_XFT_TEMPLATE % (face, _get_style(face), SIZE))
    if bmp_first:
        fonts.insert(0, _XFT_TEMPLATE %
                     (DEFAULT_BITMAP, _get_style(DEFAULT_BITMAP), FIXED_SIZE))
    return ','.join(fonts)


def main():
    font_faces = _ADDITIONAL_FONTS[:]
    font_faces.insert(0, DEFAULT_TTF)
    regular = _get_font_list(font_faces)
    print(regular)
    subprocess.run(['urxvt', '-fn', regular])


if __name__ == '__main__':
    main()
