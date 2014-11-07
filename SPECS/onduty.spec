%global  service_name  onduty
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

Source1:        onduty.service
Source2:        puma.rb

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
rm -rf %{buildroot}
mkdir -p %{buildroot}%{appdir}
mkdir -p %{buildroot}%{tmpdir}
mkdir -p %{buildroot}%{_sysconfdir}/%{name}

%{__install} -p -D -m 0755 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
%{__install} -p -m 0755 %{SOURCE2} %{buildroot}%{_sysconfdir}/%{name}
%{__install} -p -m 0644 %{SOURCE2}  %{buildroot}%{_sysconfdir}/%{name}

pushd %{name}
  mv * .bundle %{buildroot}/%{appdir}
popd
rm -f %{buildroot}%{appdir}log/.gitkeep

%pre
%{_sbindir}/useradd -c "Onduty user" -s /bin/false -r -d %{appdir} %{onduty_user} 2>/dev/null || :
%service_add_pre %{service_name}.service

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
%attr(755,%{onduty_user},%{onduty_group}) %{logdir}
%attr(755,%{onduty_user},%{onduty_group}) %{tmpdir}
%doc
