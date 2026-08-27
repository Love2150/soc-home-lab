# SOC Home Lab Documentation

This directory contains the chronological build and investigation journal for the [Enterprise SOC Home Lab](../README.md). Each entry records the objective, environment, implementation, validation evidence, troubleshooting, decisions, current state, and next actions for one lab phase.

## Daily Journal

| Day | Date | Focus | Status |
|---|---|---|---|
| [Day 1](Day01.md) | 2026-07-18 | Ubuntu host preparation and KVM/libvirt foundation | Complete |
| [Day 2](Day02.md) | 2026-07-21 | Windows 11 Enterprise deployment and QEMU guest integration | Complete |
| [Day 3](Day03.md) | 2026-07-22 | Sysmon installation and endpoint telemetry validation | Complete |
| [Day 4](Day04.md) | Not recorded | Sysmon process, Registry, and DNS investigation | Complete |
| [Day 5](Day05.md) | Not recorded | Windows Event Forwarding build and troubleshooting | Blocked; later superseded |
| [Day 6](Day06.md) | 2026-08-16 | Wazuh and Sysmon integration with first SIEM investigation | Complete |
| [Day 7](Day07.md) | 2026-08-19 | Active Directory trust repair and authentication monitoring | Complete |

## Major Progression

```text
Ubuntu + KVM
      ↓
Windows 11 endpoint
      ↓
Sysmon telemetry
      ↓
Endpoint event investigation
      ↓
WEF evaluation and troubleshooting
      ↓
Wazuh agent-based collection
      ↓
Active Directory authentication monitoring
```

## Supporting Evidence

- [`logs/`](logs/) — raw terminal or troubleshooting logs retained for reference
- [`../screenshots/`](../screenshots/) — screenshots grouped by lab day
- [`../recordings/`](../recordings/) — terminal recordings and session artifacts

Raw evidence may contain terminal control characters, repetitive output, or incomplete captures. The daily journals are the authoritative summaries of what was attempted, observed, decided, and completed.

## Documentation Conventions

- [Documentation standard](DOCUMENTATION-STANDARD.md)
- [Reusable daily-lab template](DAILY-LAB-TEMPLATE.md)

Daily files use zero-padded names (`Day01.md`, `Day02.md`, and so on). New entries should follow the shared section order and preserve failed attempts, unresolved findings, commands, and analyst conclusions.

## Current Stopping Point

At the end of Day 7, the lab had validated this path:

```text
Active Directory authentication
            ↓
Windows Security and Sysmon telemetry
            ↓
Wazuh agent
            ↓
Wazuh manager and indexer
            ↓
DQL threat hunting
            ↓
Authentication investigation
```

The next infrastructure milestone is to enroll the Windows Server/domain controller in Wazuh and investigate domain-controller Security events.
