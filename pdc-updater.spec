%{!?_licensedir: %global license %%doc}

%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2:        %global __python2 /usr/bin/python2}
%{!?python2_sitelib:  %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

Name:               pdc-updater
Version:            0.6.3
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

Requires:           fedmsg

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

%files
%doc README.rst
%license LICENSE
%{python2_sitelib}/pdcupdater/
%{python2_sitelib}/pdcupdater-%{version}*

%changelog
* Wed Nov 18 2015 Ralph Bean <rbean@redhat.com> - 0.0.1-1
- The dawn of time.
