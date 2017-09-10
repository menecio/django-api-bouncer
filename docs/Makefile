# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS       =
SPHINXBUILD      = python -msphinx
SPHINXPROJ       = DjangoAPIBouncer
SOURCEDIR        = .
BUILDDIR         = _build
GH_PAGES_SOURCES = index.rst install.rst tutorial Makefile

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

gh-pages:
	git checkout gh-pages
	rm -rf $(BUILDDIR) _sources _static
	git checkout master $(GH_PAGES_SOURCES)
	git reset HEAD
	make html
	rm -rf $(GH_PAGES_SOURCES)
	mv -fv $(BUILDDIR)/html/.[!.]* ./
	rm -rf $(BUILDDIR)
	git add -A
	git commit -m "Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`" && git push origin gh-pages ; git checkout master
