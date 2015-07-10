#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os, sys

def main(args=None):
    from .app import HadalyApp
    from kivy.utils import platform
    from kivy.logger import Logger
    import locale
    import gettext

    if platform() == 'android':
        try:
            from jnius import autoclass
        except ImportError:
            Logger.debug('Application: Unable to import jnius.')

        current_locale = autoclass(str('java.util.Locale')).getDefault().toString()
        Logger.debug('hadaly {locale}'.format(locale=current_locale))
        language = gettext.translation('hadaly', 'hadaly/data/locales/',[current_locale], fallback=True)

    else:
        current_locale, encoding = locale.getdefaultlocale()
        abspath = os.path.abspath(os.path.dirname(sys.argv[0]))
        langpath = abspath + '/data/locales/'
        language = gettext.translation('hadaly', langpath,
                                       [current_locale])

    language.install()
    HadalyApp().run()


if __name__ == '__main__':
    main()
