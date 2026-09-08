# .copr/Makefile
#
# Invoked by Copr as: make -f .copr/Makefile srpm outdir="<outdir>" spec="<spec_path>"
# CWD is the already-checked-out git worktree (Copr's SCM clone) -- no re-clone
# needed. Mirrors the srpm: idiom already used by every package in
# ykner/GNOME-X11 (see e.g. github.com/ykne/mutter/.copr/Makefile): the
# make_srpm chroot is minimal and doesn't ship `git` by default (confirmed
# empirically: "make: git: No such file or directory"), so it's installed on
# demand via dnf -- network access is available in this step.

NAME := wire-desktop
spec ?= .copr/$(NAME).spec
outdir ?= $(CURDIR)

.PHONY: srpm
srpm:
	set -e; \
	command -v git >/dev/null 2>&1 || dnf install -y git-core; \
	commit=$$(git rev-parse --short=8 HEAD); \
	upstream_version=$$(grep '"version"' electron/wire.json | head -1 | sed -E 's/.*"version": *"([^"]*)".*/\1/'); \
	release=$$(sh .copr/compute-release.sh "$$upstream_version"); \
	workdir=$$(mktemp -d); \
	mkdir -p "$$workdir/$(NAME)-$$upstream_version" "$$workdir/SOURCES"; \
	git archive HEAD | tar -x -C "$$workdir/$(NAME)-$$upstream_version"; \
	tar -czf "$$workdir/SOURCES/$(NAME)-$$upstream_version.tar.gz" -C "$$workdir" "$(NAME)-$$upstream_version"; \
	sed \
		-e "s/^%global commit0 .*/%global commit0 $$commit/" \
		-e "s/^%global release_counter .*/%global release_counter $$release/" \
		-e "s/^%global upstream_version .*/%global upstream_version $$upstream_version/" \
		"$(spec)" > "$$workdir/$(notdir $(spec))"; \
	rpmbuild -bs \
		--define "_topdir $$workdir" \
		--define "_sourcedir $$workdir/SOURCES" \
		--define "_srcrpmdir $(outdir)" \
		"$$workdir/$(notdir $(spec))"; \
	rm -rf "$$workdir"
