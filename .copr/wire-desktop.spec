# .copr/wire-desktop.spec
#
# Re-wraps the RPM that `env LINUX_TARGET=rpm node .yarn/releases/yarn-3.3.1.cjs build:linux`
# (electron-builder -> fpm) already produces correctly, instead of re-deriving the
# desktop-file/icon/mimetype/category config that only exists in that pipeline
# (see bin/build-tools/lib/build-linux.ts).
#
# The three globals below (commit0, release_counter, upstream_version) are
# placeholders that .copr/Makefile overwrites (via sed, before calling
# `rpmbuild -bs`) with literal values computed from git, electron/wire.json,
# and Copr's own package API. This bakes them into the spec text stored inside
# the generated SRPM, so the later mock %build/%install phase (which only sees
# the git-archive tarball, with no .git present) never needs git or network
# access for versioning purposes.
%global commit0          0000000
%global release_counter  1
%global upstream_version 0.0.0

%global app_dir /opt/Wire

# Prebuilt Electron/Chromium binaries: no usable debuginfo, and rpm's ELF scanner
# must not treat the bundled libEGL.so/libGLESv2.so/libvulkan.so.1/libvk_swiftshader.so/
# libffmpeg.so (Chromium's own vendored copies) as system-wide Provides, nor derive
# spurious Requires from the huge wire-desktop binary itself.
%global debug_package %{nil}
%global __requires_exclude_from ^%{app_dir}/.*$
%global __provides_exclude_from ^%{app_dir}/.*$

Name:           wire-desktop
Version:        %{upstream_version}
Release:        %{release_counter}.git%{commit0}%{?dist}
Summary:        The most secure collaboration platform.

License:        GPL-3.0
URL:            https://wire.com
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  nodejs22-bin
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  python3
BuildRequires:  cpio

Requires:       alsa-lib
Requires:       libnotify
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       nss

# rpmbuild's ELF scanner must not walk the prebuilt payload (see excludes above);
# these are runtime deps only, not link-time NEEDED entries fpm relied on either.
AutoReqProv:    no

%description
The most secure collaboration platform.

%prep
%autosetup -n %{name}-%{version}

%build
# electron-builder rebuilds native modules (e.g. registry-js, via node-gyp) against
# Electron's own headers, not the system Node -- gcc-c++/make/python3 above are for
# that step. BUILD_NUMBER short-circuits getProjectVersion()'s internal
# `git rev-parse --short HEAD` (bin/build-tools/lib/commonConfig.ts), which would
# otherwise silently degrade to "-unknown" here since there is no .git in this tree.
export BUILD_NUMBER="0-%{commit0}"
node .yarn/releases/yarn-3.3.1.cjs install --immutable
env LINUX_TARGET=rpm node .yarn/releases/yarn-3.3.1.cjs build:linux

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
built_rpm=$(ls wrap/dist/*.rpm)
( cd %{buildroot} && rpm2cpio "%{_builddir}/%{name}-%{version}/${built_rpm}" | cpio -idmv )

%files
%license LICENSE
%doc README.md
%{_bindir}/wire-desktop
%{_datadir}/applications/wire-desktop.desktop
%{_datadir}/icons/hicolor/*/apps/wire-desktop.png
%dir %{app_dir}
%{app_dir}/*
# Re-listing the same already-globbed path with an explicit %attr is the
# standard rpm idiom for overriding one file's mode within a broader glob --
# an earlier version of this spec used %exclude + re-list instead, which is
# wrong: %exclude removes a path from the WHOLE file set regardless of line
# order, so it silently dropped chrome-sandbox from the package entirely
# (caught by a local `rpmbuild --rebuild` test: the file was simply missing).
# This idiom does print a harmless "File listed twice" build warning; verified
# locally that the final package still contains exactly one entry for this
# path with the correct -rwsr-xr-x root root mode.
%attr(4755,root,root) %{app_dir}/chrome-sandbox

# Re-added because rpm2cpio|cpio only copies the payload, never scriptlets: the
# original fpm-built rpm's %post is real (confirmed via `rpm -q --scripts -p`) and
# does not survive the re-wrap. Its %postun is comment-only, so it is omitted here.
%post
old_exec="/opt/Wire/wire";

# Warn if old package is still installed
if test -e "${old_exec}"; then
  echo "WARNING: It seems that there are files from the old Wire package on"
  echo "your machine. We highly recommend that you remove the old version"
  echo "and then reinstall this package. You can remove the old package with"
  echo "the following command:"
  echo "sudo apt-get remove wire"
fi

# Clean up old invalid links
if [ -L '/usr/local/bin/wire' ] || [ -L '/usr/local/bin/wire-desktop' ]; then
  echo "Removing old invalid symlinks"
  if [ -L '/usr/local/bin/wire' ] && [ "$(readlink '/usr/local/bin/wire')" = "${old_exec}" ]; then rm -f /usr/local/bin/wire; fi
  if [ -L '/usr/local/bin/wire-desktop' ] && [ "$(readlink '/usr/local/bin/wire-desktop')" = '/opt/Wire/wire-desktop' ]; then rm -f '/usr/local/bin/wire-desktop'; fi
fi

%changelog
* Tue Sep 08 2026 Eugene Kanter <eugene.kanter@outlook.com> - 3.44.0-1.git0000000
- Initial Copr packaging: re-wrap the electron-builder/fpm rpm produced by
  `build:linux` for automated builds on push (see .copr/Makefile and
  .copr/compute-release.sh for how Version/Release/Source0 are frozen at
  SRPM-generation time).
