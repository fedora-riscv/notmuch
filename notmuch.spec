%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name: notmuch
Version: 0.11.1
Release: 1%{?dist}
Summary: System for indexing, searching, and tagging email
Group: Applications/Internet
License: GPLv3+
URL: http://notmuchmail.org/
Source0: http://notmuchmail.org/releases/notmuch-%{version}.tar.gz
Patch0: notmuch-0.6.1-gmime.patch
BuildRequires: xapian-core-devel
BuildRequires: gmime-devel
BuildRequires: libtalloc-devel
BuildRequires: zlib-devel
BuildRequires: emacs-el
BuildRequires: emacs-nox

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

%package devel
Summary: Development libraries and header files for the Notmuch library
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}

%description devel
Notmuch-devel contains the development libraries and header files for
Notmuch email program.  These libraries and header files are
necessary if you plan to do development using Notmuch.

Install notmuch-devel if you are developing C programs which will use the
Notmuch library.  You'll also need to install the notmuch package.

%package -n emacs-notmuch
Summary: Not much support for Emacs
Group: Applications/Editors
BuildArch: noarch
Requires: %{name} = %{version}-%{release}, emacs(bin) >= %{_emacs_version}

%description -n emacs-notmuch
%{summary}.

%package -n emacs-notmuch-el
Summary: Elisp source files for Not much support for Emacs
Group: Applications/Editors
BuildArch: noarch
Requires: emacs-notmuch = %{version}-%{release}

%description -n emacs-notmuch-el
%{summary}.

%package -n python-notmuch
Summary: Python bindings for notmuch
Group: Development/Libraries
BuildArch: noarch
Requires: %{name} = %{version}-%{release}
BuildRequires: python-devel

%description -n python-notmuch
%{summary}.

%prep
%setup -q
%patch0 -p1 -b .gmime

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

%install
make install DESTDIR=%{buildroot}

# Enable dynamic library stripping.
find %{buildroot}%{_libdir} -name *.so* -exec chmod 755 {} \;

# Install the python bindings and documentation
pushd bindings/python
    python setup.py install -O1 --skip-build --root %{buildroot}
popd

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%doc AUTHORS COPYING COPYING-GPL-3 INSTALL README TODO
%{_sysconfdir}/bash_completion.d/notmuch
%{_datadir}/zsh/functions/Completion/Unix/_notmuch
%{_bindir}/notmuch
%{_mandir}/man1/notmuch.1*
%{_libdir}/libnotmuch.so.2*

%files devel
%{_libdir}/libnotmuch.so
%{_includedir}/*

%files -n emacs-notmuch
%{_emacs_sitelispdir}/*.elc
%{_emacs_sitelispdir}/notmuch-logo.png

%files -n emacs-notmuch-el
%{_emacs_sitelispdir}/*.el

%files -n python-notmuch
%doc bindings/python/README
%{python_sitelib}/*

%changelog
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
