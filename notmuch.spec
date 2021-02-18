%if 0%{?fedora}
%global with_python3legacy 1
%global with_python3CFFI 1
%endif

%if 0%{?fedora} <= 29
%global with_python2 1
%endif

%if 0%{?rhel} && 0%{?rhel} <= 7
%global with_python2 1
%endif

%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

# build python 3 modules with python 3 ;)
%if 0%{?with_python3legacy} || 0%{?with_python3CFFI}
%global with_python3 1
%endif

Name:           notmuch
Version:        0.31.4
Release:        1%{?dist}
Summary:        System for indexing, searching, and tagging email
License:        GPLv3+
URL:            https://notmuchmail.org/
Source0:        https://notmuchmail.org/releases/notmuch-%{version}.tar.xz
Source1:        https://notmuchmail.org/releases/notmuch-%{version}.tar.xz.asc
# Imported from public key servers; author provides no fingerprint!
Source2:        gpgkey-7A18807F100A4570C59684207E4E65C8720B706B.gpg

# These should be removed in Fedora 26
Obsoletes:      notmuch-deliver < 0.19-5
Provides:       notmuch-deliver >= 0.19-5

BuildRequires:  make
BuildRequires:  bash-completion
BuildRequires:  emacs
BuildRequires:  emacs-el
BuildRequires:  emacs-nox
Buildrequires:  gcc gcc-c++
BuildRequires:  glib libtool
BuildRequires:  doxygen
BuildRequires:  texinfo
BuildRequires:  gnupg2
BuildRequires:  gnupg2-smime
%if 0%{?fedora} >= 27
BuildRequires:  gmime30-devel
%else
BuildRequires:  gmime-devel
%endif
BuildRequires:  libtalloc-devel
BuildRequires:  perl-interpreter
BuildRequires:  perl-generators
BuildRequires:  perl-podlators
%if 0%{?with_python2}
BuildRequires:  python2-devel
BuildRequires:  python2-docutils
BuildRequires:  python2-sphinx
%endif
BuildRequires:  ruby-devel
BuildRequires:  xapian-core-devel
BuildRequires:  zlib-devel

%if 0%{?with_python3}
BuildRequires:  python3-devel
BuildRequires:  python3-docutils
BuildRequires:  python3-sphinx
%endif

%if 0%{?with_python3CFFI}
BuildRequires:  python3-setuptools
BuildRequires:  python3-pytest
BuildRequires:  python3-pytest-shutil
BuildRequires:  python3-cffi
%endif

Requires(post): /sbin/install-info
Requires(postun): /sbin/install-info

%description
Fast system for indexing, searching, and tagging email.  Even if you
receive 12000 messages per month or have on the order of millions of
messages that you've been saving for decades, Notmuch will be able to
quickly search all of it.

Notmuch is not much of an email program. It doesn't receive messages
(no POP or IMAP support). It doesn't send messages (no mail composer,
no network code at all). And for what it does do (email search) that
work is provided by an external library, Xapian. So if Notmuch
provides no user interface and Xapian does all the heavy lifting, then
what's left here? Not much.

%package    devel
Summary:    Development libraries and header files for the Notmuch library
Requires:   %{name} = %{version}-%{release}

%description devel
Notmuch-devel contains the development libraries and header files for
Notmuch email program.  These libraries and header files are
necessary if you plan to do development using Notmuch.

Install notmuch-devel if you are developing C programs which will use the
Notmuch library.  You'll also need to install the notmuch package.

%package -n emacs-notmuch
Summary:    Not much support for Emacs
BuildArch:  noarch
Requires:   %{name} = %{version}-%{release}
Requires:   emacs(bin) >= %{_emacs_version}

%description -n emacs-notmuch
%{summary}.

%if 0%{?with_python2}
%package -n python2-notmuch
Summary:    Python2 bindings for notmuch
%{?python_provide:%python_provide python2-notmuch}

Requires:       python2

%description -n python2-notmuch
%{summary}.
%endif

