# Day 6 — Wazuh and Sysmon Integration

| Field | Value |
|---|---|
| Date | 2026-08-16 |
| Status | Complete |
| Phase | Wazuh and Sysmon integration |

## Summary

This session replaced the stalled Windows Event Forwarding (WEF) path with direct Sysmon collection through the Wazuh agent. The Wazuh all-in-one deployment was rebuilt, `WIN11-CLIENT01` was registered, the manager address was corrected, and the Sysmon Operational channel was added to the agent configuration. Local event checks, manager archive output, dashboard alerts, and a DQL search confirmed the end-to-end telemetry pipeline.

The session then moved from infrastructure troubleshooting into SOC analysis by reviewing a Sysmon Event ID 1 alert for `net user`. The alert was treated as an investigative lead rather than proof of compromise. The lab stopped with Wazuh and Sysmon operational, WEF discontinued for now, and the endpoint ready for practical threat-hunting exercises.

## Objectives

- [x] Rebuild and validate the Wazuh manager stack.
- [x] Install and register the Wazuh agent on `WIN11-CLIENT01` without relying on Internet access from the VM.
- [x] Configure direct collection of the Sysmon Operational event channel.
- [x] Validate telemetry locally, at the manager, and in the Wazuh dashboard.
- [x] Use DQL to find Sysmon process-creation events.
- [x] Perform an initial investigation of a Sysmon Event ID 1 alert.
- [x] Record the engineering decision to stop WEF troubleshooting and use direct Wazuh agent collection.

## Environment

| Component | Details |
|---|---|
| Lab | SOC Home Lab |
| Wazuh host | Ubuntu host `grim50reaper-HP-Laptop-15-dy1xxx` |
| Wazuh components | Wazuh Manager, Indexer, and Dashboard |
| Windows endpoint | `WIN11-CLIENT01` / `WIN11-CLIENT01.soclab.local` |
| Windows domain | `soclab.local` |
| Manager address used by the Windows VM | `192.168.122.1` |
| Dashboard address | `https://192.168.1.136` |
| Endpoint telemetry | Sysmon through the Wazuh agent |

## Work Completed

- Rebuilt the failed Wazuh installation with the Wazuh all-in-one installer.
- Verified the Wazuh Manager, Indexer, and Dashboard services.
- Hosted the Wazuh MSI from Ubuntu and downloaded it to the offline Windows 11 VM.
- Installed and started the Windows Wazuh service.
- Corrected the agent manager address from `192.168.1` to `192.168.122.1`.
- Confirmed that `WIN11-CLIENT01` registered with the manager and became active.
- Added the Sysmon Operational channel to `ossec.conf` and restarted the agent.
- Validated Sysmon Event ID 1 locally on Windows.
- Temporarily enabled Wazuh JSON archive logging to validate manager-side ingestion.
- Confirmed Windows endpoint alerts in the Wazuh Threat Hunting interface.
- Used DQL to locate Sysmon Event ID 1 records.
- Opened and assessed a discovery alert involving `net user`.

## Implementation and Validation

### Wazuh manager rebuild

The previous Wazuh installation on Ubuntu had service-startup problems, so it was rebuilt from scratch with the Wazuh all-in-one installation. The Manager, Indexer, and Dashboard services each returned `active` after installation.

The Ubuntu host had multiple network interfaces. Windows VM communication used the libvirt address `192.168.122.1`, while the dashboard was accessed from the Ubuntu host at `https://192.168.1.136`.

### Windows agent installation and address correction

`WIN11-CLIENT01` did not have Internet access. The Wazuh agent installer was therefore downloaded on Ubuntu, served from `192.168.122.1:8000`, and transferred locally to the VM. `Get-Service WazuhSvc` showed the service as `Running` after installation.

The agent was initially configured with the incomplete manager address:

```xml
<address>192.168.1</address>
```

The address was corrected to:

```xml
<address>192.168.122.1</address>
```

After the service was restarted, the agent log reported:

```text
wazuh-agent: INFO: Agent is now online. Process unlocked, continuing...
```

Manager-side registration validation returned the local server and the active Windows endpoint:

