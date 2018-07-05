Name:           cblm
Version:        2.9.4
Release:        5%{?dist}
Summary:        Cheap Bastard Latency Monitor aka Complex Bandwidth LM

License:        GPLv3+
URL:            http://www.digitalgenesis.com/software/cblm/
Source0:        cblm-2.9.4.tar.bz2
Source1:        cblmd-init.d
Patch0:         cblm-c7-patch

BuildRequires:  mariadb-devel
Requires:       mariadb-libs

%description
CBLM is a high performance latency (one-way and round-trip), packet loss and jitter monitoring probe. When run on two or more servers, a full mesh of connections is automatically setup between the probes. The full mesh of connections are used to transmit UDP packets between the probes. Statistics are collected and stored within a MySQL database.

%prep
%setup -q
%patch0 -p1

%build
%configure --with-mysql-lib=/usr/lib64/mysql
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
%make_install

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/{sysconfig,logrotate.d}
cat > $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/cblm << EOF_INIT
# Command-line options for cblm
IFACE=eno1
DBHOST=db.foo.bar:3306
DBNAME=dbname
DBUSER=dbuser
DBPASS=dbpwd
EOF_INIT
chmod 600 $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/cblm

## chkconfig CRUD # FIXME
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/init.d
install -m 755 -p %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/init.d/cblmd

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rsyslog.d
cat > $RPM_BUILD_ROOT%{_sysconfdir}/rsyslog.d/cblmd.conf << EOF_SYSLOG
# copy for admins
:programname, isequal, "cblmd"  /var/log/cblmd.log
EOF_SYSLOG

%post
case "$1" in
   1)
      chkconfig --add cblmd
   ;;
   2)
      chkconfig --del cblmd
      chkconfig --add cblmd
   ;;
esac

%preun
case "$1" in
   0)
      service cblmd stop
      chkconfig --del cblmd
   ;;
   1)
      :
   ;;
esac

## 2.9.4
%files
%doc README AUTHORS COPYING ChangeLog
%doc /usr/share/doc/cblm/*
%config(noreplace) %{_sysconfdir}/sysconfig/cblm
%{_bindir}/*
%{_mandir}/man1/*
%{_sysconfdir}/init.d/*
%{_sysconfdir}/rsyslog.d/*
#%{_unitdir}/cblm.service

## 2.9.5
#%files
#%doc README AUTHORS COPYING ChangeLog
#%doc /usr/share/doc/cblm/*
##%{_datarootdir} /usr/share/doc/cblm/
%config(noreplace) %{_sysconfdir}/sysconfig/cblm
#%{_libdir}/*
#%{_sbindir}/*
#%{_unitdir}/cblm.service
#%{_sysconfdir}/rsyslog.d/*
#%{_mandir}/man1/*
#%{_mandir}/man5/*


%changelog
* Wed Jul 04 2018 Mario Mikocevic <mozgy@t-com.hr> 2.9.4-4
- rework init for old SySV style, systemd will be in 2.9.5 spec
- add rsyslog conf

* Tue Jul 03 2018 Mario Mikocevic <mozgy@t-com.hr> 2.9.4-2
- initd fixes and typos

* Wed Jun 27 2018 Mario Mikocevic <mozgy@t-com.hr> 2.9.4-1
- Initial RPM release
