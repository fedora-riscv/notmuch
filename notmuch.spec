%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           notmuch
Version:        0.19
Release:        1%{?dist}
Summary:        System for indexing, searching, and tagging email
Group:          Applications/Internet
License:        GPLv3+
URL:            http://notmuchmail.org/
Source0:        http://notmuchmail.org/releases/notmuch-%{version}.tar.gz
Source1:        http://notmuchmail.org/releases/notmuch-%{version}.tar.gz.sha1
Source2:        http://notmuchmail.org/releases/notmuch-%{version}.tar.gz.sha1.asc
BuildRequires:  bash-completion
BuildRequires:  emacs
BuildRequires:  emacs-el
BuildRequires:  emacs-nox
BuildRequires:  glib libtool
BuildRequires:  gmime-devel
BuildRequires:  libtalloc-devel
BuildRequires:  perl
BuildRequires:  perl-podlators
BuildRequires:  python-docutils
BuildRequires:  python2-devel
BuildRequires:  ruby-devel
BuildRequires:  xapian-core-devel
BuildRequires:  zlib-devel

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
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}

%description devel
Notmuch-devel contains the development libraries and header files for
Notmuch email program.  These libraries and header files are
necessary if you plan to do development using Notmuch.

Install notmuch-devel if you are developing C programs which will use the
Notmuch library.  You'll also need to install the notmuch package.

%package -n emacs-notmuch
Summary:    Not much support for Emacs
Group:      Applications/Editors
BuildArch:  noarch
Requires:   %{name} = %{version}-%{release}
Requires:   emacs(bin) >= %{_emacs_version}
Obsoletes:  emacs-notmuch-el < 0.11.1-2
Provides:   emacs-notmuch-el < 0.11.1-2

%description -n emacs-notmuch
%{summary}.

%package -n python-notmuch
Summary:    Python bindings for notmuch
Group:      Development/Libraries
BuildArch:  noarch
Requires:   %{name} = %{version}-%{release}

%description -n python-notmuch
%{summary}.

%package -n ruby-notmuch
Summary:    Ruby bindings for notmuch
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}

%description -n ruby-notmuch
%{summary}.

%package    mutt
Summary:    Notmuch (of a) helper for Mutt
Group:      Development/Libraries
BuildArch:  noarch
Requires:   %{name} = %{version}-%{release}
Requires:   perl(Term::ReadLine::Gnu)

%description mutt
notmuch-mutt provide integration among the Mutt mail user agent and
the Notmuch mail indexer.

%package    deliver
Summary:    A maildir delivery tool
Group:      Development/Libraries
Requires:   %{name} = %{version}-%{release}
Requires:   glib >= 2.16

%description deliver
notmuch-deliver is a maildir delivery tool for the notmuch mail indexer. It
reads from standard input, delivers the mail to the specified maildir and adds
it to the notmuch database. This is meant as a convenient alternative to
running notmuch new after mail delivery.

%package    vim
Summary:    A Vim plugin for notmuch
Group:      Applications/Editors
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
%setup -q

%build
# The %%configure macro cannot be used because notmuch doesn't support
# some arguments the macro adds to the ./configure call.
./configure --prefix=%{_prefix} --sysconfdir=%{_sysconfdir} \
   --libdir=%{_libdir} --mandir=%{_mandir} --includedir=%{_includedir} \
   --emacslispdir=%{_emacs_sitelispdir}
make %{?_smp_mflags} CFLAGS="%{optflags}"

# Build the python bindings
pushd bindings/python
    python setup.py build
popd

# Build the ruby bindings
pushd bindings/ruby
    ruby extconf.rb --vendor --with-cflags="%{optflags}"
    make %{?_smp_mflags}
popd

# Build notmuch-mutt
pushd contrib/notmuch-mutt
    make
popd

# Build notmuch-deliver
pushd contrib/notmuch-deliver
    ./autogen.sh
    LDFLAGS="-L$(pwd)/../../lib/" CPPFLAGS="-I$(pwd)/../../lib/" ./configure \
       --prefix=%{_prefix} --sysconfdir=%{_sysconfdir} \
       --libdir=%{_libdir} \
       --includedir=%{_includedir} \
       --mandir=%{_mandir}
    make %{?_smp_mflags} CFLAGS="%{optflags}"
