###############################################################################
###############################################################################
##
##  Copyright (C) 2012-2023 Red Hat, Inc.  All rights reserved.
##
##  This copyrighted material is made available to anyone wishing to use,
##  modify, copy, or redistribute it subject to the terms and conditions
##  of the GNU General Public License v.2 or higher
##
###############################################################################
###############################################################################

# set defaults from ./configure invocation
%bcond_without sctp
%bcond_without nss
%bcond_without openssl
%bcond_without zlib
%bcond_without lz4
%bcond_without lzo2
%bcond_without lzma
%bcond_without bzip2
%bcond_without zstd
%bcond_without libnozzle
%bcond_without runautogen
%bcond_with rpmdebuginfo
%bcond_with overriderpmdebuginfo
%bcond_without buildman
%bcond_without installtests

%if %{with overriderpmdebuginfo}
%undefine _enable_debug_packages
%endif

# main (empty) package
# http://www.rpm.org/max-rpm/s1-rpm-subpack-spec-file-changes.html

Name: kronosnet
Summary: Multipoint-to-Multipoint VPN daemon
Version: 1.25
Release: 2%{?dist}
License: GPLv2+ and LGPLv2+
URL: https://kronosnet.org
Source0: https://kronosnet.org/releases/%{name}-%{version}.tar.xz

#Patch0: 1_24.testfix.patch

# Build dependencies
BuildRequires: make
BuildRequires: gcc libqb-devel
# required to build man pages
%if %{with buildman}
BuildRequires: libxml2-devel doxygen doxygen2man
%endif
%if %{with sctp}
BuildRequires: lksctp-tools-devel
%endif
%if %{with nss}
BuildRequires: nss-devel
%endif
%if %{with openssl}
BuildRequires: openssl-devel
%endif
%if %{with zlib}
BuildRequires: zlib-devel
%endif
%if %{with lz4}
BuildRequires: lz4-devel
%endif
%if %{with lzo2}
BuildRequires: lzo-devel
%endif
%if %{with lzma}
BuildRequires: xz-devel
%endif
%if %{with bzip2}
BuildRequires: bzip2-devel
%endif
%if %{with zstd}
BuildRequires: libzstd-devel
%endif
%if %{with libnozzle}
BuildRequires: libnl3-devel
%endif
%if %{with runautogen}
BuildRequires: autoconf automake libtool
%endif

%prep
%setup -q -n %{name}-%{version}
#%patch0 -p1 -b .1_24.testfix

%build
%if %{with runautogen}
./autogen.sh
%endif

%{configure} \
%if %{with installtests}
	--enable-install-tests \
%else
	--disable-install-tests \
%endif
%if %{with buildman}
	--enable-man \
%else
	--disable-man \
%endif
%if %{with sctp}
	--enable-libknet-sctp \
%else
	--disable-libknet-sctp \
%endif
%if %{with nss}
	--enable-crypto-nss \
%else
	--disable-crypto-nss \
%endif
%if %{with openssl}
	--enable-crypto-openssl \
%else
	--disable-crypto-openssl \
%endif
%if %{with zlib}
	--enable-compress-zlib \
%else
	--disable-compress-zlib \
%endif
%if %{with lz4}
	--enable-compress-lz4 \
%else
	--disable-compress-lz4 \
%endif
%if %{with lzo2}
	--enable-compress-lzo2 \
%else
	--disable-compress-lzo2 \
%endif
%if %{with lzma}
	--enable-compress-lzma \
%else
	--disable-compress-lzma \
%endif
%if %{with bzip2}
	--enable-compress-bzip2 \
%else
	--disable-compress-bzip2 \
%endif
%if %{with zstd}
	--enable-compress-zstd \
%else
	--disable-compress-zstd \
%endif
%if %{with libnozzle}
	--enable-libnozzle \
%else
	--disable-libnozzle \
%endif
	--with-initdefaultdir=%{_sysconfdir}/sysconfig/ \
	--with-systemddir=%{_unitdir}

