Name: kime
Version: 3.2.0
Release: 1
License: GPLv3
Summary: Korean IME
Url: https://github.com/Riey/kime
Source0: %{url}/archive/refs/tags/v%{version}.tar.gz

# NOTE: Currently(3.2.0) the whole thing relies on meson by source repo.

# hopefully noarch; not tested.

## Refer to <https://github.com/Riey/kime#dependencies>
## to edit build requirements

# BuildRequires: cmake
BuildRequires: clang-devel
# BuildRequires: cargo # using rustup instead
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

# check dbus, fontconfig, freetype, libxcb in the future.
# optional runtime dependencies
# gtk3
# gtk4
# qt5
# qt6
# libdbus (dbus-libs) (indicator)
# xcb (candidate)
# fontconfig (xim)
# freetype (xim)
# libxkbcommon (wayland
Requires: (google-noto-sans-cjk-vf-fonts or google-noto-sans-cjk-fonts)
Requires: im-chooser

Conflicts: kime-git

%define kime_imsettings_conf kime-imsettings.conf

%description

kime is a fast, lightweight, reliable and highly customizable input engine for Korean input.

%prep
%autosetup

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

# custom im-chooser compatibility
cat > %{kime_imsettings_conf} << EOF
SHORT_DESC="kime"
XIM=kime
XIM_PROGRAM=%{_bindir}/kime-xim
GTK_IM_MODULE=kime
QT_IM_MODULE=kime
AUXILIARY_PROGRAM=%{_bindir}/kime-indicator
EOF

%install
%meson_install
## will not autostart by default
rm -f %{buildroot}%{_sysconfdir}/xdg/autostart/kime.desktop
install -Dm644 %{kime_imsettings_conf} %{buildroot}%{_sysconfdir}/X11/xinit/xinput.d/kime.conf

%files
%license LICENSE*
%doc README.md
%doc README.ko.md
%doc NOTICE.md
%doc docs/CONFIGURATION.md
%doc docs/CONFIGURATION.ko.md
%doc docs/CHANGELOG.md
%doc res/default_config.yaml

%{_bindir}/kime
%{_bindir}/kime-xdg-autostart
%{_bindir}/kime-check
%{_bindir}/kime-indicator
%{_bindir}/kime-candidate-window
%{_bindir}/kime-xim
%{_bindir}/kime-wayland

%{_libdir}/libkime_engine.so
%{_libdir}/gtk-3.0/3.0.0/immodules/libim-kime.so
%{_libdir}/gtk-4.0/4.0.0/immodules/libkime-gtk4.so
%{_libdir}/qt5/plugins/platforminputcontexts/libkimeplatforminputcontextplugin.so
%{_libdir}/qt6/plugins/platforminputcontexts/libkimeplatforminputcontextplugin.so

%{_includedir}/kime_engine.h
%{_includedir}/kime_engine.hpp

%{_sysconfdir}/X11/xinit/xinput.d/kime.conf
%{_datadir}/applications/kime.desktop
%{_datadir}/icons/hicolor/64x64/apps/*
