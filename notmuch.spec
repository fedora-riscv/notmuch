# currently the test suite is flaky
# leave with_tests unset

%if 0%{?fedora} || 0%{?rhel} >= 9
%global with_python3legacy 1
%global with_python3CFFI 1
%endif

%if 0%{?rhel} && 0%{?rhel} <= 8
%global with_python2 1
%endif

# build python 3 modules with python 3 ;)
%if 0%{?with_python3legacy} || 0%{?with_python3CFFI}
%global with_python3 1
%endif

Name:           notmuch
Version:        0.34.2
Release:        %autorelease
Summary:        System for indexing, searching, and tagging email
License:        GPLv3+
URL:            https://notmuchmail.org/
Source0:        https://notmuchmail.org/releases/notmuch-%{version}.tar.xz
Source1:        https://notmuchmail.org/releases/notmuch-%{version}.tar.xz.asc
# Imported from public key servers; author provides no fingerprint!
Source2:        gpgkey-7A18807F100A4570C59684207E4E65C8720B706B.gpg

BuildRequires:  make
BuildRequires:  bash-completion
BuildRequires:  emacs
BuildRequires:  emacs-el
BuildRequires:  emacs-nox
Buildrequires:  gcc gcc-c++
BuildRequires:  libtool
BuildRequires:  doxygen
BuildRequires:  texinfo
BuildRequires:  gnupg2
BuildRequires:  gnupg2-smime
BuildRequires:  gmime30-devel
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
%if 0%{?with_tests}
BuildRequires:  python3-pytest
BuildRequires:  python3-pytest-shutil
%endif
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
Requires:   ruby-%{name} = %{version}-%{release}
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
%autochangelog