make %{_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

# tree cleanup
# remove static libraries
find %{buildroot} -name "*.a" -exec rm {} \;
# remove libtools leftovers
find %{buildroot} -name "*.la" -exec rm {} \;

# remove init scripts
rm -rf %{buildroot}/etc/init.d

# remove docs
rm -rf %{buildroot}/usr/share/doc/kronosnet

# main empty package
%description
 The kronosnet source

%if %{with libnozzle}
%package -n libnozzle1
Summary: Simple userland wrapper around kernel tap devices
License: LGPLv2+

%description -n libnozzle1
 This is an over-engineered commodity library to manage a pool
 of tap devices and provides the basic
 pre-up.d/up.d/down.d/post-down.d infrastructure.

%files -n libnozzle1
%license COPYING.* COPYRIGHT
%{_libdir}/libnozzle.so.*

%if 0%{?ldconfig_scriptlets}
%ldconfig_scriptlets -n libnozzle1
%else
%post -n libnozzle1 -p /sbin/ldconfig
%postun -n libnozzle1 -p /sbin/ldconfig
%endif

%package -n libnozzle1-devel
Summary: Simple userland wrapper around kernel tap devices (developer files)
License: LGPLv2+
Requires: libnozzle1%{_isa} = %{version}-%{release}
Requires: pkgconfig

%description -n libnozzle1-devel
 This is an over-engineered commodity library to manage a pool
 of tap devices and provides the basic
 pre-up.d/up.d/down.d/post-down.d infrastructure.

%files -n libnozzle1-devel
%license COPYING.* COPYRIGHT
%{_libdir}/libnozzle.so
%{_includedir}/libnozzle.h
%{_libdir}/pkgconfig/libnozzle.pc
%if %{with buildman}
%{_mandir}/man3/nozzle*.3.gz
%endif
%endif

%package -n libknet1
Summary: Kronosnet core switching implementation
License: LGPLv2+

%description -n libknet1
 The whole kronosnet core is implemented in this library.
 Please refer to the not-yet-existing documentation for further
 information.

%files -n libknet1
%license COPYING.* COPYRIGHT
%{_libdir}/libknet.so.*
%dir %{_libdir}/kronosnet

%if 0%{?ldconfig_scriptlets}
%ldconfig_scriptlets -n libknet1
%else
%post -n libknet1 -p /sbin/ldconfig
%postun -n libknet1 -p /sbin/ldconfig
%endif

%package -n libknet1-devel
Summary: Kronosnet core switching implementation (developer files)
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}
Requires: pkgconfig

%description -n libknet1-devel
 The whole kronosnet core is implemented in this library.
 Please refer to the not-yet-existing documentation for further
 information. 

%files -n libknet1-devel
%license COPYING.* COPYRIGHT
%{_libdir}/libknet.so
%{_includedir}/libknet.h
%{_libdir}/pkgconfig/libknet.pc
%if %{with buildman}
%{_mandir}/man3/knet*.3.gz
%endif

%if %{with nss}
%package -n libknet1-crypto-nss-plugin
Summary: Provides libknet1 nss support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-crypto-nss-plugin
 Provides NSS crypto support for libknet1.

%files -n libknet1-crypto-nss-plugin
%{_libdir}/kronosnet/crypto_nss.so
%endif

%if %{with openssl}
%package -n libknet1-crypto-openssl-plugin
Summary: Provides libknet1 openssl support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-crypto-openssl-plugin
 Provides OpenSSL crypto support for libknet1.

%files -n libknet1-crypto-openssl-plugin
%{_libdir}/kronosnet/crypto_openssl.so
%endif

%if %{with zlib}
%package -n libknet1-compress-zlib-plugin
Summary: Provides libknet1 zlib support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-compress-zlib-plugin
 Provides zlib compression support for libknet1.

%files -n libknet1-compress-zlib-plugin
%{_libdir}/kronosnet/compress_zlib.so
%endif

