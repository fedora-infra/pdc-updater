%{!?_licensedir: %global license %%doc}

%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2:        %global __python2 /usr/bin/python2}
%{!?python2_sitelib:  %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

Name:               pdc-updater
Version:            0.1.1
Release:            1%{?dist}
Summary:            Update the product definition center in response to fedmsg

Group:              Development/Libraries
License:            LGPLv2+
URL:                http://pypi.python.org/pypi/pdc-updater
Source0:            https://pypi.python.org/packages/source/p/%{name}/%{name}-%{version}.tar.gz
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

%description
Fedmsg consumer that listens to activity on the Fedora message bus, and updates
the Product Definition Center database in response.

%prep
%setup -q -n %{name}-%{version}

# Remove bundled egg-info in case it exists
rm -rf %{name}.egg-info

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
* Tue Jan 19 2016 Ralph Bean <rbean@redhat.com> - 0.1.1-1
- Bugfix release.

* Tue Jan 12 2016 Ralph Bean <rbean@redhat.com> - 0.1.0-1
- Getting ready for staging deployment.

* Wed Nov 18 2015 Ralph Bean <rbean@redhat.com> - 0.0.1-1
- The dawn of time.
