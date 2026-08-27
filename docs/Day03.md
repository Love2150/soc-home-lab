# Day 3 — Sysmon Installation and Endpoint Telemetry

| Field | Value |
|---|---|
| Date | 2026-07-22 |
| Status | Complete |
| Phase | Endpoint telemetry |
| Duration | 1 hour |

## Summary

Microsoft Sysmon v15.21 was deployed to the Windows 11 Enterprise virtual machine with the SwiftOnSecurity configuration. After resolving a missing configuration file and the need for Administrator privileges, Sysmon loaded the configuration successfully and generated endpoint telemetry. Process Create events (Event ID 1) were validated and reviewed for executable, parent-process, command-line, user, integrity-level, hash, process GUID, and timestamp data.

## Objectives

- [x] Deploy Microsoft Sysmon to the Windows 11 virtual machine using the SwiftOnSecurity configuration.
- [x] Verify that the endpoint generated Sysmon telemetry.
- [x] Generate and analyze initial Process Create events.

## Environment

| Component | Details |
|---|---|
| Host OS | Ubuntu |
| Guest OS | Windows 11 Enterprise |
| Virtualization | QEMU/KVM |
| Security tooling | Microsoft Sysmon v15.21 |
| Configuration | SwiftOnSecurity Sysmon Configuration (`sysmonconfig-export.xml`) |

## Work Completed

- Downloaded Microsoft Sysmon.
- Downloaded the SwiftOnSecurity Sysmon configuration.
- Installed Sysmon from an Administrator Command Prompt.
- Applied the Sysmon XML configuration.
- Verified successful installation and configuration loading.
- Opened Event Viewer and navigated to **Microsoft → Windows → Sysmon → Operational**.
- Generated test activity with Notepad, Calculator, and PowerShell.
- Confirmed Process Create logging through Event ID 1.
- Reviewed the fields recorded in Sysmon events.

## Implementation and Validation

### Sysmon deployment

Sysmon v15.21 was installed on the Windows 11 Enterprise guest from `C:\Users\SOCAdmin\Downloads\Sysmon`. The installation command accepted the Sysmon license agreement, installed the service, and loaded `sysmonconfig-export.xml`.

The applied configuration enabled process creation logging, DNS query logging, and hash logging.

| Setting | Value |
|---|---|
| Sysmon version | 15.21 |
| Configuration file | `sysmonconfig-export.xml` |
| Configuration status | Successfully loaded |
| Process creation logging | Enabled |
| DNS query logging | Enabled |
| Hash logging | Enabled |

### Telemetry generation and validation

Event Viewer was opened at **Microsoft → Windows → Sysmon → Operational**. Notepad, Calculator, and PowerShell were launched to generate test telemetry. Event ID 1 entries confirmed that Process Create logging was operational.

The reviewed Process Create event exposed the following artifacts:

- Process image
- Parent process (`ParentImage`)
- Command line
- User account
- SHA256 hash
- Integrity level
- Process GUID
- Timestamp

These fields provide the context needed to reconstruct process execution chains during endpoint investigations.

### Key event IDs observed

| Event ID | Description |
|---|---|
| 1 | Process Create |
| 4 | Sysmon Service Started |
| 16 | Sysmon Configuration Changed |
| 22 | DNS Query |

## Commands and Queries

The commands were run in this order from an Administrator Command Prompt:

```cmd
cd C:\Users\SOCAdmin\Downloads\Sysmon

Sysmon64.exe -accepteula -i sysmonconfig-export.xml

notepad.exe

calc.exe

powershell.exe
```

## Evidence

- Screenshot 1 documented successful Sysmon installation.
- Screenshot 2 showed Event Viewer at **Microsoft → Windows → Sysmon → Operational**.
- Screenshot 3 showed a Process Create event (Event ID 1).
- Screenshot 4 showed the event fields `Image`, `ParentImage`, `CommandLine`, `User`, SHA256 hash, and integrity level.
- Screenshot 5 documented test events generated with Notepad, Calculator, and PowerShell.

## Challenges and Troubleshooting

| Problem | Investigation | Resolution or status |
|---|---|---|
| Sysmon initially failed to load. | The XML configuration file was not present in the installation directory. | Downloaded the correct configuration file. |
| Sysmon could not be installed without elevated permissions. | Installation required an administrative shell. | Launched Command Prompt with Administrator privileges and completed the installation successfully. |

## Findings and Analyst Notes

- Sysmon provided more detailed endpoint telemetry than standard Windows Event Logs.
- Process creation telemetry recorded command-line arguments, parent-child process relationships, user accounts, integrity levels, and cryptographic hashes.
- The observed fields can help SOC analysts identify suspicious activity, determine how a process was executed, and reconstruct process execution chains.
- Event ID 1 confirmed that Process Create telemetry was being collected after installation.

## Decisions

- Used the SwiftOnSecurity Sysmon configuration for the deployment.
- Used Notepad, Calculator, and PowerShell to generate known test processes for validation.
- Validated telemetry directly in the Sysmon Operational log in Event Viewer.

## Skills Demonstrated

- Windows administration
- Endpoint monitoring
- Microsoft Sysmon deployment
- Event Viewer navigation
- Process analysis
- Basic digital forensics
- Windows telemetry collection

## Current Status

| Component | Status |
|---|---|
| Sysmon v15.21 installation | Complete |
| SwiftOnSecurity configuration | Complete |
| Process creation logging | Operational |
| DNS query logging | Enabled |
| Hash logging | Enabled |
| Event ID 1 validation | Complete |

## Next Steps

1. Study common Sysmon event IDs.
2. Learn parent-child process analysis.
3. Perform basic threat hunting with Event Viewer.
4. Identify suspicious PowerShell activity.
5. Prepare Sysmon logs for SIEM ingestion.

---

[← Previous day](Day02.md) · [Documentation index](README.md) · [Next day →](Day04.md)
