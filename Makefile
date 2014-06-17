.PHONY: po mo

po:
	xgettext -LPython -o data/locales/po/hadaly.pot --from-code=UTF-8 hadaly/*.kv hadaly/*.py	
	msgmerge --update --no-fuzzy-matching --backup=off data/locales/po/fr.po data/locales/po/hadaly.pot

mo:
	mkdir -p data/locales/fr/LC_MESSAGES
	msgfmt data/locales/po/fr.po -o data/locales/fr/LC_MESSAGES/hadaly.mo