```text
ID: 000, Name: grim50reaper-HP-Laptop-15-dy1xxx (server), IP: 127.0.0.1, Active/Local
ID: 001, Name: WIN11-CLIENT01, IP: any, Active
```

### Sysmon event-channel configuration

The Windows Wazuh agent was configured to collect the Sysmon Operational event channel directly. The following block was added to `C:\Program Files (x86)\ossec-agent\ossec.conf`:

```xml
<localfile>
  <location>Microsoft-Windows-Sysmon/Operational</location>
  <log_format>eventchannel</log_format>
</localfile>
```

The Wazuh agent was restarted after the configuration change.

### Local Sysmon validation

A local Windows event query returned multiple process-creation records with Event ID 1 from `Microsoft-Windows-Sysmon`. This established that Sysmon itself was operating and writing process events before manager-side ingestion was assessed.

### End-to-end telemetry validation

Temporary JSON archive logging was enabled on the Wazuh manager with:

```xml
<logall_json>yes</logall_json>
```

After the manager restart, `archives.json` showed records containing:

```text
Microsoft-Windows-Sysmon
Microsoft-Windows-Sysmon/Operational
EventID: 1
```

This confirmed the following pipeline:

```text
WIN11-CLIENT01
      ↓
    Sysmon
      ↓
  Wazuh Agent
      ↓
 Wazuh Manager
      ↓
Wazuh Indexer
      ↓
Wazuh Dashboard
```

The pipeline status was operational. Archive logging was used only for validation and can remain disabled during normal lab operation to avoid unnecessary disk usage.

### Dashboard and DQL validation

The Wazuh dashboard was available at `https://192.168.1.136`. The Threat Hunting interface displayed alerts from `WIN11-CLIENT01` after a high-severity-only filter was removed. The endpoint filter was:

```text
agent.name:"WIN11-CLIENT01"
```

A DQL query for Sysmon process creation returned telemetry in the Wazuh Events view and allowed records to be expanded for investigation:

```text
agent.name:"WIN11-CLIENT01" AND data.win.system.eventID:1
```

## Commands and Queries

### Wazuh service validation on Ubuntu

```bash
sudo systemctl is-active wazuh-manager
sudo systemctl is-active wazuh-indexer
sudo systemctl is-active wazuh-dashboard
```

Expected result for each service:

```text
active
```

### Serve the Wazuh agent installer to the Windows VM

```bash
python3 -m http.server 8000 --bind 192.168.122.1
```

### Verify and restart the Windows Wazuh service

```powershell
Get-Service WazuhSvc
Restart-Service WazuhSvc
```

### Validate agent registration on the manager

```bash
sudo /var/ossec/bin/agent_control -l
```

### Validate local Sysmon events

```powershell
Get-WinEvent -LogName "Microsoft-Windows-Sysmon/Operational" -MaxEvents 5 |
Select-Object TimeCreated,Id,ProviderName
```

### Monitor temporary manager archive output

```bash
sudo tail -f /var/ossec/logs/archives/archives.json | grep -i sysmon
```

### Wazuh dashboard filters

```text
agent.name:"WIN11-CLIENT01"
```

```text
agent.name:"WIN11-CLIENT01" AND data.win.system.eventID:1
```

## Evidence

### Infrastructure transition and WEF troubleshooting

- [Active Directory Domain Services installed](../screenshots/day06/ad-domain-services-installed.png) — confirms successful AD DS feature installation.
- [`soclab.local` domain details](../screenshots/day06/soclab-domain-details.png) — records the domain and domain-controller configuration returned by `Get-ADDomain`.
- [Workstation DNS server configuration](../screenshots/day06/workstation-dns-server-configuration.png) — points the Windows client at the domain controller's DNS service.
- [`soclab.local` DNS resolution](../screenshots/day06/soclab-dns-resolution.png) — validates the domain and domain-controller service records.
- [Domain secure-channel validation](../screenshots/day06/domain-secure-channel-validation.png) — confirms domain membership and a healthy workstation secure channel.
- [Endpoint DNS and WinRM validation](../screenshots/day06/endpoint-dns-and-winrm-validation.png) — confirms client-name resolution and successful `Test-WSMan` connectivity from the server.
- [Domain WEF source still in `Trying`](../screenshots/day06/wef-domain-source-still-trying.png) — records that the subscription source remained unresolved after the domain transition.
- [Remote Sysmon event read](../screenshots/day06/remote-sysmon-event-read.png) — proves the server could remotely retrieve a Sysmon event from the endpoint.
- [WEF Group Policy creation](../screenshots/day06/wef-group-policy-creation.png) — records creation of the `SOC-Lab-WEF` Group Policy during the final WEF attempt.

