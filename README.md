<!--
Copyright (c) Qualcomm Technologies, Inc. and/or its subsidiaries.
SPDX-License-Identifier: BSD-3-Clause
-->
# pkg-rpm-audioreach-kernel

RPM packaging for
[audioreach-kernel](https://github.com/Audioreach/audioreach-kernel) on
CentOS Stream 10 (aarch64).

AudioReach Kernel provides out-of-tree Linux kernel drivers that enable
communication between the AudioReach signal processing framework running on an
audio DSP and userspace graph service libraries. These drivers integrate
AudioReach with the Linux kernel, allowing control and data exchange between
the host CPU and DSP-based audio processing pipelines on Qualcomm platforms.
The package is maintained on the CentOS Stream 10 (`c10s`) branch and uses the
shared GitHub Actions build and release workflow.

## CI Workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| [`build-on-pr.yml`](.github/workflows/build-on-pr.yml) | Pull request | Build the RPM(s) so reviewers confirm the package still builds. Read-only — never publishes. |
| [`pkg-release.yml`](.github/workflows/pkg-release.yml) | Manual (`workflow_dispatch`) | Build **and** publish the RPM(s) to Artifactory, behind an approval gate. |

The GitHub Actions workflows use the shared
[`qcom-rpm-utils`](https://github.com/qualcomm-linux/qcom-rpm-utils) build
environment and run `rpmbuild` inside the prebuilt `rpm-builder` container
image for the runner's host architecture.

---

## Repository Layout

The `c10s` branch contains the RPM packaging files:

| File | Purpose |
|---|---|
| `audioreach-kernel.spec` | Builds the DKMS, config, and dev subpackages. |
| `sources` | SHA-512 checksum for the upstream source archive. |
| `0001-*.patch` | Packaging patch applied during the build. |
| `README.md` | Package and repository documentation. |
| `LICENSE.txt` | License for the RPM packaging repository. |

The source archive is not committed to this repository. The spec file's
`Source0` points to the upstream release, and the checksum in `sources` is
verified before the RPM is built.

---

## Packages

- `audioreach-kernel-dkms`: AudioReach kernel drivers packaged for DKMS.
  Installs the driver source into `/usr/src` and automatically builds and
  installs the `audioreach_driver` module for the running kernel (6.18+).
- `audioreach-kernel-config`: Blacklists native ASoC machine drivers that
  conflict with the AudioReach kernel driver, and installs udev rules for
  AudioReach character devices.
- `audioreach-kernel-dev`: Header files required to build userspace
  applications or kernel modules that integrate with AudioReach kernel drivers.

---

## Updating the package version

This is the everyday workflow — **two edits on `c10s`, no tarball in git**:

1. Bump `Version:` in the spec (and the `Source0:` URL if its path changed).
2. Recompute the checksum for the new tarball:
   ```bash
   sha512sum --tag audioreach-kernel-<newversion>.tar.gz > sources
   ```
3. Commit the spec + `sources`, open a PR (build verifies it), merge, then run
   **Release**. The first release fetches the new upstream tarball, verifies it,
   and caches it back to Artifactory automatically.

## License

This project is licensed under the BSD 3-Clause License. See [LICENSE.txt](LICENSE.txt) for the complete license text.

The upstream AudioReach kernel drivers are licensed separately under
`GPL-2.0-only`, as declared by `audioreach-kernel.spec`.
