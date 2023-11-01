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

# set defaults from ./configure invokation
%bcond_without sctp
%bcond_without nss
%bcond_without openssl
%bcond_without zlib
%bcond_without lz4
%bcond_without lzo2
%bcond_without lzma
%bcond_without bzip2
%bcond_with zstd
%bcond_with kronosnetd
%bcond_without libnozzle
%bcond_without runautogen
%bcond_with rpmdebuginfo
%bcond_with overriderpmdebuginfo
%bcond_without installtests

# DWZ crashes when making debuginfos. This workaround is from
# https://github.com/docker/docker/issues/22051
# I got this via https://bugzilla.redhat.com/show_bug.cgi?id=1691946
%global _dwz_low_mem_die_limit 0

%if %{with overriderpmdebuginfo}
%undefine _enable_debug_packages
%endif

%if %{with sctp}
%global buildsctp 1
%endif
%if %{with nss}
%global buildcryptonss 1
%endif
%if %{with openssl}
%global buildcryptoopenssl 1
%endif
%if %{with zlib}
%global buildcompresszlib 1
%endif
%if %{with lz4}
%global buildcompresslz4 1
%endif
%if %{with lzo2}
%global buildcompresslzo2 1
%endif
%if %{with lzma}
%global buildcompresslzma 1
%endif
%if %{with bzip2}
%global buildcompressbzip2 1
%endif
%if %{with zstd}
%global buildcompresszstd 1
%endif
%if %{with libnozzle}
%global buildlibnozzle 1
%endif
%if %{with kronosnetd}
%global buildlibnozzle 1
%global buildkronosnetd 1
%endif
%if %{with runautogen}
%global buildautogen 1
%endif
%if %{with installtests}
%global installtestsuite 1
%endif

# main (empty) package
# http://www.rpm.org/max-rpm/s1-rpm-subpack-spec-file-changes.html

Name: kronosnet
Summary: Multipoint-to-Multipoint VPN daemon
Version: 1.25
Release: 1%{?dist}
License: GPLv2+ and LGPLv2+
URL: http://www.kronosnet.org
Source0: http://www.kronosnet.org/releases/kronosnet-%{version}.tar.gz

# Build dependencies
BuildRequires: gcc
# required to build man pages
BuildRequires: libxml2-devel doxygen
BuildRequires: libqb-devel
%if %{defined buildsctp}
BuildRequires: lksctp-tools-devel
%endif
%if %{defined buildcryptonss}
BuildRequires: nss-devel
%endif
%if %{defined buildcryptoopenssl}
BuildRequires: openssl-devel
%endif
%if %{defined buildcompresszlib}
BuildRequires: zlib-devel
%endif
%if %{defined buildcompresslz4}
BuildRequires: lz4-devel
%endif
%if %{defined buildcompresslzo2}
BuildRequires: lzo-devel
%endif
%if %{defined buildcompresslzma}
BuildRequires: xz-devel
%endif
%if %{defined buildcompressbzip2}
BuildRequires: bzip2-devel
%endif
%if %{defined buildcompresszstd}
BuildRequires: libzstd-devel
%endif
%if %{defined buildkronosnetd}
BuildRequires: systemd
BuildRequires: pam-devel
%endif
%if %{defined buildlibnozzle}
BuildRequires: libnl3-devel
%endif
%if %{defined buildautogen}
BuildRequires: automake
BuildRequires: libtool
BuildRequires: autoconf
%endif

%prep
%setup -q -n %{name}-%{version}

%build
%if %{defined buildautogen}
    ./autogen.sh
%endif

%{configure} \
%if %{defined buildsctp}
	--enable-libknet-sctp \
%else
	--disable-libknet-sctp \
%endif
%if %{defined buildcryptonss}
	--enable-crypto-nss \
%else
	--disable-crypto-nss \
%endif
%if %{defined buildcryptoopenssl}
	--enable-crypto-openssl \
%else
	--disable-crypto-openssl \
%endif
%if %{defined buildcompresszlib}
	--enable-compress-zlib \