popd

%install
make install DESTDIR=%{buildroot}

# Enable dynamic library stripping.
find %{buildroot}%{_libdir} -name *.so* -exec chmod 755 {} \;

# Install the python bindings and documentation
pushd bindings/python
    python setup.py install -O1 --skip-build --root %{buildroot}
popd

# Install the ruby bindings
pushd bindings/ruby
    make install DESTDIR=%{buildroot}
popd

# Install notmuch-mutt
install contrib/notmuch-mutt/notmuch-mutt %{buildroot}%{_bindir}/notmuch-mutt
install contrib/notmuch-mutt/notmuch-mutt.1 %{buildroot}%{_mandir}/man1/notmuch-mutt.1

# Install notmuch-deliver
pushd contrib/notmuch-deliver
    make install DESTDIR=%{buildroot}
popd

# Install notmuch-vim
pushd vim
    make install DESTDIR=%{buildroot} prefix="%{_datadir}/vim/vimfiles"
popd

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%post vim
cd %{_datadir}/vim/vimfiles/doc
vim -u NONE -esX -c "helptags ." -c quit

%postun vim
cd %{_datadir}/vim/vimfiles/doc
vim -u NONE -esX -c "helptags ." -c quit

%files
%doc AUTHORS COPYING COPYING-GPL-3 INSTALL README
%{_sysconfdir}/bash_completion.d/notmuch
%{_datadir}/zsh/functions/Completion/Unix/_notmuch
%{_bindir}/notmuch
%{_mandir}/man1/notmuch.1*
%{_mandir}/man1/notmuch-address.1*
%{_mandir}/man1/notmuch-config.1*
%{_mandir}/man1/notmuch-count.1*
%{_mandir}/man1/notmuch-dump.1*
%{_mandir}/man1/notmuch-insert.1*
%{_mandir}/man1/notmuch-new.1*
%{_mandir}/man1/notmuch-reply.1*
%{_mandir}/man1/notmuch-restore.1*
%{_mandir}/man1/notmuch-search.1*
%{_mandir}/man1/notmuch-setup.1*
%{_mandir}/man1/notmuch-show.1*
%{_mandir}/man1/notmuch-tag.1*
%{_mandir}/man1/notmuch-compact.1*
%{_mandir}/man5/notmuch*.5*
%{_mandir}/man7/notmuch*.7*
%{_libdir}/libnotmuch.so.4*

%files devel
%{_libdir}/libnotmuch.so
%{_includedir}/*

%files -n emacs-notmuch
%{_emacs_sitelispdir}/*.el
%{_emacs_sitelispdir}/*.elc
%{_emacs_sitelispdir}/notmuch-logo.png

%files -n python-notmuch
%doc bindings/python/README
%{python_sitelib}/*

%files -n ruby-notmuch
%{ruby_vendorarchdir}/*

%files mutt
%{_bindir}/notmuch-mutt
%{_mandir}/man1/notmuch-mutt.1*

%files deliver
%{_bindir}/notmuch-deliver
%{_datadir}/doc/notmuch-deliver/README.mkd

%files vim
%{_datadir}/vim/vimfiles/doc/notmuch.txt
%{_datadir}/vim/vimfiles/plugin/notmuch.vim
%{_datadir}/vim/vimfiles/syntax/notmuch-compose.vim
%{_datadir}/vim/vimfiles/syntax/notmuch-folders.vim
%{_datadir}/vim/vimfiles/syntax/notmuch-git-diff.vim
%{_datadir}/vim/vimfiles/syntax/notmuch-search.vim
%{_datadir}/vim/vimfiles/syntax/notmuch-show.vim

%changelog
* Sat Nov 29 2014 Jamie Nguyen <jamielinux@fedoraproject.org> - 0.19-1
- update to upstream release 0.19
- add notmuch-vim subpackage

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