%if %{with lz4}
%package -n libknet1-compress-lz4-plugin
Summary: Provides libknet1 lz4 and lz4hc support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-compress-lz4-plugin
 Provides lz4 and lz4hc compression support for libknet1.

%files -n libknet1-compress-lz4-plugin
%{_libdir}/kronosnet/compress_lz4.so
%{_libdir}/kronosnet/compress_lz4hc.so
%endif

%if %{with lzo2}
%package -n libknet1-compress-lzo2-plugin
Summary: Provides libknet1 lzo2 support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-compress-lzo2-plugin
 Provides lzo2 compression support for libknet1.

%files -n libknet1-compress-lzo2-plugin
%{_libdir}/kronosnet/compress_lzo2.so
%endif

%if %{with lzma}
%package -n libknet1-compress-lzma-plugin
Summary: Provides libknet1 lzma support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-compress-lzma-plugin
 Provides lzma compression support for libknet1.

%files -n libknet1-compress-lzma-plugin
%{_libdir}/kronosnet/compress_lzma.so
%endif

%if %{with bzip2}
%package -n libknet1-compress-bzip2-plugin
Summary: Provides libknet1 bzip2 support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-compress-bzip2-plugin
 Provides bzip2 compression support for libknet1.

%files -n libknet1-compress-bzip2-plugin
%{_libdir}/kronosnet/compress_bzip2.so
%endif

%if %{with zstd}
%package -n libknet1-compress-zstd-plugin
Summary: Provides libknet1 zstd support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-compress-zstd-plugin
 Provides zstd compression support for libknet1.

%files -n libknet1-compress-zstd-plugin
%{_libdir}/kronosnet/compress_zstd.so
%endif

%package -n libknet1-crypto-plugins-all
Summary: Provides libknet1 crypto plugins meta package
License: LGPLv2+
%if %{with nss}
Requires: libknet1-crypto-nss-plugin%{_isa} = %{version}-%{release}
%endif
%if %{with openssl}
Requires: libknet1-crypto-openssl-plugin%{_isa} = %{version}-%{release}
%endif

%description -n libknet1-crypto-plugins-all
 Provides meta package to install all of libknet1 crypto plugins

%files -n libknet1-crypto-plugins-all

%package -n libknet1-compress-plugins-all
Summary: Provides libknet1 compress plugins meta package
License: LGPLv2+
%if %{with zlib}
Requires: libknet1-compress-zlib-plugin%{_isa} = %{version}-%{release}
%endif
%if %{with lz4}
Requires: libknet1-compress-lz4-plugin%{_isa} = %{version}-%{release}
%endif
%if %{with lzo2}
Requires: libknet1-compress-lzo2-plugin%{_isa} = %{version}-%{release}
%endif
%if %{with lzma}
Requires: libknet1-compress-lzma-plugin%{_isa} = %{version}-%{release}
%endif
%if %{with bzip2}
Requires: libknet1-compress-bzip2-plugin%{_isa} = %{version}-%{release}
%endif
%if %{with zstd}
Requires: libknet1-compress-zstd-plugin%{_isa} = %{version}-%{release}
%endif

%description -n libknet1-compress-plugins-all
 Meta package to install all of libknet1 compress plugins

%files -n libknet1-compress-plugins-all

%package -n libknet1-plugins-all
Summary: Provides libknet1 plugins meta package
License: LGPLv2+
Requires: libknet1-compress-plugins-all%{_isa} = %{version}-%{release}
Requires: libknet1-crypto-plugins-all%{_isa} = %{version}-%{release}

%description -n libknet1-plugins-all
 Meta package to install all of libknet1 plugins

%files -n libknet1-plugins-all

%if %{with installtests}
%package -n kronosnet-tests
Summary: Provides kronosnet test suite
License: GPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}
%if %{with libnozzle}
Requires: libnozzle1%{_isa} = %{version}-%{release}
%endif

%description -n kronosnet-tests
 This package contains all the libknet and libnozzle test suite.

