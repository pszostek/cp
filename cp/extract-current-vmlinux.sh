ME=$(readlink -f "$0")
MYPATH=$(dirname "$ME")

$MYPATH/extract-vmlinux.sh /boot/vmlinuz-`uname -r` > /tmp/vmlinux.elf
cp -f /boot/System.map-`uname -r` /tmp/vmlinux.symbols
