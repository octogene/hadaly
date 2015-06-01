#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.1a'


def main(args=None):
    from app import HadalyApp
    import locale
    import gettext

    current_locale, encoding = locale.getdefaultlocale()
    language = gettext.translation('hadaly', 'data/locales/',
                                   [current_locale], fallback=True)
    language.install()

    HadalyApp().run()


if __name__ == '__main__':
    main()
