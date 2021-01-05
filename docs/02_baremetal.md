# BareMetal Installation

If you are running debian, please simply run `sudo apt install pmacct`, otherwise follow the steps outline below.

Pleae continue on to the `Running Daemon` section

### Dependencies.

```sh
yum install libpcap-devel pkgconfig libtool autoconf automake make bash libstdc++-devel gcc-c++ 
```

Note, for Centos 8 or greater you need to enable the PowerTools repo to install libpcap-devel.

```sh
yum install dnf-plugins-core
yum config-manager --set-enabled powertools
yum update
```

### Build

Please checkout the code from: https://github.com/pmacct/pmacct.git

```sh
git clone https://github.com/pmacct/pmacct.git
cd pmacct
./autogen.sh
./configure #check-out available configure knobs via ./configure --help
make
sudo make install #with super-user permission
```

## Copy configuration

Please copy the sfacctd.conf or nfacctd.conf to /etc/pmacct.  You'll also need to copy 
the appropriate pretag.map.  These files can be found under the deploy folder.

## Running Daemon

I'm assuming you're only running one daemon per server.  If you are running more than one, you'll need
to update the configuration and ensure all the paths are unique.  

By convention there is 1 config that goes with a pretag map.  You can have as many processes as you 
like as long as the paths don't conflict.

For sflow use:

/usr/local/sbin/sfacctd -f /etc/pmacct/sfacctd.conf

For netflow use:

/usr/local/sbin/nfacctd -f /etc/pmacct/nfacctd.conf
