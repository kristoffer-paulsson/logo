PYI = --log=DEBUG --onefile

default: init
	pyinstaller bin/logo $(PYI)

init:
	pip install -r requirements.txt
	python setup.py develop

po:
	xgettext -Lpython --output=messages.pot lib/logo/kv/basescreen.kv lib/logo/kv/licence.kv lib/logo/kv/navdrawer.kv
	msgmerge --update --no-fuzzy-matching --backup=off assets/locales/po/ru.po messages.pot
	msgmerge --update --no-fuzzy-matching --backup=off assets/locales/po/en.po messages.pot

mo:
	mkdir -p assets/locales/ru/LC_MESSAGES
	mkdir -p assets/locales/en/LC_MESSAGES
	msgfmt -c -o assets/locales/ru/LC_MESSAGES/Logo.mo assets/locales/po/ru.po
	msgfmt -c -o assets/locales/en/LC_MESSAGES/Logo.mo assets/locales/po/en.po

docs: build
	sphinx-apidoc -o docs lib/logo
	sphinx-build -M html docs docs

test:
	py.test tests

clean:
	rm -fR ./dist
	rm -fR ./build

.PHONY: init mo po docs test clean
