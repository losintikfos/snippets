#!/usr/bin/perl

#  Copyright 2013, Bright Dadson
#
# Permission to use, copy, modify, and/or distribute this software
# for any purpose with or without fee is hereby granted, provided
# that the above copyright notice and this permission notice appear
# in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
# AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

use strict;
use warnings;
use feature ':5.10';

use Tie::File;

use subs qw(sys_call last_line);

# WARNING!!!
# WARNING!!! Tripple check the hard_drive is pointing to the correct mount. And check
# again and again and again. We don't want to loose our data do we? check again.
#
# Word of advice "Always tripple check before you use `rm -rf`. Always - consider
# using `mv` command instead.

my $hard_drive = '/dev/sda';        # Target installation location - Warning! this drive will be formatted.
my $chroot_dir = '/media/ubuntu';
my $minnow_sd  = '/dev/mmcblk0p1';  # Minnow SD Card

my ( $boot_device, $root_device ) = ( $hard_drive . '1', $hard_drive . '2' );
my ( $angstrom_efi_loc, $ubuntu_efi_loc ) = ( '/mnt/angstromefi', '/mnt/ubuntuefi' );
my $mount_check;

my $force = 0;
$force = 1 if ( ( defined $ARGV[0] ) && ( $ARGV[0] eq 'force' ) );

sub last_line {
    my $file = shift;
    return if ( not defined $file ) || ( not -e $file );

    tie my @rows, 'Tie::File', $file, mode => 'O_RDONLY' or die "error: $!\n";
    return $rows[-1];
}

## hande shell events
sub sys_call {
    my @call = @_;

    return if not @call;
    system(@call) == 0 or die "system @call failed: $?";
}

if ( not -e $chroot_dir ) {
    sys_call map eval qq("$_"), qw( mkdir -p  $chroot_dir );
    say "$chroot_dir created";
}
else {
    $mount_check = qx{mount | grep $chroot_dir};

    # Use lazy umount to avoid - mount busy or in use error
    if ( !( $mount_check eq "" ) ) {
        say "Performing umount on $chroot_dir ..";
        sys_call "umount -l $chroot_dir";
    }
    $mount_check = qx{mount | grep $ubuntu_efi_loc};
    sys_call("umount -l $ubuntu_efi_loc") if !( $mount_check eq "" );
}

# Format boot device as ext2 file system and ext4
# on root device
if ($force) {
    sys_call "mkfs.vfat $boot_device";
    sys_call "mkfs.ext4 $root_device ";
}

# Set mount points
sys_call map eval qq("$_"), qw(mkdir -p $chroot_dir)     if ( not -e $chroot_dir );
sys_call map eval qq("$_"), qw(mount $root_device $chroot_dir);
sys_call map eval qq("$_"), qw(mkdir -p $chroot_dir/dev) if ( not -e $chroot_dir . '/dev' );

sys_call map eval qq("$_"), qw(mkdir -p $chroot_dir/proc) if ( not -e $chroot_dir . '/proc' );
sys_call map eval qq("$_"), qw(mkdir -p $chroot_dir/sys)  if ( not -e $chroot_dir . '/sys' );

sys_call map eval qq("$_"), qw(mount -B /dev $chroot_dir/dev);
sys_call map eval qq("$_"), qw(mount -B /dev/pts $chroot_dir/dev/pts);
sys_call map eval qq("$_"), qw(mount -B /sys $chroot_dir/sys);
sys_call map eval qq("$_"), qw(mount -t proc proc $chroot_dir/proc);

