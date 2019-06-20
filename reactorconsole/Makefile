SHELL := /bin/bash 
VENVDIR := $(shell mktemp -ud)
PKGDIR := $(shell mktemp -ud)
GITREV := $(shell git rev-parse --verify --short HEAD)
PACKAGENAME := reactorconsole-$(GITREV).tar.gz
prefix := /opt/affecto/reactorconsole


.PHONY: clean all
all: package

dist/reactorconsole: reactorconsole.py reactorconsole.spec requirements.txt
	virtualenv --system-site-packages -p `which python3` $(VENVDIR)
	source $(VENVDIR)/bin/activate ; pip install --upgrade pip ; pip install -r requirements_dev.txt
	source $(VENVDIR)/bin/activate ; pyinstaller --clean --onefile reactorconsole.spec
	rm -rf $(VENVDIR)

install: dist/reactorconsole
	mkdir -p $(prefix)
	cp reactorconsole_config.json.example dist/reactorconsole  $(prefix)
	echo "$(GITREV)" >$(prefix)/version.txt

package: dist/reactorconsole reactorconsole_config.json.example
	mkdir $(PKGDIR)
	cp reactorconsole_config.json.example dist/reactorconsole $(PKGDIR)/
	pushd $(PKGDIR) ; tar -cvzf /tmp/$(PACKAGENAME) ./ ; popd ; mv /tmp/$(PACKAGENAME) ./
	rm -rf $(PKGDIR)

clean:
	rm -rf build/ dist/