%files -n kronosnet-tests
%{_libdir}/kronosnet/tests/*
%endif

%if %{with rpmdebuginfo}
%debug_package
%endif

%changelog
* Wed Jan 18 2023 Christine Caulfield <ccaulfie@redhat.com> - 1.25-1
  Rebase to 1.25 for PMTUd fixes
  Resolves: rhbz#2161168

* Fri Jul 15 2022 Christine Caulfield <ccaulfie@redhat.com> - 1.24-2
- Fix libnozzle tests failing & covscan warning on api_knet_handle_new test
  Resolves: rhbz#2024090

* Fri Jul 15 2022 Christine Caulfield <ccaulfie@redhat.com> - 1.24-1
- Rebase to 1.24
  Resolves: rhbz#2024090

* Wed Oct 06 2021 Christine Caulfield <ccaulfie@redhat.com> - 1.22-3
- Add back the test suite that got lost in the pull from Fedora
  Resolves: rhbz#1999980

* Wed Oct 06 2021 Christine Caulfield <ccaulfie@redhat.com> - 1.22-1
- Rebase to v1.22
  Resolves: rhbz#1999980

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1.21-4
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Wed Jun 16 2021 Florian Weimer <fweimer@redhat.com> - 1.21-3
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Thu May 13 2021 Christine Caulfield <ccaulfie@redhat.com> - 1.21-2
- add -fstack-clash-protection to the build. For the CI
  Resolves: rhbz#1954551

* Wed Apr 28 2021 Christine Caulfield <ccaulfie@redhat.com> - 1.21-1
- Rebase to 1.21 to incorporate fixes for CI complaints & openssl3
  Resolves: rhbz#1954551

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 1.20-3
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.20-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Oct 19 2020 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.20-1
- New upstream release
- Fix TX/RX stats collections
- Minor test suite improvements
- Minor build fixes

* Mon Aug 17 2020 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.19-1
- New upstream release
- Add native support for openssl 3.0 (drop API COMPAT macros).
- Code cleanup of public APIs. Lots of lines of code moved around, no
  functional changes.
- Removed kronosnetd unsupported code completely
- Removed unused poc-code from the source tree
- Make sure to initialize epoll events structures

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.18-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jul 14 2020 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.18-1
- New upstream release
- Add ability to change crypto configuration at runtime without
  restarting knet and without packet drop
- Add compatibility support for openssl 3.0
- Add functional testing framework and new test cases
- Minor build fixes
- Fix BuildRequires to use libqb doxygen2man vs internal copy

* Thu Apr 23 2020 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.16-1
- New upstream release
- Fix major issues with SCTP transport
- Fix build with recent gcc
- Minor bug fixes
- Update BuildRequires now that libqb is used unconditionally

* Wed Mar 04 2020 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.15-1
- New upstream release
- Fix major interaction issues between stats gathering and PMTUd
- Fix UDP socket options that could lead to knet not being properly
  functional
- Man pages updates
- Minor bug fixes

* Fri Jan 31 2020 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.14-1
- New upstream release
- Fixes several major issues with newer kernels
- Fix build with gcc10

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.13-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Oct 16 2019 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.13-1
- New upstream release
- Fixes more memory corruption problems on unstable networks.

* Fri Sep 20 2019 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.12-1
- New upstream release
- Fixes memory corruption problem on unstable networks.

* Wed Aug 21 2019 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.11-1
- New upstream release
- Fixes major issues with PMTUd implementation when used in combination with
  crypto.

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Jun 12 2019 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.10-1
- New upstream release
- fix URL in spec file (rhbz#1708616)

* Thu May 09 2019 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.9-1
- New upstream release

* Wed May 08 2019 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.8-2
- Fix ldconfig scriptlet (Resolves rhbz#1699074)
- Cleanup .gitignore (Resolves rhbz#1699093)

* Wed Apr 03 2019 Madison Kelly <mkelly@alteeve.ca> - 1.8-1
- Updated to upstream release v1.8.
