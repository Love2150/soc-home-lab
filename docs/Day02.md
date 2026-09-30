# Day 2 — Windows 11 Enterprise Deployment

| Field | Value |
|---|---|
| Date | 2026-07-21 |
| Status | Complete |
| Phase | Windows endpoint deployment |

## Summary

Day 2 established the first Windows endpoint in the Enterprise SOC Home Lab. The Windows 11 Enterprise workstation was deployed, internet connectivity was verified, and virtualization integration was completed by installing and validating the QEMU Guest Agent. The endpoint is now ready for Windows updates, a clean-install snapshot, endpoint security tooling, telemetry collection, and future detection engineering and incident response exercises.

## Objectives

- [x] Create a Windows 11 Enterprise virtual machine.
- [x] Complete the operating system installation.
- [x] Configure virtualization integration.
- [x] Prepare the endpoint for future security monitoring.

## Environment

| Component | Details |
|---|---|
| Host operating system | Ubuntu 24.04 LTS |
| Hypervisor | QEMU/KVM |
| VM manager | Virtual Machine Manager (`virt-manager`) |
| Guest operating system | Windows 11 Enterprise Evaluation |
| Virtual machine | `WIN11-CLIENT01` |
| Firmware | UEFI |
| Disk format | QCOW2 |
| Network | Default NAT |
| Guest integration | QEMU Guest Agent |

## Work Completed

- Downloaded the Windows 11 Enterprise Evaluation ISO.
- Created `WIN11-CLIENT01` with KVM/libvirt.
- Configured virtual CPU, memory, storage, and networking.
- Booted the virtual machine with UEFI firmware.
- Completed the Windows 11 Enterprise installation.
- Configured a local administrator account.
- Verified internet connectivity from inside the virtual machine.
- Downloaded and mounted the VirtIO driver ISO.
- Installed the QEMU Guest Agent.
- Verified that the QEMU Guest Agent service was running and configured with an **Automatic** startup type.

## Implementation and Validation

### Windows deployment

The `WIN11-CLIENT01` virtual machine was created in Virtual Machine Manager on the Ubuntu QEMU/KVM host. It used UEFI firmware, QCOW2 storage, and the default NAT network. Windows 11 Enterprise Evaluation was installed from the downloaded ISO, and a local administrator account was configured.

### VirtIO integration

The `virtio-win.iso` image was downloaded, attached to the virtual machine, and opened from the VirtIO CD within Windows. The guest tools were then installed inside the Windows guest.

### Validation

- Windows 11 Enterprise completed installation and reached the initial desktop.
- Internet connectivity worked inside `WIN11-CLIENT01`.
- The **QEMU Guest Agent** Windows service was running.
- The service startup type was set to **Automatic**.

## Commands and Queries

No repeatable command-line sequence was recorded for this phase. Deployment and guest-tool installation were completed through Virtual Machine Manager, Windows Setup, the mounted VirtIO ISO, and the Windows Services interface.

## Evidence

- [Windows 11 ready to install](../screenshots/day02/windows-11-ready-to-install.png) — records the final Windows Setup confirmation before installation.
- [Windows 11 installation progress](../screenshots/day02/windows-11-installation-progress.png) — shows the operating-system installation in progress.
- [Windows 11 system information](../screenshots/day02/windows-11-system-about.png) — confirms the installed Windows 11 Enterprise environment.
- [QEMU Guest Agent service](../screenshots/day02/qemu-guest-agent-service.png) — shows the Windows Services console used to validate guest integration.

## Challenges and Troubleshooting

| Problem | Investigation | Resolution or status |
|---|---|---|
| The virtual machine initially opened the UEFI Boot Manager instead of starting Windows Setup automatically. | The Windows installation media was available as a boot option. | Selected the Windows installation media from the boot menu and successfully launched Windows Setup. |
| The first QEMU Guest Agent installation attempt used a Windows executable downloaded on the Ubuntu host. | The attempt failed because Linux cannot execute Windows `.exe` installers. | Downloaded and mounted `virtio-win.iso`, attached it to the virtual machine, opened the VirtIO CD in Windows, and installed the guest tools successfully. Confirmed that the QEMU Guest Agent service was running with an **Automatic** startup type. |

## Findings and Analyst Notes

- A UEFI virtual machine may require manual selection of its installation media when it enters the firmware boot manager instead of launching the installer.
- Windows guest tools must be installed within the Windows guest; mounting the VirtIO ISO provided the required installation path.
- The running QEMU Guest Agent service and **Automatic** startup type confirmed successful guest integration.
- `WIN11-CLIENT01` now provides the Windows endpoint foundation needed for security tooling and telemetry collection.

## Decisions

- Use the mounted `virtio-win.iso` rather than attempting to run a Windows installer on the Ubuntu host.
- Keep the QEMU Guest Agent configured for automatic startup so virtualization integration remains available after reboot.
- Complete Windows updates and create a clean-install snapshot before adding security tooling.

## Skills Demonstrated

- Windows 11 deployment.
- Linux administration.
- QEMU/KVM virtualization.
- Virtual machine configuration.
- VirtIO driver management.
- QEMU Guest Agent installation.
- UEFI boot troubleshooting.
- Technical documentation.
- Problem solving.

## Current Status

| Component | Status |
|---|---|
| Ubuntu host | Complete |
| GitHub repository | Complete |
| KVM/libvirt | Complete |
| Windows 11 Enterprise | Complete |
| QEMU Guest Agent | Complete |
| Windows updates | Pending |
| Clean-install snapshot | Pending |
| Sysmon | Pending |
| Wazuh Agent | Pending |
| Active Directory | Pending |

## Next Steps

1. Complete all Windows updates.
2. Create a **Clean-Install** virtual machine snapshot.
3. Install Microsoft Sysmon.
4. Deploy a production-ready Sysmon configuration.
5. Install the Wazuh Agent.
6. Verify that Windows event logs are successfully collected.

---

[← Previous day](Day01.md) · [Documentation index](README.md) · [Next day →](Day03.md)
