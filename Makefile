.PHONY: po mo

po:
	xgettext -LPython -o hadaly/data/locales/po/hadaly.pot --from-code=UTF-8 hadaly/*.kv hadaly/*.py
	msgmerge --update --no-fuzzy-matching --backup=off hadaly/data/locales/po/fr.po hadaly/data/locales/po/hadaly.pot

mo:
	mkdir -p hadaly/data/locales/fr/LC_MESSAGES
	msgfmt hadaly/data/locales/po/fr.po -o hadaly/data/locales/fr/LC_MESSAGES/hadaly.mo
