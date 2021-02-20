=============
urxvt-wrapper
=============

Simplify invoking urxvt terminal from commandline.

Motivation for creating this little script was to have ability to simply run
urxvt with predefined features (like icons/font size/perl script list etc),
without providing a ton of parameters nor keeping track of resources in
``~/.Xdefaults`` file.


Installation
------------

Simply put the script preferably in your ``$PATH``.

There are a few dependencies:

* Python
* ``fc-list`` from fontconfig package
* ``urxvt`` obviously (package is often called *rxvt-unicode*) built with XFT
  support.
* using ``--tabbedalt`` switch requires `tabbedalt`_ plugin.

Also, there are three fonts internally used:

* `Symbola`_ - Font with rich set of emoji glyphs
* `Unifont`_ - Bitmap font with rich set of unicode glyphs
* `DejaVu Sans`_ - which provides several more unicode glyphs

All these fonts will be concatenated with the main font(s). If you don't have
any of them, that's ok, they simply be filtered out. Although, I would
recommend to install them to be able to display unusual glyphs/emoji.


Configuration
-------------

There are several environment variables available to be put in ``~/.bashrc`` or
such, which will have an impact on the defaults wrapper have. So here is the
list of variables, with their default values:

* ``URXVT_BMP``: ``[empty]`` - Font to be used as bitmap font (like `font-misc-misc`_
  from xorg, or `terminus`_) before all the font defined in ``URXVT_TTF``. You
  need to provide valid xft name for the font, so it is basically a convenient
  way for having bitmap font available to use with ``--bitmap`` switch, for
  details see below.
* ``URXVT_ICON_PATH``: ``~/.urxvt/icons`` - Path for icons images.
* ``URXVT_ICON``: ``[empty]`` - Icon to be used with the terminal.
* ``URXVT_PERL_EXT``: ``url-select,keyboard-select,font-size,color-themes`` -
  Comma separated list of perl extensions for the urxvt.
* ``URXVT_RUN_DIRECT``: ``false`` - Urxvt can be run using simply ``urxvt``
  executable or with daemon (``urxvtd``) and client (``urxvtc``). By default
  the latter will be chosen for launching new terminal. Note, that you don't
  need to manually run ``urxvtd`` - it will be run automatically on absence.
* ``URXVT_SIZE``: 14 - font size. It's applied to all fonts.
* ``URXVT_TTF``: ``[empty]`` - Font or comma separated font list to be used. Note,
  that first font become main font, and the others will be used for glyphs that
  are missing from the previous one. That makes the order of the selected fonts
  crucial. See below for examples.

Usage
-----

Simplest case is just to run it without any parameter (assuming script is
somewhere in ``$PATH``:

.. code:: shell-session

   $ urxvt.py

To run urxvt with *Hack Nerd Font* and *Webdings* xft fonts:

.. code:: shell-session

   $ urxvt.py -f 'Hack Nerd Font Mono,Webdings'

If you wondering how to look for the particular font name, you can use
``fc-list`` command. Let's try to look for the *Hack Nerd* font:

.. code:: shell-session

   $ fc-list|grep -i hack
   /home/gryf/.fonts/Nerd Fonts/Hack Italic Nerd Font Complete Mono.ttf: Hack Nerd Font Mono:style=Italic
   /home/gryf/.fonts/Nerd Fonts/Hack Bold Italic Nerd Font Complete Mono.ttf: Hack Nerd Font Mono:style=Bold Italic
   /home/gryf/.fonts/Nerd Fonts/Hack Regular Nerd Font Complete Mono.ttf: Hack Nerd Font Mono:style=Regular
   /home/gryf/.fonts/Nerd Fonts/Hack Bold Nerd Font Complete Mono.ttf: Hack Nerd Font Mono:style=Bold

there are four files found. Every line can be divided using colon as a
separator. First part of the line is the complete path to the
font, then there is a comma separated list of names of the font and finally
comma separated style list after ``style=`` keyword. For this example, name of
the font is common for all four files, and the difference is in style only, and
the name is **Hack Nerd Font Mono**.

To use bitmap font (which still be used through the xft library, and defined as
such), assuming that ``URXVT_BMP`` env variable contain name of the font (for
example **Misc Fixed**) , it is simple enough to:

.. code:: shell-session

   $ urxvt.py -b

Note, that this is exactly the same as:

.. code:: shell-session

   $ urxvt.py -f 'Misc Fixed'

For more options, issue:

.. code:: shell-session

   $ urxvt.py -h

to see complete list of supported parameters.

Finally, you can pass all valid urxvt options to the executable. Just use
``--`` delimiter and than use any valid params:

.. code:: shell-session

   $ urxvt.py -f 'Hack Nerd Font Mono' -n -s 16 -- -cr orange

which set the regular and bold font face to *Hack Nerd* font with its size set
to 16, without any perl extension and cursor color set to orange.


License
-------

This work is licensed under GPL3. See LICENSE file for details.


.. _terminus: http://terminus-font.sourceforge.net/
.. _font-misc-misc: https://gitlab.freedesktop.org/xorg/font/font-misc-misc
.. _tabbedalt: https://github.com/gryf/tabbedalt
.. _Symbola: http://luc.devroye.org/fonts-47197.html
.. _Unifont: http://unifoundry.com/
.. _DejaVu Sans: https://dejavu-fonts.github.io/
