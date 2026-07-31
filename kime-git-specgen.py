import requests as web
import json
import re

OUTPUT_NAME = "kime-git.spec"

REPO_API = "https://api.github.com/repos/Riey/kime"
REPO_TAGS = f"{REPO_API}/tags"
# REPO_DEV_BRANCH = f"{REPO_API}/branches/develop"
REPO_DEV_LATEST_COMMIT = f"{REPO_API}/commits?sha=develop&per_page=1&page=1"

COMMIT_COUNT_REGEX = r'[?&]page=(\d+)[^;]*?>\s*;\s*rel\s*=\s*"last"'

repo_latest_tag = json.loads(web.get(REPO_TAGS).content)[0]["name"].strip()[1:]
repo_latest_commit = web.get(REPO_DEV_LATEST_COMMIT)
# header "Link" example of `repo_latest_commit`
# REPO_LATEST_COMMIT_LINK_HEADER_EXAMPLE = '<https://api.github.com/repositories/320661831/commits?sha=develop&per_page=1&page=2>; rel="next", <https://api.github.com/repositories/320661831/commits?sha=develop&per_page=1&page=675>; rel="last"'
repo_commit_count = re.search(
    COMMIT_COUNT_REGEX, repo_latest_commit.headers["Link"]
).group(1)  # type: ignore
repo_latest_commit_hash = json.loads(repo_latest_commit.content)[0]["sha"]
repo_latest_commit_id = repo_latest_commit_hash[:7]


package_version = f"{repo_latest_tag}^git_{repo_commit_count}_{repo_latest_commit_id}"

package_spec = f"""
Name: kime-git
Version: {package_version}
Release: 1
License: GPLv3
Summary: Korean IME
Url: https://github.com/Riey/kime
Source0: %{{url}}/archive/{repo_latest_commit_id}.tar.gz

BuildRequires: clang-devel
BuildRequires: meson
BuildRequires: ninja-build
BuildRequires: pkgconf-pkg-config
BuildRequires: gtk3-devel
BuildRequires: gtk4-devel
BuildRequires: qt5-qtbase-private-devel
BuildRequires: qt6-qtbase-private-devel
BuildRequires: dbus-devel
BuildRequires: libxcb-devel
BuildRequires: fontconfig-devel
BuildRequires: freetype-devel
BuildRequires: libxkbcommon-devel

Requires: (google-noto-sans-cjk-vf-fonts or google-noto-sans-cjk-fonts)
Requires: im-chooser

Conflicts: kime

%define kime_imsettings_conf kime-imsettings.conf

%description
kime is a fast, lightweight, reliable and highly customizable input engine for Korean input.

%prep
%autosetup -n kime-{repo_latest_commit_hash}

%build
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- --profile default -y
. "$HOME/.cargo/env"
%meson \
	-Dgtk3=enabled \
	-Dgtk4=enabled \
	-Dqt5=enabled \
	-Dqt6=enabled \
	-Dcargo_profile=release \
	-Dinstall_headers=true \
	-Dinstall_docs=false
%meson_build

cat > %{{kime_imsettings_conf}} << EOF
SHORT_DESC="kime"
XIM=kime
XIM_PROGRAM=%{{_bindir}}/kime-xim
GTK_IM_MODULE=kime
QT_IM_MODULE=kime
AUXILIARY_PROGRAM=%{{_bindir}}/kime-indicator
IMSETTINGS_IGNORE_SESSION=*-wayland
EOF

%install
%meson_install
rm -f %{{buildroot}}%{{_sysconfdir}}/xdg/autostart/kime.desktop
install -Dm644 %{{kime_imsettings_conf}} %{{buildroot}}%{{_sysconfdir}}/X11/xinit/xinput.d/kime.conf

%files
%license LICENSE*
%doc README.md
%doc README.ko.md
%doc NOTICE.md
%doc docs/CONFIGURATION.md
%doc docs/CONFIGURATION.ko.md
%doc docs/CHANGELOG.md
%doc res/default_config.yaml

%{{_bindir}}/kime
%{{_bindir}}/kime-xdg-autostart
%{{_bindir}}/kime-check
%{{_bindir}}/kime-indicator
%{{_bindir}}/kime-candidate-window
%{{_bindir}}/kime-xim
%{{_bindir}}/kime-wayland

%{{_libdir}}/libkime_engine.so
%{{_libdir}}/gtk-3.0/3.0.0/immodules/libim-kime.so
%{{_libdir}}/gtk-4.0/4.0.0/immodules/libkime-gtk4.so
%{{_libdir}}/qt5/plugins/platforminputcontexts/libkimeplatforminputcontextplugin.so
%{{_libdir}}/qt6/plugins/platforminputcontexts/libkimeplatforminputcontextplugin.so

%{{_includedir}}/kime_engine.h
%{{_includedir}}/kime_engine.hpp

%{{_sysconfdir}}/X11/xinit/xinput.d/kime.conf
%{{_datadir}}/applications/kime.desktop
%{{_datadir}}/icons/hicolor/64x64/apps/*
"""

print(package_spec)

with open(file="kime-git.spec", mode="w") as spec_file:
    spec_file.write(package_spec)
