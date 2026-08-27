# Day 4 — Sysmon Investigation and Event Analysis

| Field | Value |
|---|---|
| Date | Not recorded |
| Status | Complete |
| Phase | Endpoint telemetry investigation |

## Summary

Day 4 moved beyond Sysmon installation and used its telemetry for an endpoint investigation. Windows activity was generated and reviewed in Event Viewer, with analysis focused on process creation, Registry changes, and DNS queries. Event ID 1 for `curl.exe` was correlated with Event ID 22 DNS activity, while the expected Event ID 3 network connection event was not observed and remains a documented follow-up item.

## Objectives

- [x] Generate Windows activity that produces Sysmon telemetry.
- [x] Locate and review Sysmon events in Windows Event Viewer.
- [x] Examine fields that provide process, Registry, user, hash, and DNS context.
- [x] Correlate related activity across multiple Sysmon event types.
- [x] Document missing expected telemetry without changing the configuration during the investigation.

## Environment

| Component | Details |
|---|---|
| Host | Ubuntu |
| Virtualization | KVM/QEMU |
| Endpoint | Windows 11 Enterprise VM |
| Security tooling | Sysmon and Windows Event Viewer |
| Documentation | GitHub; Ubuntu `script` command used for terminal recording |

## Work Completed

- Opened the Sysmon Operational log at `Event Viewer > Applications and Services Logs > Microsoft > Windows > Sysmon > Operational`.
- Ran `notepad.exe`, `calc.exe`, and `curl.exe` to generate process telemetry.
- Reviewed Sysmon Event ID 1 process-creation records and their investigative fields.
- Reviewed Sysmon Event ID 13 Registry Value Set activity.
- Reviewed Sysmon Event ID 22 DNS queries associated with `curl.exe`.
- Correlated the `curl.exe` process event with subsequent DNS activity.
- Searched for the expected Event ID 3 network connection record and documented that it was absent.
- Captured screenshots of the reviewed events, active Sysmon configuration, and relevant event details.

## Implementation and Validation

### Process creation — Event ID 1

The test applications `notepad.exe`, `calc.exe`, and `curl.exe` were executed to generate process-creation telemetry. Sysmon recorded Event ID 1 for these processes, including the execution of `C:\Windows\System32\curl.exe`.

The following fields were reviewed:

- `Image`
- `CommandLine`
- `ParentImage`
- `User`
- `Hashes`
- `ProcessId`
- `ParentProcessId`

Event ID 1 established what executable ran, how it was invoked, which process launched it, and which user was associated with the activity. This context matters because a legitimate executable can still be suspicious when launched by an unexpected parent or with unusual arguments.

### Registry activity — Event ID 13

Sysmon Event ID 13, Registry Value Set, was reviewed to understand how Registry modifications are represented. The following fields were examined:

- `EventType`
- `ProcessId`
- `Image`
- `TargetObject`
- `Details`
- `User`

Registry changes can support persistence, configuration changes, or other malicious behavior, but a modification is not malicious by itself. The responsible process and the affected Registry path must be evaluated together.

### `curl.exe` and DNS activity — Event IDs 1 and 22

A request to `https://example.com` was generated with Windows `curl.exe`. Event ID 1 confirmed execution of `C:\Windows\System32\curl.exe` and exposed its path and command line. Immediately afterward, Event ID 22 DNS Query records showed DNS activity associated with the process.

The Event ID 22 review included:

- `Image`
- `ProcessId`
- `QueryName`
- `QueryStatus`
- `QueryResults`

### Event correlation

The observed sequence was:

```text
curl.exe execution
  ↓
Event ID 1 — Process Create
  ↓
Event ID 22 — DNS Query
```

Timestamps, process information, process IDs, executable paths, and event-specific fields can connect these records and reconstruct endpoint activity. In this test, process execution and DNS telemetry were available; network connection telemetry was not.

## Commands and Queries

The activity-generating commands, in execution order, were:

```powershell
notepad.exe
calc.exe
curl.exe https://example.com
```

Sysmon events were then reviewed in:

