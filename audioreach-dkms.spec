%global debug_package %{nil}

Name:           audioreach-dkms
Version:        1.1.0
Release:        2%{?dist}
Summary:        AudioReach out-of-tree Linux kernel drivers

License:        GPL-2.0-only
URL:            https://github.com/Audioreach/audioreach-kernel
Source0:        https://github.com/Audioreach/audioreach-kernel/archive/refs/tags/v%{version}.tar.gz#/audioreach-kernel-%{version}.tar.gz
Source1:        dkms.conf
Source2:        audioreach.conf

ExclusiveArch:  aarch64

BuildRequires:  systemd-rpm-macros

Requires:       dkms
Requires(post): dkms
Requires(preun):dkms
Recommends:     kernel-devel

%description
AudioReach Kernel provides out-of-tree Linux kernel drivers that enable
communication between the AudioReach signal processing framework running
on an audio DSP and userspace graph service libraries.

These drivers integrate AudioReach with the Linux kernel, allowing control
and data exchange between the host CPU and DSP-based audio processing
pipelines on Qualcomm platforms.

# ── config subpackage ─────────────────────────────────────────────────────────
%package config
Summary:        AudioReach modprobe blacklist and udev rules
BuildArch:      noarch

%description config
Blacklists native ASoC machine drivers that conflict with the AudioReach
kernel driver (Config #2 path), and installs udev rules for AudioReach
character devices.

Install this alongside audioreach-dkms to activate the AudioReach
DSP audio path on QCS6490 (RB3 Gen2).

# ── devel subpackage ──────────────────────────────────────────────────────────
%package -n audioreach-linux-devel
Summary:        Development headers for AudioReach kernel drivers
BuildArch:      noarch

%description -n audioreach-linux-devel
Header files required to build userspace applications or kernel modules
that integrate with AudioReach kernel drivers.

# ─────────────────────────────────────────────────────────────────────────────

%prep
%setup -n audioreach-kernel-%{version}

%build
# Nothing built here — DKMS builds audioreach_driver.ko on the target at
# install time against the running kernel.

%install
# ── dkms: install source tree + dkms.conf into /usr/src ──────────────────────
install -d %{buildroot}%{_usrsrc}/%{name}-%{version}
cp -r audioreach-driver dsp include ipc Makefile \
    %{buildroot}%{_usrsrc}/%{name}-%{version}/
install -m 0644 %{SOURCE1} %{buildroot}%{_usrsrc}/%{name}-%{version}/dkms.conf

# ── config: blacklist + udev rules ───────────────────────────────────────────
install -d %{buildroot}%{_sysconfdir}/modprobe.d/
install -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/modprobe.d/audioreach.conf

install -d %{buildroot}%{_udevrulesdir}/
cat > %{buildroot}%{_udevrulesdir}/audioreach.rules << 'EOF'
KERNEL=="msm_audio_mem", GROUP="audio", MODE="0660"
KERNEL=="aud_pasthru_adsp", GROUP="audio", MODE="0660"
EOF

# ── dev: install UAPI and DSP headers ─────────────────────────────────────────
install -d %{buildroot}%{_includedir}/linux/
install -d %{buildroot}%{_includedir}/dsp/
install -m 0644 include/uapi/linux/msm_audio.h \
    %{buildroot}%{_includedir}/linux/
install -m 0644 include/dsp/msm_audio_mem.h \
    %{buildroot}%{_includedir}/dsp/

# ── dkms scriptlets ───────────────────────────────────────────────────────────
%post
dkms add %{name}/%{version} --rpm_safe_upgrade
dkms build %{name}/%{version} || true
dkms install %{name}/%{version} || true

%preun
dkms remove %{name}/%{version} --all --rpm_safe_upgrade || true

# ── file lists ────────────────────────────────────────────────────────────────
%files
%license LICENSE
%{_usrsrc}/%{name}-%{version}/

%files config
%{_sysconfdir}/modprobe.d/audioreach.conf
%{_udevrulesdir}/audioreach.rules

%files -n audioreach-linux-devel
%{_includedir}/linux/msm_audio.h
%{_includedir}/dsp/msm_audio_mem.h

%changelog
* Thu Sep 25 2026 Chiluka Rohith <rchiluka@qti.qualcomm.com> - 1.1.0-2
- Rename headers subpackage from audioreach-dkms-dev to
  audioreach-linux-devel for CentOS naming convention and to
  align with the Debian audioreach-linux-dev package

* Wed Aug 27 2026 Qualcomm Linux <quic_linux@quicinc.com> - 1.1.0-1
- Initial RPM packaging of audioreach-kernel version 1.1.0
