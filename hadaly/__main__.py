#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os, sys

def main(args=None):
    from .app import HadalyApp
    import locale
    import gettext

    current_locale, encoding = locale.getdefaultlocale()
    abspath = os.path.abspath(os.path.dirname(sys.argv[0]))
    langpath = abspath + '/data/locales/'
    language = gettext.translation('hadaly', langpath,
                                   [current_locale])
    language.install()
    HadalyApp().run()


if __name__ == '__main__':
    main()
