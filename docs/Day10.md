# Day 10 — Kerberos Service Ticket Investigation and Authentication Correlation

## Objective

Day 10 continued the Kerberos investigation from Day 9 by focusing on **Event ID 4769**, which records a Kerberos service ticket request.

The intended authentication chain was:

```text
SOCAdmin
   ↓
4768 — Kerberos TGT requested
   ↓
4769 — Kerberos service ticket requested
   ↓
4624 — Successful authenticated session
```

The main SOC skill was **correlating authentication events** using usernames, source IPs, systems, timestamps, and shared identifiers when available.

---

## Lab Environment

```text
Domain:
soclab.local

User:
SOCLAB\SOCAdmin

Client:
WIN11-CLIENT01
192.168.122.190

Domain Controller:
WINSRV-DC01
192.168.122.129

Wazuh Manager:
TrashPanda
192.168.122.1
```

---

## Crawl — Confirm Event ID 4769 Exists

On `WINSRV-DC01`:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Security'
    Id=4769
} -MaxEvents 10 | Select-Object TimeCreated, Id, Message
```

Multiple Event ID `4769` entries were returned.

Event 4769 means:

```text
A Kerberos service ticket was requested.
```

This confirmed the domain controller was generating the required Kerberos service-ticket telemetry.

---

## First 4769 Review

The newest event was expanded with:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Security'
    Id=4769
} -MaxEvents 1 | Format-List *
```

It showed:

```text
Account Name: Administrator@SOCLAB.LOCAL
Service Name: WINSRV-DC01$
Client Address: ::1
Failure Code: 0x0
```

### Analyst Interpretation

`::1` is the IPv6 loopback address, so this event represented **local domain-controller Kerberos activity**, not the remote SOCAdmin workstation activity we were investigating.

This was an important filtering lesson: not every 4769 event on the DC represents remote user activity.

---

## Generate Fresh SOCAdmin Kerberos Activity

On `WIN11-CLIENT01`, while logged in as `SOCLAB\SOCAdmin`:

```powershell
klist purge
dir \\WINSRV-DC01\SYSVOL
```

A matching 4769 event was then found on `WINSRV-DC01`.

Important fields:

```text
Account Name: SOCAdmin@SOCLAB.LOCAL
Service Name: WINSRV-DC01$
Client Address: ::ffff:192.168.122.190
Failure Code: 0x0
Ticket Encryption Type: 0x12
```

### Interpretation

`SOCAdmin@SOCLAB.LOCAL` identified the user.

`::ffff:192.168.122.190` is an IPv4-mapped IPv6 address representing:

```text
192.168.122.190
WIN11-CLIENT01
```

`WINSRV-DC01$` identified the target service/computer account associated with the requested Kerberos service ticket.

`Failure Code: 0x0` indicated a successful service-ticket request.

---

## Understanding Event ID 4769

Event ID `4769` represents a request for a Kerberos **service ticket**.

The Kerberos flow can be simplified as:

```text
User authenticates
        ↓
4768 — TGT requested
        ↓
User receives TGT
        ↓
4769 — Service ticket requested
        ↓
User accesses target resource/service
```

Day 9 focused on the TGT.

Day 10 focused on the service ticket used to access a specific resource or system.

---

## Wazuh Verification

Wazuh raw archives already contained valid 4769 events from `SOCAdmin`.

A known-good event contained:

```text
eventID: 4769
targetUserName: SOCAdmin@SOCLAB.LOCAL
targetDomainName: SOCLAB.LOCAL
serviceName: WINSRV-DC01$
ipAddress: ::ffff:192.168.122.190
status: 0x0
```

This proved that Wazuh had ingested workstation-generated 4769 events successfully.

---

## Built-In Wazuh Detection

Wazuh already had built-in detection coverage for successful 4769 events.

The relevant built-in rule was:

```text
Rule ID: 60106
Description: Windows Logon Success
Level: 3
Group: authentication_success
```

Recent 4769 events in `alerts.json` showed:

```text
rule.id: 60106
eventID: 4769
```

This demonstrated that a custom rule was not required for basic successful 4769 visibility.

---

## Distinguishing DC-Local Noise

Recent 4769 alerts in Wazuh mostly showed:

```text
targetUserName: WINSRV-DC01$@SOCLAB.LOCAL
ipAddress: ::1
```

or:

```text
targetUserName: Administrator@SOCLAB.LOCAL
ipAddress: ::1
```

These represented local DC Kerberos activity.

This introduced an important SOC filtering lesson:

```text
4769 by itself is not enough.
```

The analyst should also examine:

```text
targetUserName
ipAddress
serviceName
status
timestamp
```

---

## Direct Service Ticket Request Test

To force a specific Kerberos service-ticket request, the workstation used:

```powershell
klist purge
klist get cifs/WINSRV-DC01.soclab.local
```

The purpose was to explicitly request a CIFS/SMB service ticket instead of relying only on normal Windows behavior.

---

## Event Record Correlation Attempt

On `WINSRV-DC01`, a fresh SOCAdmin 4769 event was found with:

```text
TimeCreated: 9/30/2026 9:16:20 AM
RecordId: 7108

Account Name: SOCAdmin@SOCLAB.LOCAL
Service Name: WINSRV-DC01$
Client Address: ::ffff:192.168.122.190
Failure Code: 0x0
```

