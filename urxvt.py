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
import logging


SIZE = os.environ.get('URXVT_SIZE', 14)
FIXED_SIZE = os.environ.get('URXVT_FIXED_SIZE', 16)
ICON = os.environ.get('URXVT_ICON', 'tilda.png')
ICON_PATH = os.environ.get('URXVT_ICON_PATH',
                           os.path.expanduser('~/.urxvt/icons'))
DEFAULT_FONT = os.environ.get('URXVT_TTF', 'DejaVuSansMono Nerd Font Mono')
DEFAULT_BITMAP = os.environ.get('URXVT_BMP', 'Misc Fixed')
PERLEXT = os.environ.get('URXVT_PERL_EXT',
                         "url-select,keyboard-select,font-size,color-themes")
LOG = None


class Logger:
    """
    Simple logger class with output on console only
    """
    def __init__(self, logger_name):
        """
        Initialize named logger
        """
        self._log = logging.getLogger(logger_name)
        self.setup_logger()
        self._log.set_verbose = self.set_verbose

    def __call__(self):
        """
        Calling this object will return configured logging.Logger object with
        additional set_verbose() method.
        """
        return self._log

    def set_verbose(self, verbose_level):
        """
        Change verbosity level. Default level is warning.
        """
        ver_map = {0: logging.CRITICAL,
                   1: logging.ERROR,
                   2: logging.WARNING,
                   3: logging.INFO,
                   4: logging.DEBUG}
        self._log.setLevel(ver_map.get(verbose_level, ver_map[4]))

    def setup_logger(self):
        """
        Create setup instance and make output meaningful :)
        """
        if self._log.handlers:
            # need only one handler
            return

        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.set_name("console")
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        self._log.addHandler(console_handler)
        self._log.setLevel(logging.WARNING)


LOG = Logger(__name__)()

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
            LOG.debug('No suitable styles found for font in line: %s', line)
            continue

        for name in font_names:
            if style.lower() == 'bold' and not bold.get(name):
                bold[name] = style
            elif style.lower() != 'bold' and not regular.get(name):
                regular[name] = style
            else:
                LOG.debug('Font %s probably already exists in dict', name)

    return {'regular': regular, 'bold': bold}


_AVAILABLE_FONTS = _get_all_suitable_fonts()


def _get_style(name, bold=False):
    key = 'bold' if bold else 'regular'
    try:
        return _AVAILABLE_FONTS[key][name]
    except KeyError:
        LOG.warning('There is no matching font for name "%s" for style %s.',
                    name, key)
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
    parser.add_argument('-f', '--default-font', default=DEFAULT_FONT,
                        help='use particular (comma separated) font face(s) '
                        'as default(s) one, should be provided by font name, '
                        'not file name(s), default is "%s"' % DEFAULT_FONT)
    parser.add_argument('-b', '--bitmap', action='store_true', help='use '
                        'bitmap font in addition to scalable defined above')
    parser.add_argument('-i', '--icon', default=ICON, help='select icon from '
                        '%s, default "%s"' % (ICON_PATH, ICON))
    parser.add_argument('-t', '--tabbedalt', action='store_true',
                        help='activate tabbedalt extension')
    parser.add_argument('-n', '--no-perl', action='store_true',
                        help='no perl extensions')
    parser.add_argument('-s', '--size', default=SIZE, type=int,
                        help='set scalable forn size, default %s' % SIZE)
    parser.add_argument('-e', '--execute', default=None,
                        help='pass exec to urxvt')
    parser.add_argument("-v", "--verbose", help='be verbose. Adding more "v" '
                        'will increase verbosity', action="count", default=0)

    args = parser.parse_args()

    LOG.set_verbose(args.verbose)

    command = ['urxvt']
    command.extend(['-icon', os.path.join(os.path.expanduser(ICON_PATH),
                                          args.icon)])

    if not args.no_perl:
        command.append('-pe')
        if args.tabbedalt:
            command.append('tabbedalt,' + PERLEXT)
        else:
            command.append(PERLEXT)

    size = args.size
    font_faces = _ADDITIONAL_FONTS[:]
    if ',' in args.default_font:
        f_f = [f.strip() for f in args.default_font.split(',')]
        f_f.extend(font_faces)
        font_faces = f_f
    else:
        font_faces.insert(0, args.default_font)

    if args.bitmap:
        font_faces.insert(0, DEFAULT_BITMAP)

    # __import__('ipdb').set_trace()
    fn = ['-fn', _get_font_list(font_faces, size)]
    print(fn)
    fb = ['-fb', _get_font_list(font_faces, size, True)]
    print(fn)
    print(fb)
    command.extend(fn)
    command.extend(fb)

    LOG.info('%s', command)
    subprocess.run(command)


if __name__ == '__main__':
    main()