%else
	--disable-compress-zlib \
%endif
%if %{defined buildcompresslz4}
	--enable-compress-lz4 \
%else
	--disable-compress-lz4 \
%endif
%if %{defined buildcompresslzo2}
	--enable-compress-lzo2 \
%else
	--disable-compress-lzo2 \
%endif
%if %{defined buildcompresslzma}
	--enable-compress-lzma \
%else
	--disable-compress-lzma \
%endif
%if %{defined buildcompresszstd}
	--enable-compress-zstd \
%else
	--disable-compress-zstd \
%endif
%if %{defined buildkronosnetd}
	--enable-kronosnetd \
%endif
%if %{defined buildlibnozzle}
	--enable-libnozzle \
%endif
%if %{defined installtestsuite}
	--enable-install-tests \
%else
	--disable-install-tests \
%endif
	--with-initdefaultdir=%{_sysconfdir}/sysconfig/ \
	--with-systemddir=%{_unitdir}

make %{_smp_mflags}

%install
make install DESTDIR=%{buildroot}

# tree cleanup
# remove static libraries
find %{buildroot} -name "*.a" -exec rm {} \;
# remove libtools leftovers
find %{buildroot} -name "*.la" -exec rm {} \;

# handle systemd vs init script
# remove init scripts
rm -rf %{buildroot}/etc/init.d

# remove docs
rm -rf %{buildroot}/usr/share/doc/kronosnet

# Disabled because of concern that the testsuite does not play nice with the 
# network loopback interface. Upstream has a comprehensive CI/CD system which
# tests different versions of Fedora and should be very safe. In the unlikely
# event of bugs, we should probably avoid DoS´ing the fedora builders by 
# generating unwanted traffic.
#%check

# main empty package
%description
kronosnet source

%if %{defined buildkronosnetd}
## Runtime and subpackages section
%package -n kronosnetd
Summary: Multipoint-to-Multipoint VPN daemon
License: GPLv2+
Requires(post): shadow-utils
Requires: pam, /etc/pam.d/passwd
%{?systemd_requires}

%description -n kronosnetd
The kronosnet daemon is a bridge between kronosnet switching engine
and kernel network tap devices, to create and administer a
distributed LAN over multipoint-to-multipoint VPNs.
 
The daemon does a poor attempt to provide a configure UI similar
to other known network devices/tools (Cisco, quagga).
Beside looking horrific, it allows runtime changes and
reconfiguration of the kronosnet(s) without daemon reload
or service disruption.

%post -n kronosnetd
%systemd_post kronosnetd.service
getent group kronosnetadm >/dev/null || groupadd --force kronosnetadm

%postun -n kronosnetd
%systemd_postun kronosnetd.service

%preun -n kronosnetd
%systemd_preun kronosnetd.service