%if 0%{?with_python3legacy}
%package -n python3-notmuch
Summary:    Python3 bindings for notmuch (legacy)
%{?python_provide:%python_provide python3-notmuch}

Requires:       python3

%description -n python3-notmuch
%{summary}.
%endif

%if 0%{?with_python3CFFI}
%package -n python3-notmuch2
Summary:    Python3 bindings for notmuch (cffi)
%{?python_provide:%python_provide python3-notmuch2}

Requires:       python3

%description -n python3-notmuch2
%{summary}.
%endif

%package -n ruby-notmuch
Summary:    Ruby bindings for notmuch
Requires:   %{name} = %{version}-%{release}

%description -n ruby-notmuch
%{summary}.

%package    mutt
Summary:    Notmuch (of a) helper for Mutt
BuildArch:  noarch
Requires:   %{name} = %{version}-%{release}
Requires:   perl(Term::ReadLine::Gnu)

%description mutt
notmuch-mutt provide integration among the Mutt mail user agent and
the Notmuch mail indexer.

%package    vim
Summary:    A Vim plugin for notmuch
Requires:   %{name} = %{version}-%{release}
Requires:   rubygem-mail
Requires:   vim-enhanced
# Required for updating helptags in scriptlets.
Requires(post):    vim-enhanced
Requires(postun):  vim-enhanced

%description vim
notmuch-vim is a Vim plugin that provides a fully usable mail client
interface, utilizing the notmuch framework.

