# Day 1 — SOC Lab Foundation and KVM Setup

| Field | Value |
|---|---|
| Date | 2026-07-18 |
| Status | Complete |
| Phase | Lab foundation and virtualization setup |

## Summary

Established the foundation for an enterprise-style SOC home lab by preparing the Ubuntu host, configuring KVM/libvirt virtualization, and creating the `soc-home-lab` GitHub repository for progress documentation. The session ended with the host and virtualization tooling prepared, the initial repository structure in place, and Windows installation media and the first virtual machine identified as the next work.

## Objectives

- [x] Prepare the Ubuntu host for the SOC home lab.
- [x] Configure and validate KVM/libvirt virtualization.
- [x] Create and connect a GitHub repository for documenting lab progress.
- [ ] Learn enterprise SOC operations.
- [ ] Build Active Directory.
- [ ] Deploy Wazuh SIEM.
- [ ] Configure Sysmon.
- [ ] Deploy Zeek and Suricata.
- [ ] Use Velociraptor for digital forensics and incident response (DFIR).
- [ ] Practice MITRE ATT&CK detection.

## Environment

| Component | Details |
|---|---|
| Host | HP Laptop 15-dy1xxx |
| Operating system | Ubuntu 24.04 LTS |
| CPU | Intel Core i3-1005G1 |
| Memory | Upgraded from 8 GB to 16 GB RAM |
| Virtualization | KVM / libvirt |
| Virtual machine management | Virtual Machine Manager |
| Version control | Git and GitHub CLI |
| Repository | `soc-home-lab` |

## Work Completed

- Installed Ubuntu 24.04 LTS.
- Verified hardware virtualization support.
- Installed KVM and libvirt.
- Confirmed that the `libvirtd` service was running.
- Installed and verified Virtual Machine Manager.
- Created the `soc-home-lab` GitHub repository.
- Connected the Ubuntu host to GitHub using Git and GitHub CLI.
- Created the initial project structure.
- Configured `.gitignore` to exclude virtual machine disks, snapshots, and ISO files.

## Implementation and Validation

### Host and virtualization foundation

Ubuntu 24.04 LTS was installed on the HP laptop, whose memory had been upgraded from 8 GB to 16 GB. Hardware virtualization support was verified before KVM and libvirt were installed.

### Virtualization validation

The `libvirtd` service was confirmed to be running. Virtual Machine Manager was then installed and verified, establishing the management interface for the planned Windows virtual machines.

### Repository setup

The `soc-home-lab` repository was created on GitHub. The Ubuntu host was connected to GitHub through Git and GitHub CLI, and the initial project structure was created. A `.gitignore` file was added to prevent virtual machine disks, snapshots, and ISO files from being tracked.

## Commands and Queries

The source journal did not record the exact commands used during this session.

## Evidence

- Hardware virtualization support was verified.
- The `libvirtd` service was confirmed to be running.
- Virtual Machine Manager was installed and verified.
- The initial project structure and `.gitignore` changes were successfully committed to GitHub.

## Challenges and Troubleshooting

| Problem | Investigation | Resolution or status |
|---|---|---|
| `.gitignore` was accidentally created as a directory rather than a file. | The incorrect object type prevented it from being used as the repository ignore file. | Removed the directory and created `.gitignore` correctly as a file. |
| `.gitignore` contents were entered directly into the terminal, producing several `command not found` errors. | The shell attempted to interpret ignore patterns as commands. | Added the patterns to the `.gitignore` file and successfully committed the corrected changes to GitHub. |

## Findings and Analyst Notes

- Small syntax errors in Git commands can cause unexpected issues.
- Distinguishing files from directories is important when working in Linux.
- Using Git from the command line provides better insight into how version control works.

## Decisions

- Used KVM/libvirt as the virtualization platform.
- Used Git and GitHub CLI to connect the Ubuntu host to the `soc-home-lab` repository.
- Excluded virtual machine disks, snapshots, and ISO files from version control through `.gitignore`.

## Skills Demonstrated

- Ubuntu host preparation
- Hardware virtualization validation
- KVM and libvirt installation
- Virtual Machine Manager setup
- Linux file and directory troubleshooting
- Git and GitHub CLI repository setup
- Repository hygiene with `.gitignore`

## Current Status

| Component | Status |
|---|---|
| Ubuntu 24.04 LTS host | Complete |
| 16 GB memory upgrade | Complete |
| Hardware virtualization verification | Complete |
| KVM / libvirt | Operational |
| `libvirtd` service | Operational |
| Virtual Machine Manager | Operational |
| `soc-home-lab` repository | Complete |
| Initial project structure | Complete |
| `.gitignore` configuration | Complete |
| Windows 11 virtual machine | Pending |
| Active Directory environment | Pending |

## Next Steps

1. Download Windows 11 Enterprise Evaluation.
2. Download Windows Server 2022 Evaluation.
3. Create the first Windows 11 virtual machine using KVM.
4. Begin building the Active Directory environment.

---

[Documentation index](README.md) · [Next day →](Day02.md)
