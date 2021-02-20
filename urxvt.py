#!/usr/bin/env python
"""
Wrapper for launching URXVT terminal emulator. It supports automatically
generated font list for normal and bold typefaces, setting up bitmap font as a
main one, selecting an icon and so on.

Consult options below.
"""

import argparse
import os
import subprocess
import sys
import logging


RUN_DIRECT = os.environ.get('URXVT_RUN_DIRECT', False)
SIZE = os.environ.get('URXVT_SIZE', 14)
ICON = os.environ.get('URXVT_ICON', '')
ICON_PATH = os.environ.get('URXVT_ICON_PATH',
                           os.path.expanduser('~/.urxvt/icons'))
DEFAULT_FONT = os.environ.get('URXVT_TTF', '')
DEFAULT_BITMAP = os.environ.get('URXVT_BMP', '')
PERLEXT = os.environ.get('URXVT_PERL_EXT',
                         "url-select,keyboard-select,font-size,color-themes")
# Arbitrary added fonts, that provides symbols, icons, emoji (besides those
# in default font)
ADDITIONAL_FONTS = ['Symbola', 'Unifont Upper', 'DejaVu Sans']

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


class Font:
    """
    Represents font object, which can produce valid XFT strings for provided
    fonts as it's attributes - bold and regular.

    xft:font name:style=somestyle:pixelsize=12
    """

    XFT_TEMPLATE = 'xft:%s:style=%s:pixelsize=%d'

    # TODO: do we need italic/bolditalic?
    _REGULAR = ['regular', 'normal', 'book', 'medium']
    _BOLD = ['bold']
    _AVAILABLE_FONTS = {}

    def __init__(self, name, size):
        self.size = size
        self.name = name
        self._regular = None
        self._bold = None

        self._get_all_suitable_fonts()

    @property
    def bold(self):
        """
        Return full string font to use for xft definition for urxvt, i.e.
        xft:font name:style=Bold:pixelsize=20

        It may happen, that a font doesn't provide bold face. Function will
        than return empty string.
        """
        if self._bold is not None:
            return self._bold

        style = Font._AVAILABLE_FONTS['bold'].get(self.name)
        if not style:
            LOG.warning(f'Bold style not found for {self.name}')
            self._bold = ''
        else:
            self._bold = Font.XFT_TEMPLATE % (self.name, style, self.size)

        return self._bold

    @property
    def regular(self):
        """
        Return full string font to use for xft definition for urxvt, i.e.
        xft:font name:style=Regular:pixelsize=20

        Font style depends on the particular font, and can be one of case
        insensitive: regular, normal, book, medium.

        Technically, medium style should be semi-bold or bold, but there is at
        least one font face which treats medium style as regular one. It is
        placed as a last resort, and choice for particular font face is left
        to the user.
        """
        if self._regular is not None:
            return self._regular

        style = Font._AVAILABLE_FONTS['regular'].get(self.name)
        if not style:
            LOG.warning(f'Regular style not found for {self.name}')
            self._regular = ''
        else:
            self._regular = Font.XFT_TEMPLATE % (self.name, style, self.size)

        return self._regular

    def _get_all_suitable_fonts(self):
        """
        Scan all available in the system fonts, where every line have format:

        font_filename: font_name1[,font_name2,…]:style=style1[,style2,…]

        Font can have several names and several styles. Styles can be either
        single defined style or comma separated list of aliases or
        internationalized names for style, i.e.:

            filename1: font_name1:style=style
            filename2: font_name2,font_name3:style=style1,style2
            filename3: font_name4:style=style3,style4

        Information about fonts will be stored as a class variable
        _AVAILABLE_FONTS within two dictionaries: bold and regular, stored in
        corresponding keys in mentioned dict. _AVAILABLE_FONTS will have a
        format:

            {'bold': {'font name': 'Bold',
                      'font name3': 'bold'},
             'regular': {'font_name1': 'Regular',
                         'font_name2': 'Medium',
                         'font_name3': 'Normal'}}

        As for regular/normal/book/medium styles, whatever style is available
        for given font, it will be chosen, as ordered in _REGULAR list
        whichever matches first.

        Note, that fc-list and all the parsing is done once, per running this
        script, regardless of font faces passed by -f option or those defined
        in ADDITIONAL_FONTS.
        """
        if Font._AVAILABLE_FONTS:
            return

        regular = {}
        bold = {}

        out = subprocess.check_output(['fc-list']).decode('utf-8')
        out = sorted(out.split('\n'))  # let's have it in order

        for line in out:
            if not line:
                continue

            if ': ' not in line:
                continue

            if ':style=' not in line:
                continue

            line = line.split(': ')[1]
            font_names = [n.strip() for n in line.split(':')[0].split(',')]
            styles = [s.strip() for s in line.split(':style=')[1].split(',')]

            style = self._parse_style(styles)
            if not style:
                LOG.debug('No suitable styles found for font in line: %s',
                          line)
                continue

            for name in font_names:
                if style.lower() == 'bold' and not bold.get(name):
                    LOG.info('Adding bold font for name: %s', name)
                    bold[name] = style
                elif style.lower() != 'bold' and not regular.get(name):
                    LOG.info('Adding regular font for name: %s', name)
                    regular[name] = style
                else:
                    LOG.debug('Font %s probably already exists in dict', name)

        Font._AVAILABLE_FONTS = {'regular': regular, 'bold': bold}

    def _parse_style(self, styles):
        for reg_style in Font._REGULAR:
            if reg_style in ''.join(styles).lower():
                for style in styles:
                    if style.lower() == reg_style:
                        return style

        if 'bold' in ''.join(styles).lower():
            for style in styles:
                if style.lower() == 'bold':
                    return style


