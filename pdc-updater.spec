Name:               pdc-updater
Version:            0.4.0
Release:            1%{?dist}
Summary:            Update the product definition center in response to fedmsg

License:            LGPLv2+
URL:                https://pypi.io/project/pdc-updater
Source0:            https://pypi.io/packages/source/p/%{name}/%{name}-%{version}.tar.gz
BuildArch:          noarch

BuildRequires:      python2-devel
BuildRequires:      python-setuptools

BuildRequires:      fedmsg
BuildRequires:      python-fedmsg-commands
BuildRequires:      python-fedmsg-consumers
BuildRequires:      python-requests
BuildRequires:      python-dogpile-cache
BuildRequires:      python-fedora
BuildRequires:      packagedb-cli
BuildRequires:      pdc-client

# For the tests
BuildRequires:      python-nose
BuildRequires:      python-vcrpy
BuildRequires:      python-mock

Requires:           fedmsg
Requires:           python-fedmsg-commands
Requires:           python-fedmsg-consumers
Requires:           python-requests
Requires:           python-dogpile-cache
Requires:           python-fedora
Requires:           packagedb-cli
Requires:           pdc-client

# For runtime
Requires:           fedmsg-hub

%{?python_provide:%python_provide python2-%name}

%description
Fedmsg consumer that listens to activity on the Fedora message bus, and updates
the Product Definition Center database in response.

%prep
%setup -q -n %{name}-%{version}

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --skip-build --root=%{buildroot}

# setuptools installs these, but we don't want them.
rm -rf %{buildroot}%{python2_sitelib}/tests/

%check
# The tests require network, but we mock that with vcr
PYTHONPATH=. nosetests -v

%files
%doc README.rst
%license LICENSE
%{python2_sitelib}/pdcupdater/
%{python2_sitelib}/pdc_updater-%{version}*
%{_bindir}/pdc-updater-retry
%{_bindir}/pdc-updater-audit
%{_bindir}/pdc-updater-initialize

%changelog
* Thu Dec 01 2016 Ralph Bean <rbean@redhat.com> - 0.4.0-1
- new version
- Re-enable tests.
- Remove unnecessary macros and fields as per review.

* Tue Sep 27 2016 Ralph Bean <rbean@redhat.com> - 0.3.1-1
- new version

* Tue Sep 27 2016 Ralph Bean <rbean@redhat.com> - 0.3.0-1
- new version

* Thu Feb 25 2016 Ralph Bean <rbean@redhat.com> - 0.2.4-1
- new version

* Thu Jan 28 2016 Ralph Bean <rbean@redhat.com> - 0.2.3-1
- new version

* Wed Jan 27 2016 Ralph Bean <rbean@redhat.com> - 0.2.2-1
- new version

* Tue Jan 26 2016 Ralph Bean <rbean@redhat.com> - 0.2.1-1
- new version

* Tue Jan 26 2016 Ralph Bean <rbean@redhat.com> - 0.2.0-1
- new version

* Tue Jan 19 2016 Ralph Bean <rbean@redhat.com> - 0.1.1-1
- Bugfix release.

* Tue Jan 12 2016 Ralph Bean <rbean@redhat.com> - 0.1.0-1
- Getting ready for staging deployment.

* Wed Nov 18 2015 Ralph Bean <rbean@redhat.com> - 0.0.1-1
- The dawn of time.
