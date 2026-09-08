# .copr/Makefile
#
# Invoked by Copr as: make -f .copr/Makefile srpm outdir="<outdir>" spec="<spec_path>"
# CWD is the already-checked-out git worktree (Copr's SCM clone) -- no re-clone needed.

NAME := wire-desktop
spec ?= .copr/$(NAME).spec
outdir ?= $(CURDIR)

COMMIT           := $(shell git rev-parse --short=8 HEAD)
UPSTREAM_VERSION := $(shell python3 -c "import json; print(json.load(open('electron/wire.json'))['version'])")
RELEASE          := $(shell sh .copr/compute-release.sh $(UPSTREAM_VERSION))

WORKDIR := $(CURDIR)/.copr-srpm-build
TARBALL := $(NAME)-$(UPSTREAM_VERSION).tar.gz

.PHONY: srpm
srpm:
	rm -rf "$(WORKDIR)"
	mkdir -p "$(WORKDIR)/SOURCES" "$(outdir)"
	git archive --format=tar.gz --prefix=$(NAME)-$(UPSTREAM_VERSION)/ HEAD \
		-o "$(WORKDIR)/SOURCES/$(TARBALL)"
	sed \
		-e 's/^%global commit0 .*/%global commit0 $(COMMIT)/' \
		-e 's/^%global release_counter .*/%global release_counter $(RELEASE)/' \
		-e 's/^%global upstream_version .*/%global upstream_version $(UPSTREAM_VERSION)/' \
		"$(spec)" > "$(WORKDIR)/$(notdir $(spec))"
	rpmbuild -bs \
		--define "_topdir $(WORKDIR)" \
		--define "_sourcedir $(WORKDIR)/SOURCES" \
		--define "_srcrpmdir $(outdir)" \
		"$(WORKDIR)/$(notdir $(spec))"