```text
Event Viewer > Applications and Services Logs > Microsoft > Windows > Sysmon > Operational
```

## Evidence

Screenshots were captured for the following evidence:

- Sysmon Operational log.
- Event ID 1 for Notepad.
- Event ID 1 for Calculator.
- Event ID 1 for `curl.exe`.
- Event ID 13 Registry Value Set activity.
- Event ID 22 DNS activity associated with `curl.exe`.
- Active Sysmon configuration.
- Event details showing `ParentImage`, `CommandLine`, `User`, and `Hashes`.

The screenshots establish that Sysmon captured process, Registry, and DNS telemetry. No screenshot paths were recorded in the source journal, so links are not asserted here.

## Challenges and Troubleshooting

| Problem | Investigation | Resolution or status |
|---|---|---|
| Expected Sysmon Event ID 3 was missing for the `curl.exe` test. | The Sysmon Operational log was reviewed after Event ID 1 and Event ID 22 were observed for the activity. No associated Event ID 3 network connection record was found. | Unresolved. The absence was preserved as a finding; the active Sysmon configuration and any network-event filters should be reviewed in a future session. |

## Findings and Analyst Notes

- **Observed:** Sysmon recorded execution of `curl.exe` as Event ID 1 and associated DNS activity as Event ID 22.
- **Observed:** No Event ID 3 network connection event associated with the `curl.exe` test appeared in the Sysmon Operational log.
- **Interpretation:** The Event ID 1 and Event ID 22 records demonstrate that process and DNS activity can be correlated using timestamps, process IDs, executable paths, and related fields.
- **Interpretation:** The missing Event ID 3 may indicate that network connection events were disabled or filtered by the active Sysmon configuration. This is an investigation lead, not a confirmed root cause.

Key fields and their investigative value were:

| Field | Investigative value |
|---|---|
| `Image` | Identifies the executable. |
| `CommandLine` | Shows how the process was executed. |
| `ParentImage` | Identifies the process that launched it. |
| `User` | Identifies the account associated with the activity. |
| `Hashes` | Provides file hashes for indicator or reputation analysis. |
| `ProcessId` | Helps correlate activity involving a process. |
| `DestinationIp` | Identifies remote network destinations when network telemetry is available. |
| `QueryName` | Identifies domains requested by a process. |
| `TargetObject` | Identifies Registry objects being modified. |

Analyst takeaways:

- Sysmon provides endpoint context beyond basic process observation.
- Event ID 1 reveals both the executable and how it was launched.
- Parent-child relationships and command-line arguments add important investigation context.
- Event ID 13 supports investigation of Registry modifications.
- Event ID 22 can associate DNS activity with a specific process.
- Missing expected telemetry should be documented and investigated rather than ignored.

## Decisions

- The Sysmon configuration was not changed during the investigation, preserving the observed state and preventing the missing Event ID 3 from being obscured by an untracked configuration change.
- The missing Event ID 3 was recorded as an unresolved finding for later configuration and filtering analysis.
- Process, DNS, and Registry observations were treated as investigative evidence; no individual event was treated as proof of malicious activity.

## Skills Demonstrated

- Sysmon event analysis
- Windows Event Viewer
- Process investigation
- Registry investigation
- DNS investigation
- Event correlation
- Evidence collection
- SOC documentation
- Troubleshooting missing telemetry

## Current Status

| Component | Status |
|---|---|
| Sysmon process-event review | Complete |
| Registry-event review | Complete |
| DNS-event review | Complete |
| `curl.exe` Event ID 1 to Event ID 22 correlation | Complete |
| Evidence collection | Complete |
| Event ID 3 network connection validation | Unresolved |
| Day 4 lab | Complete |

## Next Steps

1. Review the active Sysmon configuration to determine whether Event ID 3 network connection telemetry is enabled.
2. Check whether network connection events are excluded by configuration filters.
3. Repeat the `curl.exe` test after configuration review and verify whether Event ID 3 is generated.

---

[← Previous day](Day03.md) · [Documentation index](README.md) · [Next day →](Day05.md)