class Urxvt:
    """
    Runner for the URXVT
    """

    def __init__(self, args):
        self.size = args.size
        self.icon = args.icon
        self.fonts = None
        self.perl_extensions = None

        self._bitmap = args.bitmap
        self._icon_path = ICON_PATH
        self._exec = args.execute
        self._rxvt_args = None

        self._setup(args)
        self._validate()

    def run(self):
        """Run terminal emulator"""
        args = self._make_command_args()
        LOG.info('Arguments to be passed: %s', ' '.join(args))
        if RUN_DIRECT:
            self._run_urxvt(args)
        else:
            self._run_client_server(args)

    def _run_client_server(self, args):
        """Utilize urxvt client/daemon mode"""
        command = ['urxvtc']
        command.extend(args)
        process = subprocess.run(command)

        if process.returncode == 2:
            subprocess.run(['urxvtd', '-q', '-o', '-f'])
            subprocess.run(command)

    def _run_urxvt(self, args):
        """Simply pass args to urxvt executable."""
        command = ['urxvt']
        command.extend(args)
        # LOG.info('%s', command)
        subprocess.run(command)

    def _setup(self, args):
        # it could be a list or a single font, it will be combined with
        # additional fonts
        self.fonts = self._parse_fonts(args.default_font)

        if args.no_perl:
            self.perl_extensions = ''
        else:
            self.perl_extensions = PERLEXT
            if args.tabbedalt:
                self.perl_extensions = 'tabbedalt,' + PERLEXT

        if args.rxvt_args:
            self._rxvt_args = args.rxvt_args

    def _validate(self):
        # validate fonts
        for font in self.fonts:
            if not any((font.regular, font.bold)):
                LOG.error('Font %s seems to be unusable or nonexistent.',
                          font.name)

    def _make_command_args(self):
        args = []

        args.extend(['-pe', self.perl_extensions])
        regular = ','.join([f.regular for f in self.fonts if f.regular])
        if regular:
            args.extend(['-fn', regular])
        bold = ','.join([f.bold for f in self.fonts if f.bold])
        if bold:
            args.extend(['-fb', bold])
        if self.icon and os.path.exists(os.path.join(ICON_PATH, self.icon)):
            args.extend(['-icon', os.path.join(ICON_PATH, self.icon)])

        if self._exec:
            args.extend(['-e', self._exec])

        if self._rxvt_args:
            args.extend(self._rxvt_args)

        return args

    def _parse_fonts(self, font_string):
        """
        Parse potentially provided font list, add additional fonts to it,
        adjust for possible bitmap font and return a list of Font objects.
        """
        # get the copy of additional fonts
        font_faces = ADDITIONAL_FONTS[:]

        # find out main font/fonts passed by commandline/env/default
        if ',' in font_string:
            f_f = [f.strip() for f in font_string.split(',')]
            f_f.extend(font_faces)
            font_faces = f_f
        else:
            font_faces.insert(0, font_string)

        if self._bitmap:
            font_faces.insert(0, DEFAULT_BITMAP)

        # return list of Font objects
        return [Font(f, self.size) for f in font_faces]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-f', '--default-font', default=DEFAULT_FONT,
                        help='use particular (comma separated) font face(s) '
                        'as default(s) one, should be provided by font name, '
                        'not file name(s), default is "%s"' % DEFAULT_FONT)
    parser.add_argument('-b', '--bitmap', action='store_true', help='use '
                        'bitmap font prior to scalable defined above')
    parser.add_argument('-i', '--icon', default=ICON, help='select icon from '
                        '%s."' % ICON_PATH)
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
    parser.add_argument("rxvt_args", nargs='*')

    args = parser.parse_args()

    LOG.set_verbose(args.verbose)

    urxvt = Urxvt(args)
    urxvt.run()


if __name__ == '__main__':
    main()
