# Enterprise SOC Home Lab

An enterprise-style Security Operations Center lab built on Ubuntu and KVM to practice endpoint telemetry, SIEM operations, Active Directory monitoring, threat hunting, detection analysis, and incident investigation.

![Wazuh SOC dashboard showing an active monitored endpoint](screenshots/day06/Screenshot%20from%202026-08-16%2022-32-47.png)

## Project Overview

This project documents the design and operation of a practical SOC environment running on a single upgraded laptop. The lab currently combines Windows endpoint telemetry, Active Directory authentication, Microsoft Sysmon, and Wazuh to create an end-to-end investigation workflow.

The repository emphasizes more than installation. Each phase records the objective, implementation, evidence, problems encountered, troubleshooting process, analyst interpretation, and next steps.

## Current Capabilities

- Ubuntu 24.04 LTS virtualization host running KVM/QEMU and libvirt
- Windows 11 Enterprise monitored endpoint (`WIN11-CLIENT01`)
- Windows Server 2022 domain controller for `soclab.local`
- Microsoft Sysmon endpoint telemetry
- Wazuh manager, indexer, and dashboard
- Wazuh agent collection of Windows Security and Sysmon event channels
- DQL-based threat hunting in the Wazuh dashboard
- Process, DNS, Registry, and authentication-event investigation
- Active Directory trust troubleshooting and authentication validation
- Centralized technical documentation, screenshots, and terminal recordings

## Architecture

```text
                         Ubuntu 24.04 LTS Host
                    KVM / QEMU / libvirt / virt-manager
                                  |
                +-----------------+-----------------+
                |                                   |
                v                                   v
       Windows 11 Enterprise                Windows Server 2022
         WIN11-CLIENT01                    Active Directory / DNS
                |                              soclab.local
                |
        +-------+-------+
        |               |
        v               v
     Sysmon       Windows Security Log
        |               |
        +-------+-------+
                |
           Wazuh Agent
                |
                v
          Wazuh Manager
                |
                v
          Wazuh Indexer
                |
                v
         Wazuh Dashboard
                |
                v
     Threat Hunting / DQL / Investigation
```

## Validated Telemetry Pipeline

```text
Generate Windows activity
          ↓
Capture endpoint telemetry with Sysmon and Windows Security auditing
          ↓
Collect events through the Wazuh agent
          ↓
Process and index events in Wazuh
          ↓
Search with DQL
          ↓
Investigate process, command-line, DNS, Registry, and authentication activity
```

Status: **Operational**

## Lab Environment

| Component | Implementation | Status |
|---|---|---|
| Physical host | HP Laptop 15-dy1xxx, Intel Core i3-1005G1, 16 GB RAM | Operational |
| Host operating system | Ubuntu 24.04 LTS | Operational |
| Virtualization | KVM/QEMU, libvirt, virt-manager | Operational |
| Windows endpoint | Windows 11 Enterprise Evaluation | Operational |
| Domain services | Windows Server 2022, Active Directory, DNS | Operational |
| Lab domain | `soclab.local` | Operational |
| Endpoint telemetry | Microsoft Sysmon | Operational |
| SIEM/XDR platform | Wazuh manager, indexer, dashboard, and endpoint agent | Operational |
| Windows Event Forwarding | Tested extensively; discontinued as the primary collection path | Documented finding |
| Zeek | Planned | Future phase |
| Suricata | Planned | Future phase |
| Velociraptor | Planned | Future phase |

## Milestones

| Phase | Focus | Outcome | Documentation |
|---|---|---|---|
| Day 1 | Host and virtualization foundation | Installed Ubuntu, KVM/libvirt, and repository structure | [Day 1](docs/Day01) |
| Day 2 | Windows endpoint deployment | Built `WIN11-CLIENT01` and installed QEMU guest integration | [Day 2](docs/Day02.md) |
| Day 3 | Sysmon deployment | Installed Sysmon and validated Event ID 1 telemetry | [Day 3](docs/Day03.md) |
| Day 4 | Endpoint investigation | Analyzed process, Registry, and DNS activity across Sysmon events | [Day 4](docs/Day04.md) |
| Day 5 | Centralized Windows logging | Built a Windows Event Collector and isolated a workgroup WEF limitation | [Day 5](docs/Day05.md) |
| Day 6 | Wazuh integration | Built the Sysmon → Wazuh pipeline and completed the first SIEM investigation | [Day 6](docs/Day06.md) |
| Day 7 | Authentication monitoring | Repaired domain trust and investigated failed and successful domain logons | [Day 7](docs/Day07.md) |