%prep
%{gpgverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
%setup -q

%build
# The %%configure macro cannot be used because notmuch doesn't support
# some arguments the macro adds to the ./configure call.
./configure --prefix=%{_prefix} --sysconfdir=%{_sysconfdir} \
   --libdir=%{_libdir} --mandir=%{_mandir} --includedir=%{_includedir} \
   --emacslispdir=%{_emacs_sitelispdir}
make %{?_smp_mflags} CFLAGS="%{optflags} -fPIC"

# Build the python bindings
pushd bindings/python
    %if 0%{?with_python2}
    %py2_build
    %endif
    %if 0%{?with_python3}
    %py3_build
    %endif
popd

# Build the python cffi bindings
pushd bindings/python-cffi
    %if 0%{?with_python3CFFI}
    %py3_build
    %endif
popd

# Build notmuch-mutt
pushd contrib/notmuch-mutt
    make
popd

%install
make install DESTDIR=%{buildroot}

# Enable dynamic library stripping.
find %{buildroot}%{_libdir} -name *.so* -exec chmod 755 {} \;

# Install the python bindings and documentation
pushd bindings/python
    %if 0%{?with_python2}
    %py2_install
    %endif
    %if 0%{?with_python3legacy}
    %py3_install
    %endif
popd

# Install the python cffi bindings and documentation
pushd bindings/python-cffi
    %if 0%{?with_python3CFFI}
    %py3_install
    %endif
popd

# Install the ruby bindings
pushd bindings/ruby
    make install DESTDIR=%{buildroot}
popd

# Install notmuch-mutt
install -m0755 contrib/notmuch-mutt/notmuch-mutt \
    %{buildroot}%{_bindir}/notmuch-mutt
install -m0644 contrib/notmuch-mutt/notmuch-mutt.1 \
    %{buildroot}%{_mandir}/man1/notmuch-mutt.1

# Install notmuch-vim
pushd vim
    make install DESTDIR=%{buildroot} prefix="%{_datadir}/vim/vimfiles"
popd

rm -f %{buildroot}/%{_datadir}/applications/mimeinfo.cache
rm -f %{buildroot}%{_infodir}/dir

ls -lR %{buildroot}%{_mandir}

%ldconfig_scriptlets

%post
/sbin/install-info %{_infodir}/notmuch.info %{_infodir}/dir ||:

%preun
if [ $1 -eq 0 ]; then
  /sbin/install-info --delete %{_infodir}/notmuch.info %{_infodir}/dir ||:
fi

%post vim
cd %{_datadir}/vim/vimfiles/doc
vim -u NONE -esX -c "helptags ." -c quit

%postun vim
cd %{_datadir}/vim/vimfiles/doc
vim -u NONE -esX -c "helptags ." -c quit

%files
%doc AUTHORS COPYING COPYING-GPL-3 README
%{_datadir}/zsh/site-functions/_notmuch
%{_datadir}/zsh/site-functions/_email-notmuch
%{_datadir}/bash-completion/completions/notmuch
%{_bindir}/notmuch
%{_mandir}/man1/notmuch.1*
%{_mandir}/man1/notmuch-address.1*
%{_mandir}/man1/notmuch-config.1*
%{_mandir}/man1/notmuch-count.1*
%{_mandir}/man1/notmuch-dump.1*
%{_mandir}/man1/notmuch-insert.1*
%{_mandir}/man1/notmuch-new.1*
%{_mandir}/man1/notmuch-reindex.1*
%{_mandir}/man1/notmuch-reply.1*
%{_mandir}/man1/notmuch-restore.1*
%{_mandir}/man1/notmuch-search.1*
%{_mandir}/man1/notmuch-setup.1*
%{_mandir}/man1/notmuch-show.1*
%{_mandir}/man1/notmuch-tag.1*
%{_mandir}/man1/notmuch-compact.1*
%{_mandir}/man5/notmuch*.5*
%{_mandir}/man7/notmuch*.7*
%{_infodir}/*.info*
%{_libdir}/libnotmuch.so.5*

%files devel
%{_libdir}/libnotmuch.so
%{_includedir}/*
%{_mandir}/man3/notmuch*.3*

%files -n emacs-notmuch
%{_emacs_sitelispdir}/*.el
%{_emacs_sitelispdir}/*.elc
%{_emacs_sitelispdir}/notmuch-logo.png
%{_mandir}/man1/notmuch-emacs-mua.1*
%{_bindir}/notmuch-emacs-mua
%{_datadir}/applications/notmuch-emacs-mua.desktop

%if 0%{?with_python2}
%files -n python2-notmuch
%doc bindings/python/README
%{python2_sitelib}/notmuch*
%endif

%if 0%{?with_python3legacy}
%files -n python3-notmuch
%doc bindings/python/README
%{python3_sitelib}/notmuch*
%endif

%if 0%{?with_python3CFFI}
%files -n python3-notmuch2
%{python3_sitearch}/notmuch*
%endif

%files -n ruby-notmuch
%{ruby_vendorarchdir}/*

%files mutt
%{_bindir}/notmuch-mutt
%{_mandir}/man1/notmuch-mutt.1*

%files vim
%{_datadir}/vim/vimfiles/doc/notmuch.txt
%{_datadir}/vim/vimfiles/plugin/notmuch.vim
%{_datadir}/vim/vimfiles/syntax/notmuch-compose.vim
%{_datadir}/vim/vimfiles/syntax/notmuch-folders.vim
%{_datadir}/vim/vimfiles/syntax/notmuch-git-diff.vim
%{_datadir}/vim/vimfiles/syntax/notmuch-search.vim
%{_datadir}/vim/vimfiles/syntax/notmuch-show.vim

%changelog
* Thu Feb 18 2021 Michael J Gruber <mjg@fedoraproject.org> - 0.31.4-1
- rebase with bugfix release

* Thu Feb 11 2021 Michael J Gruber <mjg@fedoraproject.org> - 0.31.3-5
- fix FTBS #927636

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.31.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Jan 06 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 0.31.3-3
- F-34: rebuild against ruby 3.0

* Fri Dec 25 18:27:23 CET 2020 Michael J Gruber <mjg@fedoraproject.org> - 0.31.3-2
- drop upstream patch

* Fri Dec 25 18:11:21 CET 2020 Michael J Gruber <mjg@fedoraproject.org> - 0.31.3-1
- rebase with bugfix release

* Fri Dec 11 2020 Michael J Gruber <mjg@fedoraproject.org> - 0.31.2-5
- fix sphinx race condition in build

* Fri Dec 11 2020 Michael J Gruber <mjg@fedoraproject.org> - 0.31.2-4
- fix new CFFI python bindings (notmuch2)

* Fri Dec 11 2020 Michael J Gruber <mjg@fedoraproject.org> - 0.31.2-3
- ship info doc

* Fri Dec 11 2020 Michael J Gruber <mjg@fedoraproject.org> - 0.31.2-2
- build API doc

* Sun Nov 08 2020 Michael J Gruber <mjg@fedoraproject.org> - 0.31.2-1
- rebase with bugfix release

* Sun Sep 06 2020 Michael J Gruber <mjg@fedoraproject.org> - 0.31-1
- rebase with upstream release 0.31 (#1876170)

* Sun Aug 30 2020 Michael J Gruber <mjg@fedoraproject.org> - 0.31~rc2-1
- rebase with upstream RC

* Wed Aug 19 2020 Michael J Gruber <mjg@fedoraproject.org> - 0.31~rc1-1
- rebase with upstream RC

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.30-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sat Jul 11 2020 Michael J Gruber <mjg@fedoraproject.org> - 0.30-1
- rebase with upstream release 0.30

* Fri Jul 03 2020 Michael J Gruber <mjg@fedoraproject.org> - 0.30~rc3-1
- rebase with upstream RC
- reenable signature verification which was missing in rc2
- do not track the signature file in git (but do track the keyring) as per PG

* Thu Jun 25 2020 Michael J Gruber <mjg@fedoraproject.org> - 0.30~rc2-1
- rebase with upstream RC
- build new default (CFFI) python module but keep legacy for now

* Tue May 26 2020 Miro Hrončok <mhroncok@redhat.com> - 0.29.3-4
- Rebuilt for Python 3.9

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.29.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sat Jan 18 2020 Mamoru TASAKA <mtasaka@fedoraproject.org> - 0.29.3-2
- F-32: rebuild against ruby27

* Wed Nov 27 2019 Michael J Gruber <mjg@fedoraproject.org> - 0.29.3-1
- bugfix release (bz #1763420)

* Thu Oct 31 2019 Michael J Gruber <mjg@fedoraproject.org> - 0.29.2-1
- bugfix release

* Thu Oct 03 2019 Miro Hrončok <mhroncok@redhat.com> - 0.29.1-4
- Rebuilt for Python 3.8.0rc1 (#1748018)

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 0.29.1-3
- Rebuilt for Python 3.8

* Thu Jul 25 2019 Michael J Gruber <mjg@fedoraproject.org> - 0.29.1-2
- verify package signature

* Wed Jun 12 2019 Michael J Gruber <mjg@fedoraproject.org> - 0.29.1-1
- Update to 0.29.1

* Fri Jun 07 2019 Michael J Gruber <mjg@fedoraproject.org> - 0.29-1
- Update to 0.29

* Mon May 06 2019 Michael J Gruber <mjg@fedoraproject.org> - 0.28.4-1
- Bugfix release 0.28.4

* Thu Mar 07 2019 Michael J Gruber <mjg@fedoraproject.org> - 0.28.3-1
- Bugfix release 0.28.3

* Wed Feb 20 2019 Michael J Gruber <mjg@fedoraproject.org> - 0.28.2-1
- Update to 0.28.2

* Tue Feb 05 2019 Michael J Gruber <mjg@fedoraproject.org> - 0.28.1-1
- Update to 0.28.1

* Tue Feb 05 2019 Michael J Gruber <mjg@fedoraproject.org> - 0.27-7
- Switch to python3 only for Fedora 30 and above

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.27-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Jan 21 2019 Mamoru TASAKA <mtasaka@fedoraproject.org> - 0.27-5
- F-30: rebuild against ruby26

* Mon Jul 16 2018 Michael J Gruber <mjg@fedoraproject.org> - 0.27-4
- BR gcc gcc-c++

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.27-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 0.27-2
- Rebuilt for Python 3.7

* Wed Jun 13 2018 Michael J Gruber <mjg@fedoraproject.org> - 0.27-1
- new upstream version

* Sat May 26 2018 Dan Čermák <dan.cermak@cgc-instruments.com> - 0.26.2-0
- new upstream version

* Thu Feb 08 2018 Iryna Shcherbina <ishcherb@redhat.com> - 0.25-6
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.25-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Jan 20 2018 Björn Esser <besser82@fedoraproject.org> - 0.25-4
- Rebuilt for switch to libxcrypt

* Fri Jan 05 2018 Mamoru TASAKA <mtasaka@fedoraproject.org> - 0.25-3
- F-28: rebuild for ruby25

* Fri Sep 08 2017 Kalev Lember <klember@redhat.com> - 0.25-2
- Switch to gmime 3.0 on F27+

* Mon Aug 21 2017 Gonéri Le Bouder <goneri@redhat.com> - 0.25-0
- new upstream version

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.24.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.24.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jun 01 2017 Ralph Bean <rbean@redhat.com> - 0.24.2-1
- new version

* Tue Apr 04 2017 Ralph Bean <rbean@redhat.com> - 0.24.1-1
- new version

* Mon Mar 13 2017 Ralph Bean <rbean@redhat.com> - 0.24-1
- new version

* Thu Mar 02 2017 Ralph Bean <rbean@redhat.com> - 0.23.7-1
- new version

* Tue Feb 28 2017 Ralph Bean <rbean@redhat.com> - 0.23.6-1
- new version

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.23.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jan 12 2017 Vít Ondruch <vondruch@redhat.com> - 0.23.5-2
- Rebuilt for https://fedoraproject.org/wiki/Changes/Ruby_2.4

* Mon Jan 09 2017 Ralph Bean <rbean@redhat.com> - 0.23.5-1
- new version

* Mon Dec 26 2016 Peter Robinson <pbrobinson@fedoraproject.org> 0.23.3-3
- Rebuild (xapian 1.4)

* Mon Dec 19 2016 Miro Hrončok <mhroncok@redhat.com> - 0.23.3-2
- Rebuild for Python 3.6

* Wed Nov 30 2016 Ralph Bean <rbean@redhat.com> - 0.23.3-1
- new version

* Mon Oct 24 2016 Ralph Bean <rbean@redhat.com> - 0.23.1-1
- new version

* Tue Oct 04 2016 Ralph Bean <rbean@redhat.com> - 0.23-1
- new version

* Tue Sep 27 2016 Ralph Bean <rbean@redhat.com> - 0.22.2-1
- Latest upstream.

* Tue Sep 27 2016 Ralph Bean <rbean@redhat.com> - 0.21-6
- Fixed python3 conditional in the files section.

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.21-5
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Mon Apr 04 2016 Ralph Bean <rbean@redhat.com> - 0.21-4
- Modernized python macros and added a python3 subpackage.

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.21-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jan 12 2016 Vít Ondruch <vondruch@redhat.com> - 0.21-2
- Rebuilt for https://fedoraproject.org/wiki/Changes/Ruby_2.3

* Fri Nov 27 2015 Jonathan Underwood <jonathan.underwood@gmail.com> - 0.21-1
- Update to 0.21
- Remove sha1 files - unused
- Ruby bindings are now built by default, so don't build them explicitly (thanks Jan Synáček)
- Add -fPIC to compiler flags

* Wed Sep 16 2015 Jonathan Underwood <jonathan.underwood@gmail.com> - 0.20.2-1
- Update to 0.20.2
- No longer build notmuch-deliver (no longer shipped upstream)
- Add python-sphinx to BuildRequires so man pages are built

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.19-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 0.19-3
- Rebuilt for GCC 5 C++11 ABI change

* Sat Jan 17 2015 Mamoru TASAKA <mtasaka@fedoraproject.org> - 0.19-2
- Rebuild for https://fedoraproject.org/wiki/Changes/Ruby_2.2

* Sat Nov 29 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 0.19-1
- update to upstream release 0.19
- add notmuch-vim subpackage
- fix "self-obsoletion" due to incorrect Provides for emacs-notmuch subpackage
  (and we can remove both Obsoletes and Provides anyway as no longer relevant)
- fix "non-conffile-in-etc /etc/bash_completion.d/notmuch"
- fix "install-file-in-docs /usr/share/doc/notmuch/INSTALL"
- fix "spurious-executable-perm /usr/share/man/man1/notmuch-mutt.1.gz"
- {__python} is deprecated

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.18.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Aug 13 2014 Luke Macken <lmacken@redhat.com> - 0.18.1-3
- Build a ruby-notmuch subpackage (#947571)

* Wed Aug 13 2014 Luke Macken <lmacken@redhat.com> - 0.18.1-2
- Add bash-completion, emacs, and python-docutils to the build requirements

* Mon Jul 28 2014 Luke Macken <lmacken@redhat.com> - 0.18.1-1
- Update to 0.18.1 (#1094701)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.17-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Feb 13 2014 Ralph Bean <rbean@redhat.com> - 0.17-1
- Latest upstream.

* Wed Feb 12 2014 Ralph Bean <rbean@redhat.com> - 0.16-2
- Added install of notmuch-deliver.

* Fri Sep 27 2013 Lars Kellogg-Stedman <lars@redhat.com> - 0.16-1
- Updated to notmuch 0.16.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.13.2-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 0.13.2-6
- Perl 5.18 rebuild

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.13.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Sep 17 2012 Karel Klíč <kklic@redhat.com> - 0.13.2-4
- notmuch-mutt requires perl(Term::Readline::Gnu)

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.13.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jul 13 2012 Karel Klíč <kklic@redhat.com> - 0.13.2-2
- Packaged notmuch-mutt from contrib

* Fri Jul 13 2012 Karel Klíč <kklic@redhat.com> - 0.13.2-1
- Update to the newest release
- Merge emacs-notmuch-el into emacs-el to conform to the packaging
  guidelines

* Wed Mar  7 2012 Karel Klíč <kklic@redhat.com> - 0.11.1-1
- Update to newest release, which fixes CVE-2011-1103

* Mon Jan 30 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0.11-1
- Latest upstream release
- Update patch so it applies

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Oct 20 2011 Luke Macken <lmacken@redhat.com> - 0.9-1
- Latest upstream release

* Tue Aug 09 2011 Luke Macken <lmacken@redhat.com> - 0.6.1-2
- Create a subpackage for the Python bindings

* Thu Jul 28 2011 Karel Klíč <kklic@redhat.com> - 0.6.1-1
- Latest upstream release
- Added -gmime patch to compile with GMime 2.5.x (upstream uses GMime 2.4.x)

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Dec 09 2010 Karel Klic <kklic@redhat.com> - 0.5-3
- Removed local emacs %%globals, as they are not needed

* Thu Nov 25 2010 Karel Klic <kklic@redhat.com> - 0.5-2
- Removed BuildRoot tag
- Removed %%clean section

* Mon Nov 15 2010 Karel Klic <kklic@redhat.com> - 0.5-1
- New upstream release

* Fri Oct 15 2010 Karel Klic <kklic@redhat.com> - 0.3.1-3
- Improved the main package description.
- Various spec file improvements.

* Fri Oct  8 2010 Karel Klic <kklic@redhat.com> - 0.3.1-2
- Added patch that fixes linking on F13+

* Thu Oct  7 2010 Karel Klic <kklic@redhat.com> - 0.3.1-1
- New version
- Splitted notmuch into several packages

* Wed Nov 18 2009 Jeffrey C. Ollie <jeff@ocjtech.us> - 0.0-0.3.306635c2
- First version
