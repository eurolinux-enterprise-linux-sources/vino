Name:    vino
Version: 3.22.0
Release: 7%{?dist}
Summary: A remote desktop system for GNOME

License: GPLv2+
URL:     https://wiki.gnome.org/Projects/Vino
#VCS:    git:git://git.gnome.org/vino
Source0: https://download.gnome.org/sources/%{name}/3.22/%{name}-%{version}.tar.xz

# https://bugzilla.redhat.com/show_bug.cgi?id=1380620
Patch0: revert-gsettings-conversion-file.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1546043
Patch1: Return-error-if-X11-is-not-detected.patch
Patch2: Do-not-restart-service-after-unclean-exit-code.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1580577
Patch3: Do-not-listen-all-if-invalid-interface-is-provided.patch
Patch4: Prevent-monitoring-all-interfaces-after-change-of-ot.patch
Patch5: Properly-remove-watches-when-changing-server-props.patch

BuildRequires: pkgconfig(avahi-client)
BuildRequires: pkgconfig(avahi-glib)
BuildRequires: pkgconfig(gnutls)
BuildRequires: pkgconfig(gtk+-x11-3.0)
BuildRequires: pkgconfig(ice)
BuildRequires: pkgconfig(libnotify)
BuildRequires: pkgconfig(libsecret-1)
BuildRequires: pkgconfig(sm)
BuildRequires: pkgconfig(telepathy-glib)
BuildRequires: libgcrypt-devel
BuildRequires: libXt-devel, libXtst-devel, libXdamage-devel
BuildRequires: intltool
BuildRequires: gettext
BuildRequires: desktop-file-utils

# For user unit.
BuildRequires: systemd
%{?systemd_requires}

# Needed for autoreconf
BuildRequires: gnome-common

# Following requires are for directory ownership
Requires: telepathy-filesystem
Requires: dbus

%description
Vino is a VNC server for GNOME. It allows remote users to
connect to a running GNOME session using VNC.


%prep
%setup -q
%patch0 -p1 -b .revert-gsettings-conversion-file
%patch1 -p1 -b .Return-error-if-X11-is-not-detected
%patch2 -p1 -b .Do-not-restart-service-after-unclean-exit-code
%patch3 -p1 -b .Do-not-listen-all-if-invalid-interface-is-provided
%patch4 -p1 -b .Prevent-monitoring-all-interfaces-after-change-of-ot
%patch5 -p1 -b .Properly-remove-watches-when-changing-server-props

# Needed for revert-gsettings-conversion-file.patch
autoreconf -fi

%build
%configure                      \
  --disable-silent-rules        \
  --with-avahi                  \
  --with-secret                 \
  --with-telepathy              \
  --with-gnutls                 \

make %{?_smp_mflags}


%install
make install DESTDIR=%{buildroot} INSTALL="install -p"
%find_lang %{name}


%check
desktop-file-validate %{buildroot}%{_datadir}/applications/vino-server.desktop


%post
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
%systemd_user_post vino-server.service


%preun
%systemd_user_preun vino-server.service


%postun
if [ $1 -eq 0 ]; then
  touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
  gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
  glib-compile-schemas %{_datadir}/glib-2.0/schemas &>/dev/null || :
fi
%systemd_user_postun vino-server.service


%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
glib-compile-schemas %{_datadir}/glib-2.0/schemas &>/dev/null || :


