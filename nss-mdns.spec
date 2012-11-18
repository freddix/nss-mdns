Summary:	Host name resolution via Multicast DNS
Name:		nss-mdns
Version:	0.10
Release:	14
License:	LGPL
Group:		Libraries
Source0:	http://0pointer.de/lennart/projects/nss-mdns/%{name}-%{version}.tar.gz
# Source0-md5:	03938f17646efbb50aa70ba5f99f51d7
Requires(post,preun):	/usr/bin/perl
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
nss-mdns is a plugin for the GNU Name Service Switch (NSS)
functionality of the GNU C Library (glibc) providing host
name resolution via Multicast DNS (aka Zeroconf, aka Apple
Rendezvous, aka Apple Bonjour), effectively allowing name
resolution by common Unix/Linux programs in the ad-hoc
mDNS domain .local.

nss-mdns provides client functionality only, which means
that you have to run a mDNS responder daemon seperately
from nss-mdns if you want to register the local host name
via mDNS.

%prep
%setup -q

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post
/usr/sbin/ldconfig
if [ -f /etc/nsswitch.conf ] ; then
	LANG=C perl -ibak -pe '
	sub insert {
	    my @bits = split(" ", shift);

	    if (grep { $_ eq "mdns4_minimal" || $_ eq "mdns4"
		    || $_ eq "mdns6_minimal" || $_ eq "mdns6"
		    || $_ eq "mdns_minimal" || $_ eq "mdns" } @bits) {
		return join " ", @bits;
	    }

	    return join " ", map {
		$_ eq "dns" ? ("mdns4_minimal", "[NOTFOUND=return]", $_) : $_
	    } @bits;
	}

	s/^(hosts:\s+)(.*)$/$1.insert($2)/e;
	' /etc/nsswitch.conf
fi

%preun
if [ "$1" -eq 0 -a -f /etc/nsswitch.conf ] ; then
	LANG=C perl -ibak -pe '
	my @remove = (
		"mdns4_minimal [NOTFOUND=return]",
		"mdns4_minimal",
		"mdns4",
		"mdns6_minimal [NOTFOUND=return]",
		"mdns6_minimal",
		"mdns6",
		"mdns_minimal [NOTFOUND=return]",
		"mdns_minimal",
		"mdns",
		);
	sub remove {
	    my $s = shift;
	    foreach my $bit (@remove) {
		$s =~ s/\s+\Q$bit\E//g;
	    }
	    return $s;
	}
	s/^(hosts:\s+)(.*)$/$1.remove($2)/e;
	' /etc/nsswitch.conf
fi

%postun	-p /usr/sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc doc/README
%attr(755,root,root) %{_libdir}/libnss*.so.?

