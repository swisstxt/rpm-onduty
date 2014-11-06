%global  service_name  onduty-server
%global  onduty_user   onduty
%global  onduty_group  %{onduty_user}

Name:           onduty
Version:        %{ver}
Release:        %{rel}1%{?dist}
Summary:        onduty - oncall alerts
BuildArch:      x86_64
Group:          Application/Internet
License:        commercial
URL:            https://github.com/swisstxt/onduty
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Source0:        onduty.service

BuildRequires: ruby rubygems rubygem-bundler
BuildRequires: gcc libxml2 libxml2-devel libxslt libxslt-devel openssl-devel

Requires: ruby rubygems rubygem-bundler
Requires: libxml2 libxslt

Requires(post):    chkconfig
Requires(preun):   chkconfig, initscripts
Requires(postun):  initscripts

%define git_repo git@github.com:swisstxt/%{name}.git
%define appdir /srv/%{name}
%define cfgdir %{appdir}/config
%define logdir %{appdir}/log
%define tmpdir %{appdir}/tmp

%description
onduty - oncall alerts

%prep
rm -rf %{name}
git clone %{git_repo}
pushd %{name}
  git checkout -q %{version}
  rm -f log/*
  rm -f tmp/*
popd

%build
pushd %{name}
  gem install bundler
  bundle install --deployment --binstubs --without development
popd

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{appdir}
mkdir -p $RPM_BUILD_ROOT/%{tmpdir}

install -p -D -m 0755 %{SOURCE0} \
  %{buildroot}%{%_unitdir}/%{service_name}.service

pushd %{name}
  mv * .bundle $RPM_BUILD_ROOT/%{appdir}
popd
rm -f $RPM_BUILD_ROOT/%{appdir}/log/.gitkeep

%pre
if [ $1 -eq 1 ]; then
  getent group %{onduty_group} > /dev/null || groupadd -r %{onduty_group}
  getent passwd %{onduty_user} > /dev/null || \
    useradd -r -d %{appdir} -g %{onduty_group} \
    -s /sbin/nologin -c "Onduty server" %{onduty_user}
  exit 0
  %service_add_pre %{service_name}.service
fi

%post
if [ $1 == 1 ]; then
  %service_add_post %{service_name}.service
fi

%preun
if [ $1 = 0 ]; then
  %service_add_preun %{service_name}.service
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%{_unitdir}/%{service_name}.service
%defattr(-,root,root,-)
%{appdir}
%doc