## Investigation Highlights

### Sysmon Process Analysis

The lab generated and analyzed Sysmon Event ID 1 records for processes such as `notepad.exe`, `calc.exe`, `curl.exe`, `net.exe`, `net1.exe`, and PowerShell. Investigations focused on:

- Executable image and path
- Command-line arguments
- Parent-child process relationships
- User and integrity context
- Process GUIDs and IDs
- File hashes
- Surrounding activity and analyst context

### Cross-Event Correlation

A `curl.exe` test was used to correlate:

```text
Process execution
      ↓
Sysmon Event ID 1 — Process Create
      ↓
Sysmon Event ID 22 — DNS Query
```

The expected Sysmon Event ID 3 network connection was not observed. Rather than treating the missing telemetry as success, the result was documented for later configuration analysis.

### Discovery Activity in Wazuh

Wazuh detected `net user` activity and identified it as account discovery behavior. The investigation examined the process chain, execution account, command line, and adjacent PowerShell and `secedit.exe` activity.

The detection was treated as an investigative lead—not automatic proof of compromise.

### Active Directory Authentication

The lab generated and compared:

- Event ID 4625 — failed logon
- Event ID 4624 — successful logon

The investigation used account name, workstation, source address, authentication package, logon process, and Logon Type 2 to determine that the activity was a benign local authentication sequence.

### Domain Trust Troubleshooting

A broken workstation trust relationship was investigated using a repeatable sequence:

```text
DNS → Domain Controller discovery → Trust validation → Repair
```

Representative commands included:

```powershell
nslookup soclab.local
nltest /dsgetdc:soclab.local
Test-ComputerSecureChannel -Verbose
Test-ComputerSecureChannel -Repair -Credential (Get-Credential SOCLAB\Administrator)
```

## Important Engineering Decision

Windows Event Forwarding was tested through network, firewall, WinRM, authentication, subscription, and remote-log-access layers. Although the collector could reach and authenticate to the endpoint, the workgroup-based collector-initiated source remained in a `Trying` state.

Instead of allowing WEF troubleshooting to block the project, the lab switched to direct Sysmon event-channel collection with the Wazuh agent. This produced a reliable pipeline and allowed the project to return to investigation and detection work. The WEF attempt remains documented as a troubleshooting case study.

## Skills Demonstrated

- Linux system administration
- KVM/QEMU virtualization
- Windows 11 and Windows Server deployment
- Active Directory, DNS, and domain trust troubleshooting
- Microsoft Sysmon deployment and analysis
- Windows Event Viewer and Windows Security auditing
- Wazuh installation, endpoint enrollment, and telemetry validation
- DQL threat-hunting queries
- Process and command-line analysis
- Parent-child process correlation
- Authentication-event analysis
- Network, firewall, WinRM, and service troubleshooting
- Evidence collection and technical documentation
- Separating detections from confirmed incidents

## Repository Structure

```text
soc-home-lab/
├── README.md
├── docs/
│   ├── Day01
│   ├── Day02.md
│   ├── Day03.md
│   ├── Day04.md
│   ├── Day05.md
│   ├── Day06.md
│   ├── Day07.md
│   └── logs/
├── recordings/
└── screenshots/
    ├── day01/
    ├── day02/
    ├── day03/
    ├── day04/
    ├── day05/
    └── day06/
```

Large VM disks, snapshots, ISO images, and other generated artifacts are intentionally excluded from version control.

## Next Steps

- Enroll the Windows Server endpoint in Wazuh
- Collect and investigate domain-controller Security events
- Build repeatable authentication and account-management scenarios
- Create detection rules and map investigations to MITRE ATT&CK
- Add Zeek and Suricata network telemetry
- Add Velociraptor for DFIR and endpoint collection
- Develop attack-and-investigate scenarios across the workstation and server
- Improve architecture diagrams, evidence captions, and project status tracking

## Security and Scope

This repository documents activity performed in an isolated, personally controlled lab for defensive-security education. Hostnames, private RFC 1918 addresses, example commands, and lab-domain information are included for reproducibility. Credentials, VM disk images, snapshots, and installation media should never be committed.

## Author

Brandon Love — [GitHub](https://github.com/Love2150) | [Cybersecurity Portfolio](https://love2150.github.io)