### Service and agent state

- Wazuh Manager, Indexer, and Dashboard returned `active`.
- `Get-Service WazuhSvc` returned `Running`.
- The agent log stated that the agent was online.
- `agent_control -l` showed `WIN11-CLIENT01` as `Active` with agent ID `001`.
- [Wazuh dashboard with one active agent](../screenshots/day06/wazuh-dashboard-active-agent.png) — confirms the enrolled endpoint and populated alert overview.

### Source and ingestion validation

- The local Sysmon Operational channel returned Event ID 1 records from `Microsoft-Windows-Sysmon`.
- Wazuh manager archive output contained the Sysmon provider, channel, and Event ID 1.
- The Threat Hunting view showed dozens of endpoint alerts after the high-severity-only filter was removed.
- The DQL process-creation query returned expandable Sysmon events.
- [Wazuh Discover context](../screenshots/day06/wazuh-discover-context.png) — shows surrounding indexed records from the manager and endpoint.
- [Wazuh Sysmon event details](../screenshots/day06/wazuh-sysmon-event-details.png) — shows Event ID 1 fields for `WIN11-CLIENT01.soclab.local`.
- [Wazuh process-event context](../screenshots/day06/wazuh-process-event-context.png) — shows nearby `net.exe`, PowerShell, and `secedit.exe` activity used for investigation context.

### First Sysmon investigation record

| Field | Value |
|---|---|
| Endpoint | `WIN11-CLIENT01.soclab.local` |
| Event | Sysmon Event ID 1 |
| Provider | `Microsoft-Windows-Sysmon` |
| Process | `C:\Windows\SysWOW64\net1.exe` |
| Command line | `C:\WINDOWS\system32\net1 user` |
| Parent process | `C:\Windows\SysWOW64\net.exe` |
| Parent command line | `net user` |
| User | `NT AUTHORITY\SYSTEM` |
| Wazuh rule ID | `92031` |
| Rule level | `3` |
| Rule description | `Discovery activity executed` |
| Rule groups | `sysmon`, `sysmon_eid1_detections`, `windows` |

## Challenges and Troubleshooting

| Problem | Investigation | Resolution or status |
|---|---|---|
| WEF client remained in `Trying` state with WinRM-related errors | Tested domain membership, Group Policy, DNS, time synchronization, WinRM connectivity, Kerberos/SPN-related configuration, and both source-initiated and collector-initiated subscriptions | WEF was discontinued for now because it consumed substantial lab time without becoming reliable. Sysmon collection moved to the Wazuh agent. |
| Existing Wazuh installation had service-startup problems | Replaced the installation and checked all three Wazuh services | Rebuilt with the all-in-one installation; Manager, Indexer, and Dashboard became operational. |
| Windows VM had no Internet access | Hosted the MSI from Ubuntu over the libvirt network | Agent installer transferred successfully from `192.168.122.1:8000`. |
| Agent was installed with `<address>192.168.1</address>` | Reviewed and corrected the Wazuh agent configuration | Changed the manager address to `192.168.122.1`; the agent came online and registered as active. |
| Dashboard initially showed limited results | Removed the high-severity-only filter | Dozens of alerts from `WIN11-CLIENT01` became visible. |
| Domain trust warning remains | Warning states: `The trust relationship between this workstation and the primary domain failed.` | Unresolved but non-blocking for Wazuh and Sysmon telemetry; defer unless it blocks a future objective. |

## Findings and Analyst Notes

### Initial process-creation assessment

The command `net user` enumerates Windows user accounts. It can represent legitimate administrative activity, but it is also associated with attacker discovery and reconnaissance. Wazuh classified the event as `Discovery activity executed`, but the event alone was not sufficient to classify the activity as malicious.

