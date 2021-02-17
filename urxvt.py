#!/usr/bin/env python
"""
Wrapper for launchin urxvt terminal emulator. It supports automatically
generated font list for normal and bold typefaces, setting up bitmap font as a
main one, selecting an icon and so on.

Consult options below.
"""

import argparse
import collections
import os
import subprocess
import sys


SIZE = os.environ.get('URXVT_SIZE', 14)
FIXED_SIZE = os.environ.get('URXVT_FIXED_SIZE', 16)
ICON = os.environ.get('URXVT_ICON', 'tilda.png')
ICON_PATH = os.environ.get('URXVT_ICON_PATH',
                           os.path.expanduser('~/.urxvt/icons'))
DEFAULT_FONT = os.environ.get('URXVT_TTF', 'DejaVuSansMono Nerd Font Mono')
DEFAULT_BITMAP = os.environ.get('URXVT_BMP', 'Misc Fixed')
PERLEXT = os.environ.get('URXVT_PERL_EXT',
                         "url-select,keyboard-select,font-size,color-themes")

# Arbitrary added fonts, that provides symbols, icons, emoji (besides those in
# Nerd Font)
_ADDITIONAL_FONTS = ['Symbola', 'Unifont Upper', 'DejaVu Sans']
_REGULAR = ['regular', 'normal', 'book', 'medium']
_XFT_TEMPLATE = 'xft:%s:style=%s:pixelsize=%d'


def _parse_style(styles):
    for reg_style in _REGULAR:
        if reg_style in ''.join(styles).lower():
            for style in styles:
                if style.lower() == reg_style:
                    return style

    if 'bold' in ''.join(styles).lower():
        for style in styles:
            if style.lower() == 'bold':
                return style


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

        {font_name1: (style),
         font_name2: (style1, style2),
         font_name3: (style1, style2),
         font_name4: (style3, style4)}

    """
    regular = {}
    bold = {}

    out = subprocess.check_output(['fc-list']).decode('utf-8')

    for line in out.split('\n'):
        if not line:
            continue

        if ': ' not in line:
            continue

        if ':style=' not in line:
            continue

        line = line.split(': ')[1]
        font_names = [n.strip() for n in line.split(':')[0].split(',')]
        styles = [s.strip() for s in line.split(':style=')[1].split(',')]

        style = _parse_style(styles)
        if not style:
            continue

        for name in font_names:
            if style.lower() == 'bold' and not bold.get(name):
                bold[name] = style
            elif style.lower() != 'bold' and not regular.get(name):
                regular[name] = style

    return {'regular': regular, 'bold': bold}


_AVAILABLE_FONTS = _get_all_suitable_fonts()


def _get_style(name, bold=False):
    key = 'bold' if bold else 'regular'
    try:
        return _AVAILABLE_FONTS[key][name]
    except KeyError:
        print(f'There is no matching font for name "{name}".')
        return None


def _get_font_list(ff_list, size, bold=False):
    fonts = []
    for face in ff_list:
        style = _get_style(face, bold)
        if not style:
            continue
        fonts.append(_XFT_TEMPLATE % (face, _get_style(face, bold), size))
    return ','.join(fonts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d', '--default-font', default=DEFAULT_FONT,
                        help='use particular (comma separated) font face(s) '
                        'as default(s) one, should be provided by font name, '
                        'not file name(s), default is "%s"' % DEFAULT_FONT)
    parser.add_argument('-b', '--bitmap', action='store_true', help='use '
                        'bitmap font in addition to scalable defined above')
    parser.add_argument('-i', '--icon', default=ICON, help='select icon from '
                        '%s, default "%s"' % (ICON_PATH, ICON))
    parser.add_argument('-t', '--tabbedalt', action='store_true',
                        help='activate tabbedalt extension')
    parser.add_argument('-s', '--size', default=SIZE, type=int,
                        help='set scalable forn size, default %s' % SIZE)

    parser.add_argument('-e', '--exec', help='pass exec to urxvt')
    parser.add_argument('-n', '--no-perl', action='store_true',
                        help='no perl extensions')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-q", "--quiet", help='please, be quiet. Adding more '
                       '"q" will decrease verbosity', action="count",
                       default=0)
    group.add_argument("-v", "--verbose", help='be verbose. Adding more "v" '
                       'will increase verbosity', action="count", default=0)

    args = parser.parse_args()

    font_faces = _ADDITIONAL_FONTS[:]
    font_faces.insert(0, DEFAULT_TTF)
    regular = _get_font_list(font_faces)
    print(regular)
    subprocess.run(['urxvt', '-fn', regular])


if __name__ == '__main__':
    main()
