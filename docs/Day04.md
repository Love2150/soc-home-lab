# Day 4 – Sysmon Investigation and Event Analysis

## Objective

The objective of Day 4 was to move beyond installing Sysmon and begin using Sysmon telemetry as a SOC analyst would during an endpoint investigation.

The lab focused on generating Windows activity, locating the resulting Sysmon events, examining important event fields, and correlating activity across multiple event types.

---

## Lab Environment

- Ubuntu host
- KVM/QEMU virtualization
- Windows 11 Enterprise VM
- Sysmon
- Windows Event Viewer
- GitHub for documentation
- Ubuntu `script` command for terminal recording

---

## Sysmon Log Location

Sysmon events were reviewed at:

`Event Viewer > Applications and Services Logs > Microsoft > Windows > Sysmon > Operational`

---

# Investigation 1 – Process Creation

## Sysmon Event ID 1

**Event ID 1 – Process Create** records the creation of a new process.

Test applications were executed to generate process creation telemetry, including:

- `notepad.exe`
- `calc.exe`
- `curl.exe`

Important fields reviewed included:

- Image
- CommandLine
- ParentImage
- User
- Hashes
- ProcessId
- ParentProcessId

### SOC Analysis

Event ID 1 provides important context for determining how a process started and what command was executed.

The `ParentImage` and `CommandLine` fields are particularly useful because an executable may be legitimate while the way it was launched or the arguments supplied to it may be suspicious.

---

# Investigation 2 – Registry Activity

## Sysmon Event ID 13

**Event ID 13 – Registry Value Set** was reviewed to understand how Sysmon records modifications to Windows Registry values.

Important fields reviewed included:

- EventType
- ProcessId
- Image
- TargetObject
- Details
- User

### SOC Analysis

Registry modifications are important during security investigations because attackers can modify Registry values for persistence, configuration changes, or other malicious activity.

A Registry modification is not automatically malicious. The process responsible for the change and the Registry location being modified must be analyzed to determine whether the activity is expected.

---

# Investigation 3 – curl.exe Activity

A network-related test was performed using Windows `curl.exe`.

Example:

```powershell
curl.exe https://example.com
```

## Event ID 1 – Process Creation

Sysmon successfully recorded the execution of:

`C:\Windows\System32\curl.exe`

The Event ID 1 record confirmed that the curl process executed and provided process information including the executable path and command line.

---

## Event ID 22 – DNS Query

Immediately following the curl execution, Sysmon generated **Event ID 22 – DNS Query** events.

This demonstrated that Sysmon could associate DNS activity with the process responsible for generating the request.

Important fields include:

- Image
- ProcessId
- QueryName
- QueryStatus
- QueryResults

### Event Correlation

The investigation allowed activity to be correlated across multiple Sysmon events:

`curl.exe execution`

↓

`Event ID 1 – Process Create`

↓

`Event ID 22 – DNS Query`

This demonstrates how SOC analysts can use timestamps, process information, and event fields to reconstruct endpoint activity.

---

# Event ID 3 Observation

The original investigation expected to identify:

**Sysmon Event ID 3 – Network Connection**

However, no Event ID 3 associated with the curl test was observed in the Sysmon Operational log.

Rather than changing the configuration during the investigation, the missing event was documented as a finding.

Possible investigation areas for a future session include reviewing the active Sysmon configuration and determining whether network connection events are enabled or filtered.

### Finding

> Sysmon successfully recorded the execution of `curl.exe` with Event ID 1 and associated DNS activity with Event ID 22. No Event ID 3 network connection event was observed during the test. The absence of Event ID 3 was documented for future investigation of the active Sysmon configuration.

---

# Key SOC Fields Reviewed

During the investigation, several Sysmon fields were identified as particularly valuable:

| Field | Investigative Value |
|---|---|
| Image | Identifies the executable |
| CommandLine | Shows how the process was executed |
| ParentImage | Identifies the process that launched it |
| User | Identifies the account associated with activity |
| Hashes | Provides file hashes for IOC/reputation analysis |
| ProcessId | Helps correlate activity involving a process |
| DestinationIp | Identifies remote network destinations when available |
| QueryName | Identifies domains requested by a process |
| TargetObject | Identifies Registry objects being modified |

---

# Evidence Collected

Screenshots were captured showing:

- Sysmon Operational log
- Event ID 1 – Notepad
- Event ID 1 – Calculator
- Event ID 1 – curl.exe
- Event ID 13 – Registry Value Set
- Event ID 22 – DNS activity associated with curl.exe
- Active Sysmon configuration
- Event details containing fields such as:
  - ParentImage
  - CommandLine
  - User
  - Hashes

---

# Key Takeaways

1. Sysmon provides significantly more endpoint visibility than standard process observation alone.

2. Event ID 1 can reveal not only what executable ran but how it was launched.

3. Parent-child process relationships and command-line arguments provide valuable investigation context.

4. Registry activity can be investigated using Sysmon Event ID 13.

5. DNS activity can be associated with specific processes using Event ID 22.

6. Multiple Sysmon events can be correlated using timestamps, process IDs, executable paths, and other fields.

7. Expected telemetry may not always be present. Missing events should be documented and investigated rather than ignored.

---

# Day 4 Status

**COMPLETE**

Skills practiced:

- Sysmon event analysis
- Windows Event Viewer
- Process investigation
- Registry investigation
- DNS investigation
- Event correlation
- Evidence collection
- SOC documentation
- Troubleshooting missing telemetry