if (
    (
           ( not -e $chroot_dir . '/bin' )
        && ( not -e $chroot_dir . '/dev' )
        && ( not -e $chroot_dir . '/home' )
        && ( not -e $chroot_dir . '/lost+found' )
        && ( not -e $chroot_dir . '/mnt' )
        && ( not -e $chroot_dir . '/proc' )
        && ( not -e $chroot_dir . '/run' )
        && ( not -e $chroot_dir . '/selinux' )
        && ( not -e $chroot_dir . '/sys' )
        && ( not -e $chroot_dir . '/usr' )
        && ( not -e $chroot_dir . '/boot' )
        && ( not -e $chroot_dir . '/etc' )
        && ( not -e $chroot_dir . '/lib' )
        && ( not -e $chroot_dir . '/media' )
        && ( not -e $chroot_dir . '/opt' )
        && ( not -e $chroot_dir . '/root' )
        && ( not -e $chroot_dir . '/sbin' )
        && ( not -e $chroot_dir . '/srv' )
        && ( not -e $chroot_dir . '/tmp' )
        && ( not -e $chroot_dir . '/var' )
    )
    || $force
  )
{
    # preparing for debootstrap
    say "Preparing to debootstrap Ubuntu 12.04 LTS Precise..";

    # Download deboootstrap
    my $work_loc = "deb_work";

    sys_call "rm -rf $work_loc" if ( -e $work_loc && $force );
    sys_call map eval qq("$_"), qw(mkdir $work_loc) if ( not -e $work_loc );

    my $deb_file = "debootstrap_1.0.40~ubuntu0.4_all.deb";
    sys_call(
        map eval qq("$_"), qw(wget -P
          $work_loc http://gb.archive.ubuntu.com/ubuntu/pool/main/d/debootstrap/$deb_file)
    ) unless -e "$work_loc/$deb_file";

    # Extract the debootstrap deb file
    sys_call map eval qq("$_"), qw(ar -xf $work_loc/$deb_file) unless ( -e "usr" && -e "control" );

    sys_call( map eval qq("$_"), qw(mv control.tar.gz data.tar.gz debian-binary $work_loc) )
      if ( -e "control.tar.gz" && -e "data.tar.gz" );

    # Extract both control.tar-gz and data.tar.gz
    # say "Extracting debootstrap files..";

    sys_call map eval qq("$_"), qw(tar xzf $work_loc/control.tar.gz)
      unless ( -e "usr" && -e "control" );
    sys_call map eval qq("$_"), qw(tar xzf $work_loc/data.tar.gz)
      unless ( -e "usr" && -e "control" );

    # fire debootstrap
    my $current_loc = qx{pwd};
    $current_loc =~ s/^\s*|\s*$//g;

    $ENV{'DEBOOTSTRAP_DIR'} = $current_loc . '/usr/share/debootstrap';

    my ( $release, $target ) = ( 'precise', $chroot_dir );
    my $mirror      = 'http://uk.archive.ubuntu.com/ubuntu/';
    my $target_arch = 'i386';

    sys_call(
        map eval qq("$_"),
        qw($current_loc/usr/sbin/debootstrap --verbose --extractor=ar --arch $target_arch $release $target $mirror)
    );
}

# set host configuration
my $host_name = 'compute-node-01';
qx{cat > $chroot_dir/etc/hostname <<EOF
$host_name
EOF
};

# set host config
qx{cat > $chroot_dir/etc/hosts <<EOF
127.0.0.1       localhost
127.0.0.1       $host_name

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet    
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
EOF
};

# set network access config
my ( $net_conf, $net_conf_file ) = ( "iface eth0 inet dhcp", "$chroot_dir/etc/network/interfaces" );
qx{echo $net_conf >> $net_conf_file} unless last_line $net_conf_file eq $net_conf;

say "Preparing boot loader..";

# let use the same boot loader shipped with minnow for
# simplicity and save ourselves bit of hustle
if ( not -e $angstrom_efi_loc ) {
    sys_call( map eval qq("$_"), qw(mkdir $angstrom_efi_loc) );
}
else {
    $mount_check = qx{mount | grep $angstrom_efi_loc};
    sys_call("umount -l $angstrom_efi_loc") if !( $mount_check eq "" );
}
sys_call( map eval qq("$_"), qw(mount $minnow_sd $angstrom_efi_loc) );

sys_call("rm -rf $ubuntu_efi_loc") if ( -e $ubuntu_efi_loc && $force );
if ( not -e $ubuntu_efi_loc ) {
    sys_call( map eval qq("$_"), qw(mkdir $ubuntu_efi_loc) );
}
else {
    $mount_check = qx{mount | grep $ubuntu_efi_loc};
    sys_call("umount -l $ubuntu_efi_loc") if !( $mount_check eq "" );
}

sys_call( map eval qq("$_"), qw(mount $boot_device  $ubuntu_efi_loc) );
qx{cp -r $angstrom_efi_loc/* $ubuntu_efi_loc} unless -e $ubuntu_efi_loc . '/EFI';

# preload mmc module
my ( $mod, $mod_file ) = ( "mmc", "$chroot_dir/etc/initramfs-tools/modules" );
qx{echo $mod >> $mod_file} unless last_line $mod_file eq $mod;

#Chrooting
#sys_call(map eval qq("$_"), qw(chroot $chroot_dir /bin/bash));

# Set timezone
sys_call( map eval qq("$_"), qw(cp /usr/share/zoneinfo/Europe/London /etc/localtime) )
  unless -e "/etc/localtime/London";

say "Updating Ubuntu installation..";

# pull ubuntu's current update
#sys_call("chroot $chroot_dir /bin/bash");
#sleep(1);

opendir C_R, "." or die "ERROR: file handle to existing location failed";
chdir($chroot_dir);
chroot '.';

sys_call "ls";
sys_call "apt-get -y dist-upgrade";
sys_call "apt-get install -y --force-yes initramfs-tools";
sys_call
"apt-get install -y --force-yes build-essential linux-image-generic grub-efi-ia32 bash-completion";
sys_call "apt-get install -y --force-yes ssh";

sys_call( map eval qq("$_"), qw(mount $boot_device  mnt) );
qx{cp -r usr/lib/grub/i386-efi mnt/EFI/BOOT/} unless -e "mnt/EFI/BOOT/i386-efi";

# remove root pass for now until your first boot
# please set the password once you've logged in
sys_call "passwd -d root";

say "Configuring boot loader";

# obtain the correct file names for both initrd and vmlinuz
my $initrd = qx{ls boot | grep initrd};
$initrd =~ s/^\s*|\s*$//g;

my $vmlinuz = qx{ls boot | grep vmlinuz};
$vmlinuz =~ s/^\s*|\s*$//g;

# Grub config settings
qx{cat > mnt/EFI/BOOT/grub.cfg <<EOF
# Automatically created by OE
serial --unit=0 --speed=115200 --word=8 --parity=no --stop=1
default=boot
timeout=1

menuentry "Ubuntu 12.04 LTS Precise (i386)" {
insmod part_msdos
insmod ext2
set root='(hd0,msdos2)'
linux /boot/$vmlinuz root=$root_device ro rootwait console=ttyPCH0,115200 console=tty0 vmalloc=256MB snd-hda-intel.enable_msi=0
initrd /boot/$initrd
}
EOF
};

# fstab entry - this ensures boot time mount
qx{cat > etc/fstab <<EOF
# device                                    mount   type options freq passno
$root_device   /       ext4 errors=remount-ro 0 1
#$boot_device   /boot   ext2 defaults   0 1
EOF
};

# just to be sure we have the right sources.list locations
# misc
qx{cat > etc/apt/sources.list <<EOF
# deb cdrom:[Ubuntu-Server 12.04.3 LTS _Precise Pangolin_ - Release i386 (20130820.2)]/ precise main restricted

#deb cdrom:[Ubuntu-Server 12.04.3 LTS _Precise Pangolin_ - Release i386 (20130820.2)]/ precise main restricted

# See http://help.ubuntu.com/community/UpgradeNotes for how to upgrade to
# newer versions of the distribution.
deb http://gb.archive.ubuntu.com/ubuntu/ precise main restricted
deb-src http://gb.archive.ubuntu.com/ubuntu/ precise main restricted

## Major bug fix updates produced after the final release of the
## distribution.
deb http://gb.archive.ubuntu.com/ubuntu/ precise-updates main restricted
deb-src http://gb.archive.ubuntu.com/ubuntu/ precise-updates main restricted

## N.B. software from this repository is ENTIRELY UNSUPPORTED by the Ubuntu
## team. Also, please note that software in universe WILL NOT receive any
## review or updates from the Ubuntu security team.
deb http://gb.archive.ubuntu.com/ubuntu/ precise universe
deb-src http://gb.archive.ubuntu.com/ubuntu/ precise universe
deb http://gb.archive.ubuntu.com/ubuntu/ precise-updates universe
deb-src http://gb.archive.ubuntu.com/ubuntu/ precise-updates universe

## N.B. software from this repository is ENTIRELY UNSUPPORTED by the Ubuntu 
## team, and may not be under a free licence. Please satisfy yourself as to 
## your rights to use the software. Also, please note that software in 
## multiverse WILL NOT receive any review or updates from the Ubuntu
## security team.
deb http://gb.archive.ubuntu.com/ubuntu/ precise multiverse
deb-src http://gb.archive.ubuntu.com/ubuntu/ precise multiverse
deb http://gb.archive.ubuntu.com/ubuntu/ precise-updates multiverse
deb-src http://gb.archive.ubuntu.com/ubuntu/ precise-updates multiverse

## N.B. software from this repository may not have been tested as
## extensively as that contained in the main release, although it includes
## newer versions of some applications which may provide useful features.
## Also, please note that software in backports WILL NOT receive any review
## or updates from the Ubuntu security team.
deb http://gb.archive.ubuntu.com/ubuntu/ precise-backports main restricted universe multiverse
deb-src http://gb.archive.ubuntu.com/ubuntu/ precise-backports main restricted universe multiverse

deb http://security.ubuntu.com/ubuntu precise-security main restricted
deb-src http://security.ubuntu.com/ubuntu precise-security main restricted
deb http://security.ubuntu.com/ubuntu precise-security universe
deb-src http://security.ubuntu.com/ubuntu precise-security universe
deb http://security.ubuntu.com/ubuntu precise-security multiverse
deb-src http://security.ubuntu.com/ubuntu precise-security multiverse

## Uncomment the following two lines to add software from Canonical's
## 'partner' repository.
## This software is not part of Ubuntu, but is offered by Canonical and the
## respective vendors as a service to Ubuntu users.
# deb http://archive.canonical.com/ubuntu precise partner
# deb-src http://archive.canonical.com/ubuntu precise partner

## Uncomment the following two lines to add software from Ubuntu's
## 'extras' repository.
## This software is not part of Ubuntu, but is offered by third-party
## developers who want to ship their latest software.
# deb http://extras.ubuntu.com/ubuntu precise main
# deb-src http://extras.ubuntu.com/ubuntu precise main
EOF
};


# come out of debootstrap environment
chdir(*C_R);

while ( ( stat(".") )[0] != ( stat("..") )[0] or ( stat(".") )[1] != ( stat("..") )[1] ) {
    chdir "..";
}

chroot ".";

say "Ubuntu 12.04 LTS - debootstrapping completed successfully.";

1;