%files -n kronosnetd
%license COPYING.* COPYRIGHT 
%dir %{_sysconfdir}/kronosnet
%dir %{_sysconfdir}/kronosnet/*
%config(noreplace) %{_sysconfdir}/sysconfig/kronosnetd
%config(noreplace) %{_sysconfdir}/pam.d/kronosnetd
%config(noreplace) %{_sysconfdir}/logrotate.d/kronosnetd
%{_unitdir}/kronosnetd.service
%{_sbindir}/*
%{_mandir}/man8/*
%endif

%if %{defined buildlibnozzle}
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

%ldconfig_scriptlets -n libnozzle1

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
%endif

%package -n libknet1
Summary: Kronosnet core switching implementation (protocol v1)
License: LGPLv2+
BuildRequires: libqb-devel
BuildRequires: doxygen

%description -n libknet1
Kronosnet, often referred to as knet, is a network abstraction layer 
designed for High Availability use cases, where redundancy, security, 
fault tolerance and fast fail-over are the core requirements of your 
application.

The whole kronosnet core is implemented in this library.
Please refer to https://kronosnet.org/ for further  information.

%files -n libknet1
%license COPYING.* COPYRIGHT
%{_libdir}/libknet.so.*
%dir %{_libdir}/kronosnet

%ldconfig_scriptlets -n libknet1

%package -n libknet1-devel
Summary: Kronosnet core switching implementation (developer files)
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}
Requires: pkgconfig

%description -n libknet1-devel
The whole kronosnet core is implemented in this library.
Please refer to the not-yet-existing documentation for further
information. 

# libknet.pc leading to pkgconfig(libknet) automatic virtual provides,
# like other files, is not explicitly versioned in the name like the
# subpackages are -- intention of doing so for subpackage names is
# to ease the cross-checking the compatibility of the remote clients
# interchanging data using this network communication library, as
# the number denotes the protocol version (providing multiple
# protocol versions in parallel is not planned).
%files -n libknet1-devel
%{_libdir}/libknet.so
%{_includedir}/libknet.h
%{_libdir}/pkgconfig/libknet.pc
%{_mandir}/man3/*.3.gz

%if %{defined buildcryptonss}
%package -n libknet1-crypto-nss-plugin
Summary: Libknet1 nss support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-crypto-nss-plugin
NSS crypto support for libknet1.

%files -n libknet1-crypto-nss-plugin
%{_libdir}/kronosnet/crypto_nss.so
%endif

%if %{defined buildcryptoopenssl}
%package -n libknet1-crypto-openssl-plugin
Summary: Libknet1 openssl support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-crypto-openssl-plugin
OpenSSL crypto support for libknet1.

%files -n libknet1-crypto-openssl-plugin
%{_libdir}/kronosnet/crypto_openssl.so
%endif

%if %{defined buildcompresszlib}
%package -n libknet1-compress-zlib-plugin
Summary: Libknet1 zlib support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-compress-zlib-plugin
zlib compression support for libknet1.

%files -n libknet1-compress-zlib-plugin
%{_libdir}/kronosnet/compress_zlib.so
%endif
%if %{defined buildcompresslz4}
%package -n libknet1-compress-lz4-plugin
Summary: Libknet1 lz4 and lz4hc support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-compress-lz4-plugin
lz4 and lz4hc compression support for libknet1.

%files -n libknet1-compress-lz4-plugin
%{_libdir}/kronosnet/compress_lz4.so
%{_libdir}/kronosnet/compress_lz4hc.so
%endif

%if %{defined buildcompresslzo2}
%package -n libknet1-compress-lzo2-plugin
Summary: Libknet1 lzo2 support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-compress-lzo2-plugin
lzo2 compression support for libknet1.

%files -n libknet1-compress-lzo2-plugin
%{_libdir}/kronosnet/compress_lzo2.so
%endif

%if %{defined buildcompresslzma}
%package -n libknet1-compress-lzma-plugin
Summary: Libknet1 lzma support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-compress-lzma-plugin
lzma compression support for libknet1.

%files -n libknet1-compress-lzma-plugin
%{_libdir}/kronosnet/compress_lzma.so
%endif

%if %{defined buildcompressbzip2}
%package -n libknet1-compress-bzip2-plugin
Summary: Libknet1 bzip2 support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-compress-bzip2-plugin
bzip2 compression support for libknet1.

%files -n libknet1-compress-bzip2-plugin
%{_libdir}/kronosnet/compress_bzip2.so
%endif

%if %{defined buildcompresszstd}
%package -n libknet1-compress-zstd-plugin
Summary: Libknet1 zstd support
License: LGPLv2+
Requires: libknet1%{_isa} = %{version}-%{release}

%description -n libknet1-compress-zstd-plugin
zstd compression support for libknet1.

%files -n libknet1-compress-zstd-plugin
%{_libdir}/kronosnet/compress_zstd.so
%endif

%package -n libknet1-crypto-plugins-all
Summary: Libknet1 crypto plugins meta package
License: LGPLv2+
%if %{defined buildcryptonss}
Requires: libknet1-crypto-nss-plugin%{_isa} = %{version}-%{release}
%endif
%if %{defined buildcryptoopenssl}
Requires: libknet1-crypto-openssl-plugin%{_isa} = %{version}-%{release}
%endif

%description -n libknet1-crypto-plugins-all
meta package to install all of libknet1 crypto plugins

%files -n libknet1-crypto-plugins-all

%package -n libknet1-compress-plugins-all
Summary: Libknet1 compress plugins meta package
License: LGPLv2+
%if %{defined buildcompresszlib}
Requires: libknet1-compress-zlib-plugin%{_isa} = %{version}-%{release}
%endif
%if %{defined buildcompresslz4}
Requires: libknet1-compress-lz4-plugin%{_isa} = %{version}-%{release}
%endif
%if %{defined buildcompresslzo2}
Requires: libknet1-compress-lzo2-plugin%{_isa} = %{version}-%{release}
%endif
%if %{defined buildcompresslzma}
Requires: libknet1-compress-lzma-plugin%{_isa} = %{version}-%{release}
%endif
%if %{defined buildcompressbzip2}
Requires: libknet1-compress-bzip2-plugin%{_isa} = %{version}-%{release}
%endif
%if %{defined buildcompresszstd}
Requires: libknet1-compress-zstd-plugin%{_isa} = %{version}-%{release}
%endif

%description -n libknet1-compress-plugins-all
meta package to install all of libknet1 compress plugins

%files -n libknet1-compress-plugins-all

%package -n libknet1-plugins-all
Summary: Libknet1 plugins meta package
License: LGPLv2+
Requires: libknet1-compress-plugins-all%{_isa} = %{version}-%{release}
Requires: libknet1-crypto-plugins-all%{_isa} = %{version}-%{release}

%description -n libknet1-plugins-all
meta package to install all of libknet1 plugins

%files -n libknet1-plugins-all

%if %{with installtests}
%package -n kronosnet-tests
Group: System Environment/Libraries
Summary: kronosnet test suite
Requires: libknet1 = %{version}-%{release}
Requires: libnozzle1%{_isa} = %{version}-%{release}

%description -n kronosnet-tests
 this package contains the libknet test suite

%files -n kronosnet-tests
%defattr(-,root,root,-)
%{_libdir}/kronosnet/tests/*
%endif

%if %{with rpmdebuginfo}
# This is left over from upstream.
%debug_package
%endif

%changelog
* Mon Jan 16 2023 Christine Caulfield <ccaulfie@redhat.com> - 1.25-1
  Rebase to 1.25 for PMTUd fixes
  Resolves: rhbz#2161172

  * Wed Jul 27 2022 Christine Caulfield <ccaulfie@redhat.com> - 1.24-2
  Don't run nozzle_up_down tests, as they don't work in RH CI
  Resolves: rhbz#2024095

* Wed Jul 27 2022 Christine Caulfield <ccaulfie@redhat.com> - 1.24-1
  Rebase to 1.24
  Resolves: rhbz#2024095

* Thu Sep 16 2021 Christine Caulfield <ccaulfie@redhat.com> - 1.22-1
  Rebase to 1.22
  Resolves: rhbz#1999976

* Wed Sep 23 2020 Christine Caulfield <ccaulfie@redhat.com> - 1.18-1
  Rebase to 1.18
  Resolves: rhbz#1855301

* Wed May  6 2020 Christine Caulfield <ccaulfie@redhat.com> - 1.16-1
  Rebase to 1.16
  Resolves: rhbz#1796503

* Wed Apr 15 2020 Christine Caulfield <ccaulfie@redhat.com> - 1.15-1
  Rebase to 1.15
  Resolves: rhbz#1796503

* Thu Oct 17 2019 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.10-4
  Disable fun_pmtud_crypto_test as it can take several hours to run
  Resolves: rhbz#1736872

* Wed Oct 16 2019 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.10-3
  PMTUd: Fix MTU calculation when using crypto
  Resolves: rhbz#1736872
  host: Fix defrag buffer reclaim logic that could cause delivery
        of corrupted data
  ResolveS: rhbz#1761711

* Wed Oct 16 2019 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.10-2
  link: Fix memory corruption when too many up/down events are recorded
  Resolves: rhbz#1753517

* Wed Jun 12 2019 Christine Caulfield <ccaulfie@redhat.com> - 1.10-1
  Rebase to 1.10 for ACL support
  Resolves: rhbz#1688880

* Tue May 21 2019 Christine Caulfield <ccaulfie@redhat.com> - 1.9-3
  Fix kronosnet-tests dependancies and add workaround for dwz crash
  Resolves: rhbz#1688880

* Tue May 14 2019 Christine Caulfield <ccaulfie@redhat.com> - 1.9-2
  add some covscan fixes
  Resolves: rhbz#1688880

* Tue May 14 2019 Christine Caulfield <ccaulfie@redhat.com> - 1.9-1
  Rebase to knet 1.9
  Resolves: rhbz#1688880

* Thu Mar 28 2019 Christine Caulfield <ccaulfie@redhat.com> - 1.4-5
  link: Check address families on a link always match
  Resolves: rhbz#1691419

* Thu Mar 14 2019 Christine Caulfield <ccaulfie@redhat.com> - 1.4-4
  Add Gating tests
  Resolves: rhbz#1682128

* Fri Dec 14 2018 Christine Caulfield <ccaulfie@redhat.com> - 1.4-3
  Don't spin if we get EPERM from sendmsg - iptables can cause this
  Resolves: rhbz#1658301

* Fri Oct 19 2018 Christine Caulfield <ccaulfie@redhat.com> - 1.4-2
  Don't close the loopback link when all the 'real' nodes are down
  Resolves: rhbz1640619

* Tue Aug  7 2018 Christine Caulfield <ccaulfie@redhat.com> - 1.4-1
- Rebase to v1.4

* Tue May 22 2018 Christine Caulfield <ccaulfie@redhat.com> - 1.3-1
- Rebase to v1.3

* Tue Apr 10 2018 Christine Caulfield <ccaulfie@redhat.com> - 1.1-9
- Rebase from Fedora

* Fri Mar 09 2018 Madison Kelly <mkelly@alteeve.ca> - 1.1-8
- Changed pkgconfig() to normal package names to help avoid the wrong
  package being pulled in to satisfy dependencies.

* Wed Mar 07 2018 Madison Kelly <mkelly@alteeve.ca> - 1.1-7
- Moved the comment back above '%%files -n libknet1-devel'.
- Added comment to '%%debug_package'.

* Wed Mar 07 2018 Madison Kelly <mkelly@alteeve.ca> - 1.1-6
- Added a version requirement to lz4 to deal with koji pulling in the
  wrong package.

* Tue Mar 06 2018 Madison Kelly <mkelly@alteeve.ca> - 1.1-5
- Updated ldconfig scriptlet calls.
- Moved the debug_package leading comment.

* Sun Mar 04 2018 Madison Kelly <mkelly@alteeve.ca> - 1.1-4
- Removed leading spaces from descriptions.
- Added the (commented out) %%check tests.
- Updated the changelog macro references to have two percent signs.
- Dropped the redundant libknet1-devel license files.
- Changed 'GPLv2+ + LGPLv2+' to 'GPLv2+ and LGPLv2+'.
- Updated %%ldconfig_scriptlets call.
- Clarified the kronosnet protocol version in the summary. 

* Mon Feb 26 2018 Madison Kelly <mkelly@alteeve.ca> - 1.1-3
- Fixed the changelog to not have the full macro names.

* Sun Feb 25 2018 Madison Kelly <mkelly@alteeve.ca> - 1.1-2
- Moved the 'BuildRequires: systemd' to be conditional with kronostnetd.

* Sun Feb 25 2018 Madison Kelly <mkelly@alteeve.ca> - 1.1-1
- Rerolled for 1.1 upstream release.
- Removed the (no longer needed) gcc8-fixes.patch
- Added the new doxygen and libqb-devel buildrequires for libknetd.

