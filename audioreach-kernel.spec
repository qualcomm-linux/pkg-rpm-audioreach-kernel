%global debug_package %{nil}

Name:           audioreach-kernel
Version:        1.1.0
Release:        1%{?dist}
Summary:        AudioReach out-of-tree Linux kernel drivers

License:        GPL-2.0-only
URL:            https://github.com/qualcomm-linux/pkg-audioreach-kernel
Source0:        https://github.com/qualcomm-linux/pkg-audioreach-kernel/archive/refs/tags/upstream/%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExclusiveArch:  aarch64

%description
AudioReach Kernel provides out-of-tree Linux kernel drivers that enable
communication between the AudioReach signal processing framework running
on an audio DSP and userspace graph service libraries.

These drivers integrate AudioReach with the Linux kernel, allowing control
and data exchange between the host CPU and DSP-based audio processing
pipelines on Qualcomm platforms.

# ── dkms subpackage ───────────────────────────────────────────────────────────
%package dkms
Summary:        AudioReach kernel drivers (DKMS)
Requires:       dkms
Requires(post): dkms
Requires(preun):dkms
Recommends:     kernel-devel

%description dkms
AudioReach kernel drivers packaged for DKMS. Installs the driver source
into /usr/src and automatically builds and installs the audioreach_driver
module for the running kernel (6.18+).

# ── config subpackage ─────────────────────────────────────────────────────────
%package config
Summary:        AudioReach modprobe blacklist and udev rules
BuildArch:      noarch

%description config
Blacklists native ASoC machine drivers that conflict with the AudioReach
kernel driver (Config #2 path), and installs udev rules for AudioReach
character devices.

Install this alongside audioreach-kernel-dkms to activate the AudioReach
DSP audio path on QCS6490 (RB3 Gen2).

# ── dev subpackage ────────────────────────────────────────────────────────────
%package dev
Summary:        Development headers for AudioReach kernel drivers
BuildArch:      noarch

%description dev
Header files required to build userspace applications or kernel modules
that integrate with AudioReach kernel drivers.

# ─────────────────────────────────────────────────────────────────────────────

%prep
%setup -n pkg-audioreach-kernel-upstream-%{version}

%build
# Nothing built here — DKMS builds audioreach_driver.ko on the target at
# install time against the running kernel.

%install
# ── dkms: install source tree + dkms.conf into /usr/src ──────────────────────
install -d %{buildroot}%{_usrsrc}/%{name}-%{version}
cp -r audioreach-driver dsp include ipc Makefile \
    %{buildroot}%{_usrsrc}/%{name}-%{version}/

cat > %{buildroot}%{_usrsrc}/%{name}-%{version}/dkms.conf << 'EOF'
PACKAGE_NAME="audioreach-kernel"
PACKAGE_VERSION="1.1.0"
BUILT_MODULE_NAME[0]="audioreach_driver"
BUILT_MODULE_LOCATION[0]="audioreach-driver"
DEST_MODULE_LOCATION[0]="/extra/audioreach-kernel"
AUTOINSTALL="yes"
BUILD_EXCLUSIVE_KERNEL_MIN="6.18"
MAKE[0]="make -C ${kernel_source_dir} M=${dkms_tree}/${PACKAGE_NAME}/${PACKAGE_VERSION}/build/audioreach-driver modules VENDOR_QCOM=1"
CLEAN="make -C ${kernel_source_dir} M=${dkms_tree}/${PACKAGE_NAME}/${PACKAGE_VERSION}/build/audioreach-driver clean"
EOF

# ── config: blacklist + udev rules ───────────────────────────────────────────
install -d %{buildroot}%{_sysconfdir}/modprobe.d/
cat > %{buildroot}%{_sysconfdir}/modprobe.d/audioreach.conf << 'EOF'
blacklist q6apm-lpass-dais
blacklist q6apm-dai
blacklist snd-q6dsp-common
blacklist q6prm-clocks
blacklist q6prm
blacklist snd-q6apm
blacklist snd-soc-sc8280xp
blacklist snd-soc-x1e80100
EOF

install -d %{buildroot}/usr/lib/udev/rules.d/
cat > %{buildroot}/usr/lib/udev/rules.d/audioreach.rules << 'EOF'
KERNEL=="msm_audio_mem", GROUP="audio", MODE="0660"
KERNEL=="aud_pasthru_adsp", GROUP="audio", MODE="0660"
EOF

# ── dev: install UAPI and DSP headers ─────────────────────────────────────────
install -d %{buildroot}%{_includedir}/audioreach-kernel/uapi/linux/
install -d %{buildroot}%{_includedir}/audioreach-kernel/dsp/
install -m 0644 include/uapi/linux/msm_audio.h \
    %{buildroot}%{_includedir}/audioreach-kernel/uapi/linux/
install -m 0644 include/dsp/msm_audio_mem.h \
    %{buildroot}%{_includedir}/audioreach-kernel/dsp/

# ── dkms scriptlets ───────────────────────────────────────────────────────────
%post dkms
dkms add %{name}/%{version} --rpm_safe_upgrade
dkms build %{name}/%{version} || true
dkms install %{name}/%{version} || true

%preun dkms
dkms remove %{name}/%{version} --all --rpm_safe_upgrade || true

# ── file lists ────────────────────────────────────────────────────────────────
%files dkms
%license LICENSE
%{_usrsrc}/%{name}-%{version}/

%files config
%{_sysconfdir}/modprobe.d/audioreach.conf
/usr/lib/udev/rules.d/audioreach.rules

%files dev
%{_includedir}/audioreach-kernel/

%changelog
* Wed Aug 27 2026 Qualcomm Linux <quic_linux@quicinc.com> - 1.1.0-1
- Initial RPM packaging of audioreach-kernel version 1.1.0