%files -f %{name}.lang
%doc AUTHORS NEWS README docs/TODO docs/remote-desktop.txt
%license COPYING
%{_datadir}/dbus-1/services/org.freedesktop.Telepathy.Client.Vino.service
%{_datadir}/telepathy/clients/Vino.client
%{_libexecdir}/*
%{_datadir}/applications/vino-server.desktop
%{_datadir}/glib-2.0/schemas/org.gnome.Vino.enums.xml
%{_datadir}/glib-2.0/schemas/org.gnome.Vino.gschema.xml
%{_datadir}/GConf/gsettings/org.gnome.Vino.convert
%{_userunitdir}/vino-server.service


%changelog
* Mon Aug 27 2018 Ondrej Holy <oholy@redhat.com> - 3.22.0-7
- Prevent monitoring all interfaces after change of other props
- Resolves: #1580577

* Wed May 23 2018 Ondrej Holy <oholy@redhat.com> - 3.22.0-6
- Do not restart service after unclean exit code
- Do not listen all if invalid interface is provided
- Resolves: #1546043, #1580577

* Mon May 21 2018 Ondrej Holy <oholy@redhat.com> - 3.22.0-5
- Return error if X11 is not detected
- Resolves: #1546043

* Mon May 21 2018 Ondrej Holy <oholy@redhat.com> - 3.22.0-4
- Add missing parameter for systemd scriptlets
- Resolves: #1507892

* Thu Mar 2 2017 Ondrej Holy <oholy@redhat.com> - 3.22.0-3
- Revert GSettings conversion file
- Resolves: #1380620

* Thu Feb 23 2017 Ondrej Holy <oholy@redhat.com> - 3.22.0-2
- Revert icon cache scriplets
- Resolves: #1387055

* Thu Feb 16 2017 Ondrej Holy <oholy@redhat.com> - 3.22.0-1
- Update to 3.22.0
- Resolves: #1387055, #1380620

* Mon Mar 23 2015 Richard Hughes <rhughes@redhat.com> - 3.14.2-1
- Update to 3.14.2
- Resolves: #1174570, #1192548

* Sat Feb 15 2014 Soren Sandmann <ssp@redhat.com> - 3.8.1-10
- Do not install vino-preferences.ui (#1059231)

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 3.8.1-9
- Mass rebuild 2014-01-24

* Tue Jan 7 2014 Soren Sandmann <ssp@redhat.com> - 3.8.1-8
- Make 'initialised' variable static; caught by coverity

* Mon Jan 6 2014 Soren Sandmann <ssp@redhat.com> - 3.8.1-7
- Also dont install the .desktop file for vino-preferences

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 3.8.1-6
- Mass rebuild 2013-12-27

* Fri Dec 20 2013 Soren Sandmann <ssp@redhat.com> - 3.8.1-5
- Dont install vino-preferences and vino-passwd.
- This fixes bugs 882985, 948897, and 955591

* Tue Dec 17 2013 Soren Sandmann <ssp@redhat.com> - 3.8.1-4
- Translation updates (bz 1030384)

* Wed Sep 18 2013 Debarshi Ray <rishi@fedorapeople.org> - 3.8.1-3
- Fix denial of service (CVE-2013-5745)

* Mon Jun 10 2013 Matthias Clasen <mclasen@redhat.com> - 3.8.1-2
- Be more careful with memory allocation

* Mon Apr 15 2013 Kalev Lember <kalevlember@gmail.com> - 3.8.1-1
- Update to 3.8.1

* Tue Mar 26 2013 Kalev Lember <kalevlember@gmail.com> - 3.8.0-1
- Update to 3.8.0

* Tue Mar 19 2013 Richard Hughes <rhughes@redhat.com> - 3.7.92-1
- Update to 3.7.92

* Fri Mar  8 2013 Matthias Clasen <mclasen@redhat.com> - 3.7.91-1
- Update to 3.7.91

* Tue Feb 19 2013 Richard Hughes <rhughes@redhat.com> - 3.7.90-1
- Update to 3.7.90

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.7.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jan 16 2013 Richard Hughes <hughsient@gmail.com> - 3.7.4-1
- Update to 3.7.4

* Wed Jan 09 2013 Richard Hughes <hughsient@gmail.com> - 3.7.3-1
- Update to 3.7.3

* Sun Dec  2 2012 Matthias Clasen <mclasen@redhat.com> - 3.6.2-2
- Don't add a vendor prefix to the desktop file, that breaks
  activating the preferences from the statusicon (#827913)

* Tue Nov 13 2012 Kalev Lember <kalevlember@gmail.com> - 3.6.2-1
- Update to 3.6.2

* Wed Oct 17 2012 Kalev Lember <kalevlember@gmail.com> - 3.6.1-1
- Update to 3.6.1

* Tue Sep 25 2012 Matthias Clasen <mclasen@redhat.com> - 3.6.0-1
- Update to 3.6.0

* Wed Sep 19 2012 Richard Hughes <hughsient@gmail.com> - 3.5.92-1
- Update to 3.5.92

* Wed Aug 22 2012 Richard Hughes <hughsient@gmail.com> - 3.5.90-1
- Update to 3.5.90

* Fri Jul 27 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.5.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jun 07 2012 Richard Hughes <hughsient@gmail.com> - 3.5.2-1
- Update to 3.5.2

* Sun May 06 2012 Kalev Lember <kalevlember@gmail.com> - 3.5.1-1
- Update to 3.5.1

* Tue Apr 24 2012 Kalev Lember <kalevlember@gmail.com> - 3.4.1-2
- Silence rpm scriptlet output

* Tue Apr 17 2012 Kalev Lember <kalevlember@gmail.com> - 3.4.1-1
- Update to 3.4.1

* Tue Mar 27 2012 Debarshi Ray <rishi@fedoraproject.org> - 3.4.0-1
- Update to 3.4.0

* Wed Mar 21 2012 Kalev Lember <kalevlember@gmail.com> - 3.3.92-1
- Update to 3.3.92
- Don't BR unique-devel; vino doesn't use libunique any more

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Dec 21 2011 Matthias Clasen <mclasen@redhat.com> - 3.3.3-1
- Update to 3.3.3

* Wed Nov  2 2011 Matthias Clasen <mclasen@redhat.com> - 3.3.1-1
- Update to 3.3.1

* Wed Oct 26 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2.1-2
- Rebuilt for glibc bug#747377

* Wed Oct 19 2011 Matthias Clasen <mclasen@redhat.com> - 3.2.1-1
- Update to 3.2.1

* Tue Sep 27 2011 Ray <rstrode@redhat.com> - 3.2.0-1
- Update to 3.2.0

* Tue Sep 20 2011 Matthias Clasen <mclasen@redhat.com> - 3.1.92-1
- Update to 3.1.92

* Tue Sep  6 2011 Matthias Clasen <mclasen@redhat.com> - 3.1.91-1
- Update to 3.1.91

* Wed Aug 31 2011 Matthias Clasen <mclasen@redhat.com> - 3.1.90-1
- Update to 3.1.90

* Thu Aug 18 2011 Matthias Clasen <mclasen@redhat.com> - 3.1.5-1
- Update to 3.1.5

* Mon Jul 25 2011 Matthias Clasen <mclasen@redhat.com> - 3.1.4-1
- Update to 3.1.4

* Tue Jul 05 2011 Bastien Nocera <bnocera@redhat.com> 3.1.3-1
- Update to 3.1.3

* Tue Jun 14 2011 Tomas Bzatek <tbzatek@redhat.com> - 3.1.2-1
- Update to 3.1.2

* Wed May 11 2011 Tomas Bzatek <tbzatek@redhat.com> - 3.1.1-1
- Update to 3.1.1

* Sat May 07 2011 Christopher Aillon <caillon@redhat.com> - 3.0.2-2
- Update icon cache scriptlet

* Wed May  4 2011 Christopher Aillon <caillon@redhat.com> - 3.0.2-1
- Update to 3.0.2

* Mon Apr 25 2011 Matthias Clasen <mclasen@redhat.com> - 3.0.1-1
- Update to 3.0.1

* Mon Apr  4 2011 Matthias Clasen <mclasen@redhat.com> - 3.0.0-1
- Update to 3.0.0

* Fri Mar 25 2011 Matthias Clasen <mclasen@redhat.com> - 2.99.5-1
- Update to 2.99.5

* Mon Mar 21 2011 Matthias Clasen <mclasen@redhat.com> - 2.99.4-1
- Update to 2.99.4

* Tue Mar  8 2011 Matthias Clasen <mclasen@redhat.com> - 2.99.3-1
- Update to 2.99.3

* Tue Feb 22 2011 Matthias Clasen <mclasen@redhat.com> - 2.99.0-1
- Update to 2.99.0

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.32.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Nov  3 2010 Matthias Clasen <mclasen@redhat.com> - 2.32.0-2
- Rebuild against libnotify 0.7.0

* Wed Sep 29 2010 Matthias Clasen <mclasen@redhat.com> - 2.32.0-1
- Update to 2.32.0

* Tue Aug 31 2010 Matthias Clasen <mclasen@redhat.com> - 2.31.91-1
- Update to 2.31.91

* Wed Jun 30 2010 Matthias Clasen <mclasen@redhat.com> - 2.31.4-1
- Update to 2.31.4

* Tue Mar 30 2010 Matthias Clasen <mclasen@redhat.com> - 2.28.2-1
- Update to 2.28.2

* Mon Oct 19 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.1-1
- Update to 2.28.1

* Sun Sep 27 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-3
- Even better, just rely on autostart

* Sun Sep 27 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-2
- Make vino-server set a proper restart command

* Wed Sep 23 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-1
- Update to 2.28.0

* Mon Sep  7 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.92-1
- Update to 2.27.92

* Tue Aug 25 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.91-1
- Update to 2.27.91

* Tue Aug 11 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.90-1
- Update to 2.27.90

* Mon Aug  3 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.5-2
- Enable telepathy

* Tue Jul 28 2009 Matthias Clasen <mclasen@redhat.com> - 2.27.5-1
- Update to 2.27.5

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.26.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul  9 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-5
- Rebuild to shrink GConf schemas

* Tue Jun 16 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-4
- Try again: rebuild with new gcc

* Mon Jun 15 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-3
- Rebuild with new gcc

* Fri Jun 12 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-2
- Drop unneeded direct dependencies

* Mon Apr 13 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-1
- Update to 2.26.1
- See http://download.gnome.org/sources/vino/2.26/vino-2.26.1.news

* Mon Mar 16 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-1
- Update to 2.26.0

* Mon Mar  2 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.92-1
- Update to 2.25.92
- Enable NetworkManager support

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.91-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 18 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.91-1
- Update to 2.25.91

* Tue Feb  3 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.90-1
- Update to 2.25.90

* Fri Jan 23 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.5-1
- Update to 2.25.5

* Tue Jan  6 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.4-1
- Update to 2.25.4

* Wed Dec 17 2008 Matthias Clasen <mclasen@redhat.com> - 2.25.3-1
- Update to 2.25.3

* Mon Oct 20 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.1-1
- Update to 2.24.1

* Mon Sep 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.0-1
- Update to 2.24.0

* Mon Sep  8 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.92-1
- Update to 2.23.92

* Tue Sep  2 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.91-1
- Update to 2.23.91

* Fri Aug 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.90-1
- Update to 2.23.90

* Fri Jul 25 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.5-3
- Use autostart to have gnome-session start the server

* Fri Jul 25 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.5-2
- Use standard icon names

* Tue Jul 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.5-1
- Update to 2.23.5

* Mon Apr  7 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.1-1
- Update to 2.22.1

* Mon Mar 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-1
- Update to 2.22.0

* Mon Feb 25 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.92-1
- Update 2.21.92

* Tue Feb 12 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.91-1
- Update to 2.21.91

* Tue Jan 29 2008 Matthias Clasen <mclasen@redhat.com> - 2.21.90-1
- Update to 2.21.90

* Wed Dec  5 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.3-1
- Update to 2.21.3

* Tue Nov 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.2-1
- Update to 2.21.2

* Tue Oct 23 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-2
- Rebuild against new dbus-glib

* Mon Oct 15 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-1
- Update to 2.20.1 (translation updates)

* Tue Oct  2 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-2
- Fix a directory ownership issue

* Mon Sep 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-1
- Update to 2.20.0

* Tue Sep  4 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.92-1
- Update to 2.19.92

* Mon Aug 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.90-1
- Update to 2.19.90
- Update the license field

* Mon Jul  9 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.5-1
- Update to 2.19.5

* Sun May 20 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.1-1
- Update to 2.18.1

* Tue Mar 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.18.0-1
- Update to 2.18.0

* Tue Feb 27 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.92-1
- Update to 2.17.92
- Drop obsolete patches

* Wed Jan 24 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.5-2
- Fix some careless gconf value handling
- use libnotify
- Improve category in the desktop file

* Wed Jan 10 2007 Matthias Clasen <mclasen@redhat.com> - 2.17.5-1
- Update to 2.17.5

* Tue Dec 19 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.4-1
- Update to 2.17.4

* Mon Nov  6 2006 Matthias Clasen <mclasen@redhat.com> - 2.17.2-1
- Update to 2.17.2

* Sun Oct 22 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-1
- Update to 2.16.0

* Wed Oct 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.5-6
- Fix scripts according to the packaging guidelines

* Tue Oct 17 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.5-5
- Fix #191160

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.13.5-4.1
- rebuild

* Sat Jun 10 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.5-4
- More missing BuildRequires

* Mon May 22 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.5-3
- Add missing BuildRequires

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.13.5-2.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.13.5-2.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Tue Jan 17 2006 Mark McLoughlin <markmc@redhat.com> 2.13.5-2
- Build with --enable-avahi

* Tue Jan 17 2006 Matthias Clasen <mclasen@redhat.com> 2.13.5-1
- Update to 2.13.5

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Mon Sep 26 2005 Mark McLoughlin <markmc@redhat.com> 2.12.0-2
- Add patch from Alexandre Oliva <oliva@lsd.ic.unicamp.br> to fix
  more keyboard brokeness (#158713)

* Wed Sep  7 2005 Matthias Clasen <mclasen@redhat.com> 2.12.0-1
- Update to 2.12.0

* Wed Aug 17 2005 Matthias Clasen <mclasen@redhat.com> 2.11.90-2
- Rebuild

* Thu Aug  4 2005 Matthias Clasen <mclasen@redhat.com> 2.11.90-1
- New upstream version

* Mon Jul 11 2005 Matthias Clasen <mclasen@redhat.com> 2.11.1.2-1
- Newer upstream version
- Drop upstreamed patches

* Fri May 20 2005 Mark McLoughlin <markmc@redhat.com> 2.10.0-4
- Fix various keyboarding handling issues:
   + bug #142974: caps lock not working
   + bug #140515: shift not working with some keys
   + bug #134451: over-eager key repeating

* Wed Apr 27 2005 Jeremy Katz <katzj@redhat.com> - 2.10.0-3
- silence %%post

* Mon Mar 28 2005 Christopher Aillon <caillon@redhat.com>
- rebuilt

* Fri Mar 25 2005 Christopher Aillon <caillon@redhat.com> 2.10.0-1
- Update to 2.10.0
- Update the GTK+ theme icon cache on (un)install

* Wed Mar  2 2005 Mark McLoughlin <markmc@redhat.com> 2.9.2-2
- Rebuild with gcc4

* Thu Jan 27 2005 Matthias Clasen <mclasen@redhat.com> 2.9.2-1
- Update to 2.9.2

* Tue Oct 12 2004 Mark McLoughlin <markmc@redhat.com> 2.8.1-1
- Update to 2.8.1
- Remove backported fixes

* Thu Oct  7 2004 Mark McLoughlin <markmc@redhat.com> 2.8.0.1-1.1
- Don't hang with metacity's "reduced resources" mode (#134240) 
- Improve the key repeat rate situation a good deal (#134451)

* Wed Sep 29 2004 Mark McLoughlin <markmc@redhat.com> 2.8.0.1-1
- Update to 2.8.0.1

* Tue Sep 21 2004 Mark McLoughlin <markmc@redhat.com> 2.8.0-1
- Update to 2.8.0
- Remove upstreamed work-without-gnutls patch

* Tue Sep  7 2004 Matthias Clasen <mclasen@redhat.com> 2.7.92-3
- Disable help button until there is help (#131632)
 
* Wed Sep  1 2004 Mark McLoughlin <markmc@redhat.com> 2.7.92-2
- Add patch to fix hang without GNU TLS (bug #131354)

* Mon Aug 30 2004 Mark McLoughlin <markmc@redhat.com> 2.7.92-1
- Update to 2.7.92

* Tue Aug 17 2004 Mark McLoughlin <markmc@redhat.com> 2.7.91-1
- Update to 2.7.91

* Mon Aug 16 2004 Mark McLoughlin <markmc@redhat.com> 2.7.90-2
- Define libgcrypt_version

* Thu Aug 12 2004 Mark McLoughlin <markmc@redhat.com> 2.7.90-1
- Update to 2.7.90

* Wed Aug  4 2004 Mark McLoughlin <markmc@redhat.com> 2.7.4-1
- Update to 2.7.4

* Tue Jul 13 2004 Mark McLoughlin <markmc@redhat.com> 2.7.3.1-1
- Initial build.
