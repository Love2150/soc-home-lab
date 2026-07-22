# Day 2 – Windows 11 Enterprise Deployment


**Date:** July 21, 2026


---


# Objective


The objective of today's lab was to deploy the first Windows endpoint for the Enterprise SOC Home Lab. This included creating a Windows 11 Enterprise virtual machine, completing the operating system installation, configuring virtualization integration, and preparing the endpoint for future security monitoring.


---


# Environment


| Component | Details |

|-----------|---------|

| Host Operating System | Ubuntu 24.04 LTS |

| Hypervisor | QEMU/KVM |

| VM Manager | Virtual Machine Manager (virt-manager) |

| Guest Operating System | Windows 11 Enterprise Evaluation |

| Virtual Machine Name | WIN11-CLIENT01 |

| Firmware | UEFI |

| Network | Default NAT |

| Guest Integration | QEMU Guest Agent |


---


# Tasks Completed


- Downloaded the Windows 11 Enterprise Evaluation ISO.

- Created the `WIN11-CLIENT01` virtual machine using KVM/libvirt.

- Configured virtual CPU, memory, storage, and networking.

- Booted the VM using UEFI firmware.

- Completed the Windows 11 Enterprise installation.

- Configured a local administrator account.

- Verified internet connectivity inside the virtual machine.

- Downloaded and mounted the VirtIO driver ISO.

- Installed the QEMU Guest Agent.

- Verified the QEMU Guest Agent service is running and configured to start automatically.


---


# Virtual Machine Configuration


| Setting | Value |

|----------|---------|

| Name | WIN11-CLIENT01 |

| Operating System | Windows 11 Enterprise Evaluation |

| Firmware | UEFI |

| Disk Format | QCOW2 |

| Network | NAT |

| Integration Services | QEMU Guest Agent |


---


# Challenges Encountered


## UEFI Boot Manager


After creating the virtual machine, the system initially booted into the UEFI Boot Manager instead of automatically launching the Windows installer.


### Resolution


Selected the Windows installation media from the boot menu and successfully launched the Windows Setup process.


---


## Guest Agent Installation


Initially attempted to install the QEMU Guest Agent by downloading the Windows executable on the Ubuntu host, which failed because Linux cannot execute Windows `.exe` installers.


### Resolution


Downloaded and mounted the `virtio-win.iso` image, attached it to the virtual machine, opened the VirtIO CD within Windows, and installed the guest tools successfully. Verified installation by confirming the **QEMU Guest Agent** service was running with an **Automatic** startup type.


---


# Lessons Learned


- Learned how to deploy a Windows virtual machine using QEMU/KVM and Virtual Machine Manager.

- Gained a better understanding of UEFI firmware and virtual machine boot processes.

- Learned the purpose of the VirtIO driver package and QEMU Guest Agent.

- Reinforced troubleshooting techniques by identifying and correcting installation issues related to virtualization tools.


---


# Skills Demonstrated


- Windows 11 Deployment

- Linux Administration

- QEMU/KVM Virtualization

- Virtual Machine Configuration

- VirtIO Driver Management

- QEMU Guest Agent Installation

- UEFI Boot Troubleshooting

- Technical Documentation

- Problem Solving


---


# Screenshots


- Windows Setup

- Windows installation progress

- Initial Windows desktop

- Virtual Machine Manager configuration

- VirtIO ISO mounted

- QEMU Guest Agent service running


---


# Next Steps


- Complete all Windows Updates.

- Create a **Clean-Install** virtual machine snapshot.

- Install Microsoft Sysmon.

- Deploy a production-ready Sysmon configuration.

- Install the Wazuh Agent.

- Verify Windows event logs are successfully collected.


---


# Summary


Day 2 established the first Windows endpoint within the Enterprise SOC Home Lab. The workstation was successfully deployed, network connectivity was verified, and virtualization integration was completed through the installation of the QEMU Guest Agent. This endpoint now serves as the foundation for deploying endpoint security tooling, collecting telemetry, and conducting future detection engineering and incident response exercises.


## Lab Status


| Component | Status |

|----------|--------|

| Ubuntu Host | ✅ Complete |

| GitHub Repository | ✅ Complete |

| KVM/libvirt | ✅ Complete |

| Windows 11 Enterprise | ✅ Complete |

| QEMU Guest Agent | ✅ Complete |

| Windows Updates | ⏳ Pending |

| Snapshot | ⏳ Pending |

| Sysmon | ⏳ Pending |

| Wazuh Agent | ⏳ Pending |

| Active Directory | ⏳ Pending |
