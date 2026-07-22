# Day 3 - Sysmon Installation & Endpoint Telemetry

**Date:** July 22, 2026 
**Duration:** 1 Hour

---

# Objective

Deploy Microsoft Sysmon to the Windows 11 virtual machine using the SwiftOnSecurity configuration, verify endpoint telemetry generation, and analyze the first process creation events.

---

# Environment

| Component | Details |
|-----------|---------|
| Host OS | Ubuntu |
| Guest OS | Windows 11 Enterprise |
| Virtualization | QEMU/KVM |
| Tool | Microsoft Sysmon v15.21 |
| Configuration | SwiftOnSecurity Sysmon Configuration |

---

# Tasks Completed

- [x] Downloaded Microsoft Sysmon
- [x] Downloaded SwiftOnSecurity Sysmon configuration
- [x] Installed Sysmon as Administrator
- [x] Applied Sysmon XML configuration
- [x] Verified successful installation
- [x] Opened Event Viewer
- [x] Navigated to Microsoft → Windows → Sysmon → Operational
- [x] Generated Process Create events
- [x] Verified Event ID 1 logging
- [x] Reviewed Sysmon event details

---

# Commands Used

```cmd
cd C:\Users\SOCAdmin\Downloads\Sysmon

Sysmon64.exe -accepteula -i sysmonconfig-export.xml

notepad.exe

calc.exe

powershell.exe
```

---

# Configuration

| Setting | Value |
|----------|-------|
| Sysmon Version | 15.21 |
| Configuration File | sysmonconfig-export.xml |
| Configuration Status | Successfully Loaded |
| Process Creation Logging | Enabled |
| DNS Query Logging | Enabled |
| Hash Logging | Enabled |

---

# Screenshots

## Screenshot 1
- Sysmon installation completed successfully

## Screenshot 2
- Event Viewer
- Microsoft → Windows → Sysmon → Operational

## Screenshot 3
- Event ID 1 (Process Create)

## Screenshot 4
Event fields displayed:

- Image
- ParentImage
- CommandLine
- User
- SHA256 Hash
- Integrity Level

## Screenshot 5
Generated test events using:

- Notepad
- Calculator
- PowerShell

---

# Challenges Encountered

Initially, Sysmon failed to load because the XML configuration file was not present in the installation directory. After downloading the correct configuration file, the installation required launching Command Prompt with Administrator privileges before Sysmon could be installed successfully.

---

# Lessons Learned

Sysmon provides significantly more detailed endpoint telemetry than standard Windows Event Logs. Process creation events include valuable forensic information such as command-line arguments, parent-child process relationships, user accounts, integrity levels, and cryptographic hashes. This information is commonly used by SOC analysts during investigations to identify suspicious activity and determine how a process was executed.

---

# Skills Demonstrated

- Windows Administration
- Endpoint Monitoring
- Microsoft Sysmon Deployment
- Event Viewer Navigation
- Process Analysis
- Basic Digital Forensics
- Windows Telemetry Collection

---

# Key Event IDs Observed

| Event ID | Description |
|----------|-------------|
| 1 | Process Create |
| 4 | Sysmon Service Started |
| 16 | Sysmon Configuration Changed |
| 22 | DNS Query |

---

# Investigation Notes

The Process Create event included the following artifacts:

- Process Image
- Parent Process
- Command Line
- User Account
- SHA256 Hash
- Integrity Level
- Process GUID
- Timestamp

These fields provide critical context during endpoint investigations and allow analysts to reconstruct process execution chains.

---

# Next Steps

- Study common Sysmon Event IDs
- Learn parent-child process analysis
- Perform basic threat hunting using Event Viewer
- Identify suspicious PowerShell activity
- Prepare Sysmon logs for SIEM ingestion

---

# Summary

Today I successfully deployed Microsoft Sysmon to my Windows 11 virtual machine using the SwiftOnSecurity configuration. After resolving issues with the configuration file and administrative permissions, I verified that Sysmon was generating endpoint telemetry. I confirmed Process Create (Event ID 1) events and analyzed important fields including the executable path, parent process, command line, user account, integrity level, and SHA256 hash. This lab demonstrated how Sysmon enhances Windows logging and provides the detailed telemetry that SOC analysts use for threat detection, incident response, and digital forensic investigations.

---