The alert therefore requires context from the process chain, executing account, and nearby events. This is the distinction between reviewing a detection and completing an investigation.

### Surrounding activity

Nearby activity included:

```text
net.exe / net1.exe
powershell.exe
secedit.exe
```

A Sysmon Event ID 11 file-creation event was also observed under:

```text
C:\Windows\SystemTemp\
```

The activity ran as:

```text
NT AUTHORITY\SYSTEM
```

These records provide a useful chain for future timeline analysis, but they still require context and should not be labeled automatically as malicious.

### Investigation questions retained for follow-up

- What process launched the command?
- What account executed it?
- What occurred before it?
- What occurred after it?
- Is the behavior expected on this system?
- Are additional suspicious commands present in the same process chain?

### Analyst conclusion

The telemetry and alerting pipeline worked as intended. The observed `net user` activity is a discovery lead that warrants timeline analysis; it is not, by itself, evidence that the endpoint was compromised.

## Decisions

- Stop WEF troubleshooting for now. The subscription could be created and appeared active, but the client remained in `Trying` state and the pipeline was unreliable.
- Collect Sysmon directly from Windows with the Wazuh agent so the lab can prioritize practical SOC investigation work.
- Use JSON archive logging only for end-to-end validation, then leave it disabled during normal operation to limit unnecessary disk usage.
- Defer the domain trust warning because it does not block the core telemetry pipeline; revisit it only if it blocks a future lab objective.
- Retain the Windows Server in the lab, but do not use it primarily as the WEF collector. Planned roles remain Active Directory/domain services, Windows Security event generation, authentication monitoring, account and group activity, a second Wazuh-monitored Windows system, and future workstation-to-server attack and investigation scenarios.

## Skills Demonstrated

- Deploying and validating a Wazuh endpoint agent
- Troubleshooting SIEM agent connectivity
- Configuring Windows Event Channel collection
- Sending Sysmon telemetry to a SIEM
- Validating telemetry at both the source and manager
- Accessing and navigating the Wazuh dashboard
- Filtering endpoint telemetry and writing DQL queries
- Investigating Sysmon Event ID 1
- Reviewing command-line execution and parent/child process relationships
- Reviewing process execution under `NT AUTHORITY\SYSTEM`
- Building an investigation timeline from surrounding events
- Distinguishing a detection from a confirmed security incident

## Current Status

| Component | Status |
|---|---|
| Ubuntu Wazuh Manager | Operational |
| Wazuh Indexer | Operational |
| Wazuh Dashboard | Operational |
| `WIN11-CLIENT01` Wazuh agent | Operational |
| Sysmon | Operational |
| Sysmon to Wazuh ingestion | Operational |
| Wazuh Threat Hunting | Operational |
| DQL queries | Operational |
| Sysmon Event ID 1 investigation workflow | Operational |
| Windows Server integration | Pending |
| WEF | Discontinued |
| Domain trust warning | Unresolved, non-blocking |

The core lab infrastructure is operational, and the environment has moved from setup and troubleshooting into SOC investigation work. Windows activity can now be captured with Sysmon, sent through the Wazuh agent, indexed and detected in Wazuh, searched with DQL, and investigated through process and command-line context.

Session completion state:

- Lab telemetry pipeline: Complete
- Wazuh/Sysmon integration: Complete
- Threat Hunting validation: Complete
- Ready for practical SOC investigations: Yes

## Next Steps

1. Build a short timeline around the `net user` discovery alert.
2. Examine the nearby `powershell.exe` and `secedit.exe` activity.
3. Practice distinguishing benign administrative behavior from suspicious discovery.
4. Generate controlled Sysmon Event IDs 1, 3, 11, 13, and 22.
5. Investigate those events through Wazuh Threat Hunting.
6. Document the supporting evidence and analyst conclusions.
7. After the endpoint investigation block, install the Wazuh agent on the Windows Server and collect its Windows Security events as a second monitored Windows host.

---

[← Previous day](Day05.md) · [Documentation index](README.md) · [Next day →](Day07.md)