The Wazuh manager was searched for that exact Event Record ID:

```bash
sudo grep '"eventRecordID":"7108"' /var/ossec/logs/alerts/alerts.json
```

and:

```bash
sudo grep '"eventRecordID":"7108"' /var/ossec/logs/archives/archives.json
```

No matching Wazuh entry was returned.

---

## Verify Wazuh Agent Health

The DC agent was checked with:

```bash
sudo /var/ossec/bin/agent_control -lc
```

Result:

```text
ID: 002
Name: WINSRV-DC01
Active
```

Fresh events from the DC were also present in Wazuh, including:

```text
4624 — Windows Logon Success
4634 — Windows User Logoff
```

This proved that the agent itself was healthy and that Security events were still flowing.

---

## Temporary Raw Archive Troubleshooting

Raw JSON archiving was temporarily re-enabled:

```xml
<logall_json>yes</logall_json>
```

After restarting the Wazuh manager, the raw archive was searched for 4769 events from:

```text
192.168.122.190
```

The archive returned known-good historical SOCAdmin 4769 events, confirming successful ingestion had occurred previously.

---

## Logon GUID Correlation Attempt

One known-good SOCAdmin 4769 event had this Logon GUID:

```text
{b8ea3d23-5af8-ea2c-b05f-dc7a2051ba09}
```

The Wazuh archives and alerts were searched for the same GUID:

```bash
sudo grep 'b8ea3d23-5af8-ea2c-b05f-dc7a2051ba09' /var/ossec/logs/alerts/alerts.json
```

and:

```bash
sudo grep 'b8ea3d23-5af8-ea2c-b05f-dc7a2051ba09' /var/ossec/logs/archives/archives.json
```

Only the 4769 event was returned.

A matching 4624 with the same Logon GUID was not found in the available Wazuh dataset.

---

## Final Correlation Result

The exact 4769-to-4624 correlation by shared Logon GUID was **not proven** in the available data.

However, the overall authentication chain was supported by the environment and previously observed telemetry:

```text
SOCAdmin on WIN11-CLIENT01
        ↓
4768 — TGT requested
        ↓
4769 — Service ticket requested
        ↓
Target: WINSRV-DC01$
        ↓
4624 — Successful Kerberos network logon observed separately
```

The correlation was based on:

```text
User: SOCAdmin
Source: 192.168.122.190
Domain: SOCLAB.LOCAL
Target: WINSRV-DC01
Authentication: Kerberos
Timing: closely related authentication activity
```

---

## Key SOC Lessons

- Event ID `4769` records Kerberos service-ticket requests.
- Not every 4769 event represents remote user activity.
- `::1` identifies local loopback activity on the DC.
- `::ffff:192.168.122.190` represents the Windows client.
- `Failure Code: 0x0` means the ticket request succeeded.
- `serviceName` identifies the target service or computer account.
- Wazuh built-in rule `60106` can alert on successful 4769 events.
- A SIEM may contain large amounts of normal Kerberos background activity.
- User, IP, service, target host, and time are important correlation pivots.
- Shared identifiers such as Logon GUID can improve correlation when available.
- A missing shared GUID match does not automatically invalidate the broader authentication story.
- SOC analysts should distinguish confirmed facts from inferred correlations.

---

## Investigation Model

```text
Generate Activity
      ↓
Verify Event on Source
      ↓
Identify User
      ↓
Identify Source IP
      ↓
Identify Service
      ↓
Check Success/Failure
      ↓
Verify SIEM Ingestion
      ↓
Correlate with Related Events
```

---

## Analyst Summary

A successful Kerberos service-ticket request was observed for:

```text
SOCAdmin@SOCLAB.LOCAL
```

from:

```text
192.168.122.190
WIN11-CLIENT01
```

targeting:

```text
WINSRV-DC01$
```

with:

```text
Failure Code: 0x0
```

The activity was consistent with expected domain authentication behavior.

Wazuh already had built-in visibility for successful 4769 events through rule `60106`.

The exact Logon GUID correlation between a 4769 event and a corresponding 4624 event was not demonstrated in the available Wazuh data, so the final authentication chain was correlated using user, host, source IP, Kerberos context, and timing.

No evidence reviewed during Day 10 indicated clearly malicious Kerberos activity.

---

## Day 10 Completion Status

```text
[✓] Verified Event ID 4769 generation
[✓] Reviewed full 4769 event
[✓] Distinguished local DC activity from workstation activity
[✓] Identified SOCAdmin service-ticket request
[✓] Identified source workstation
[✓] Interpreted Service Name
[✓] Interpreted Failure Code 0x0
[✓] Confirmed Wazuh 4769 visibility
[✓] Identified built-in Wazuh Rule 60106
[✓] Attempted Event Record ID correlation
[✓] Verified Wazuh DC agent health
[✓] Attempted Logon GUID correlation
[✓] Documented exact evidence vs inferred correlation
```

---

## Day 10 Stopping Point

Day 10 ended with the ability to explain the Kerberos authentication sequence:

```text
4768
TGT requested
        ↓
4769
Service ticket requested
        ↓
4624
Successful authenticated session
```

The main improvement over Day 9 was learning how to separate useful user-generated Kerberos activity from background domain-controller authentication noise and how to correlate activity across multiple authentication events.
