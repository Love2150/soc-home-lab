# Day 9 — Kerberos Authentication Monitoring and Custom Wazuh Detection

## Objective

The goal of Day 9 was to move beyond basic successful-logon monitoring and investigate **Kerberos authentication activity** on the domain controller.

The lab focused on tracing:

```text
SOCLAB\SOCAdmin
        ↓
Kerberos TGT request
        ↓
WINSRV-DC01 Event ID 4768
        ↓
Wazuh ingestion
        ↓
Custom detection rule
        ↓
Visible SIEM alert
```

This became the first day where we not only investigated telemetry, but also identified a detection gap and created a working custom Wazuh rule to close it.

---

## Lab Environment

```text
User:
SOCLAB\SOCAdmin

Client:
WIN11-CLIENT01
192.168.122.190

Domain Controller:
WINSRV-DC01
192.168.122.129

Domain:
soclab.local

Wazuh Manager:
TrashPanda
192.168.122.1
```

---

# Crawl — Generate Kerberos Activity

To deliberately create a fresh Kerberos authentication event, the workstation ticket cache was cleared.

On `WIN11-CLIENT01`:

```powershell
klist purge
```

Then a domain resource was accessed:

```powershell
dir \\WINSRV-DC01\SYSVOL
```

The idea was simple:

```text
Clear cached Kerberos tickets
        ↓
Access domain resource
        ↓
Windows must request new Kerberos tickets
```

---

# Initial Wazuh Search

The first Wazuh search was:

```text
agent.name:"WINSRV-DC01" AND data.win.system.eventID:4768
```

No results appeared in Threat Hunting.

This initially suggested that the Kerberos TGT event might not be reaching Wazuh.

---

# Verify the Event Exists on the Domain Controller

Before changing Wazuh, the event was checked locally on `WINSRV-DC01`.

Command:

```powershell
Get-WinEvent -FilterHashtable @{
    LogName='Security'
    Id=4768
} -MaxEvents 10 | Select-Object TimeCreated,Id,Message
```

The domain controller showed multiple:

```text
Event ID 4768
A Kerberos authentication ticket (TGT) was requested.
```

This proved that:

```text
Windows auditing was working
Kerberos activity was being generated
Event 4768 existed locally
```

So the problem was not Active Directory or Windows auditing.

---

# Verify Wazuh Security Log Collection

The Wazuh agent configuration on `WINSRV-DC01` was checked.

The agent contained:

```xml
<location>Security</location>
<log_format>eventchannel</log_format>
```

The Security channel was therefore being collected.

The existing query did not exclude Event ID 4768.

This eliminated the Wazuh agent Security-channel filter as the cause.

---

# Raw Event Archiving Test

Wazuh raw-event archiving was initially disabled:

```xml
<logall>no</logall>
<logall_json>no</logall_json>
```

For troubleshooting, JSON raw archiving was temporarily enabled:

```xml
<logall_json>yes</logall_json>
```

The Wazuh manager was restarted.

Then another Kerberos request was generated from `WIN11-CLIENT01`.

The raw archive was searched:

```bash
sudo grep '"eventID":"4768"' /var/ossec/logs/archives/archives.json
```

A real Event ID 4768 was found from `WINSRV-DC01`, proving that Wazuh was receiving the event.

---

# Important Fields from Event 4768

The raw event contained:

```text
eventID: 4768
targetUserName: SOCAdmin
targetDomainName: SOCLAB.LOCAL
serviceName: krbtgt
status: 0x0
ticketEncryptionType: 0x12
preAuthType: 2
ipAddress: ::ffff:192.168.122.190
```

The event was generated on:

```text
WINSRV-DC01
```

for:

```text
SOCLAB\SOCAdmin
```

and originated from:

```text
192.168.122.190
```

which is `WIN11-CLIENT01`.

The IPv4-mapped IPv6 form appeared as:

```text
::ffff:192.168.122.190
```

---

# Understanding Event ID 4768

Event ID `4768` means:

```text
A Kerberos authentication ticket (TGT) was requested.
```

The service name:

```text
krbtgt
```

confirms that this is a Ticket Granting Ticket request.

The result:

```text
status: 0x0
```

indicates the request succeeded.

So the authentication chain was:

```text
SOCAdmin
    ↓
WIN11-CLIENT01
    ↓
Requests TGT
    ↓
WINSRV-DC01
    ↓
Event ID 4768
    ↓
Successful Kerberos TGT issuance
```

---

# Detection Gap Identified

Even though Wazuh was receiving Event ID 4768, there was no visible alert in Threat Hunting.

This revealed an important distinction:

```text
Event ingestion
≠
Alert generation
```

The event existed in the raw archives, but no Wazuh rule was generating an alert for it.

This became a detection-engineering exercise.

---

# Custom Wazuh Rule — First Attempt

A custom rule was created using rule ID:

```text
100100
```

Several versions were tested.

Initial attempts used:

```xml
<if_sid>60000</if_sid>
```

and later:

```xml
<if_sid>60001</if_sid>
```

These did not produce the desired live alert.

The Windows ruleset was inspected:

```bash
sudo sed -n '1,35p' /var/ossec/ruleset/rules/0575-win-base_rules.xml
```

This showed:

```text
60000 = Windows EventChannel base rule
60001 = Windows Security channel parent
```

---

# Wazuh Logtest

The rule was tested with:

```bash
sudo /var/ossec/bin/wazuh-logtest -v
```

The event decoded into fields such as:

```text
win.system.eventID: 4768
win.system.channel: Security
win.eventdata.targetUserName: SOCAdmin
win.eventdata.serviceName: krbtgt
win.eventdata.status: 0x0
win.eventdata.ipAddress: ::ffff:192.168.122.190
```

The debugging output confirmed that Wazuh was loading rule `100100`, but earlier versions were not matching.

The final simplified rule was then created.

---

# Final Working Rule

The working custom rule became:

```xml
<group name="windows,windows_security,">

  <rule id="100100" level="7">
    <if_sid>60103</if_sid>
    <field name="win.system.eventID">^4768$</field>
    <description>Kerberos TGT requested for $(win.eventdata.targetUserName) from $(win.eventdata.ipAddress)</description>
    <group>authentication_success,kerberos,</group>
  </rule>

</group>
```

The Wazuh alert threshold was checked:

```bash
sudo grep -n 'log_alert_level' /var/ossec/etc/ossec.conf
```

Result:

```text
<log_alert_level>3</log_alert_level>
```

The custom rule level was:

```text
7
```

so it was above the configured alert threshold.

---

# Rule Validation

The rule file was tested:

```bash
sudo /var/ossec/bin/wazuh-analysisd -t
```

No errors were returned.

The manager was restarted:

```bash
sudo systemctl restart wazuh-manager
sudo systemctl is-active wazuh-manager
```

Result:

```text
active
```

---

# Successful Custom Detection

Another Kerberos request was generated:

```powershell
klist purge
dir \\WINSRV-DC01\SYSVOL
```

The raw archive then showed the event being processed by the custom rule:

```text
rule.id: 100100
rule.level: 7
description:
Kerberos TGT requested for SOCAdmin from ::ffff:192.168.122.190
```

The alert was also present in:

```text
/var/ossec/logs/alerts/alerts.json
```

with:

```text
agent.name: WINSRV-DC01
eventID: 4768
targetUserName: SOCAdmin
serviceName: krbtgt
status: 0x0
```

This confirmed that the custom rule was fully operational.

---

# Final Detection Chain

```text
WIN11-CLIENT01
192.168.122.190
        ↓
SOCLAB\SOCAdmin
        ↓
klist purge
        ↓
Access \\WINSRV-DC01\SYSVOL
        ↓
Kerberos TGT requested
        ↓
WINSRV-DC01 Event ID 4768
        ↓
Wazuh agent forwards event
        ↓
Wazuh manager receives event
        ↓
Custom rule 100100 matches
        ↓
Level 7 alert generated
        ↓
Visible in alerts.json / Wazuh
```

---

# Analyst Interpretation

The observed event represents a successful Kerberos Ticket Granting Ticket request for:

```text
SOCLAB\SOCAdmin
```

The request originated from:

```text
192.168.122.190
```

which is `WIN11-CLIENT01`.

The request was processed by:

```text
WINSRV-DC01
```

The service requested was:

```text
krbtgt
```

and:

```text
status: 0x0
```

indicates the authentication was successful.

No evidence in the reviewed event indicated failed authentication or malicious Kerberos activity.

---

# Key SOC Lessons

Day 9 introduced several important SOC and detection-engineering concepts:

- A Windows event can exist without generating a SIEM alert.
- Raw event ingestion and alert generation are separate stages.
- Always verify the source event before troubleshooting the SIEM.
- Raw archives can help prove whether telemetry is reaching the manager.
- Custom detection rules can close visibility gaps.
- `wazuh-logtest` is useful for rule debugging.
- Parent-rule relationships matter in Wazuh.
- Event ID `4768` tracks Kerberos TGT requests.
- `krbtgt` identifies Ticket Granting Ticket activity.
- `status: 0x0` indicates a successful request.
- Source IP correlation can identify the originating workstation.
- Detection engineering requires testing the full path from event generation to alert creation.

---

# Breakout — Troubleshooting a Missing SIEM Alert

Use this sequence:

```text
SOURCE → COLLECTION → INGESTION → DECODING → RULE → ALERT
```

### Questions to Ask

1. Did the source system generate the event?
2. Is the Wazuh agent collecting the correct log channel?
3. Did the event reach the Wazuh manager?
4. Were the expected fields decoded?
5. Did a rule match the event?
6. Was the alert level high enough to be logged?
7. Is the alert visible in `alerts.json`?
8. Is the dashboard indexing and displaying it?

This is the same troubleshooting process used during Day 9.

---

# Day 9 Completion Status

| Objective | Status |
|---|---|
| Generate fresh Kerberos authentication activity | ✅ Complete |
| Verify Event ID 4768 on domain controller | ✅ Complete |
| Confirm Security channel collection | ✅ Complete |
| Prove Wazuh raw ingestion | ✅ Complete |
| Identify missing-alert visibility gap | ✅ Complete |
| Create custom Wazuh rule | ✅ Complete |
| Debug rule using wazuh-logtest | ✅ Complete |
| Generate live Rule 100100 alert | ✅ Complete |
| Identify source workstation | ✅ Complete |
| Interpret Kerberos TGT request | ✅ Complete |

---

# Detection Created

```text
Rule ID: 100100
Level: 7
Description:
Kerberos TGT requested for SOCAdmin from ::ffff:192.168.122.190
```

This rule should remain in the lab as part of the growing custom detection library.

---

# Cleanup

Raw JSON archiving was enabled temporarily for troubleshooting.

After validating the detection, return:

```xml
<logall_json>no</logall_json>
```

and restart:

```bash
sudo systemctl restart wazuh-manager
```

This prevents unnecessary disk growth from storing every raw event.

---

# Stopping Point

Day 9 ended with a functioning custom Kerberos detection.

The lab can now:

```text
Generate Kerberos activity
        ↓
Capture Event ID 4768
        ↓
Send it to Wazuh
        ↓
Match custom Rule 100100
        ↓
Generate a Level 7 alert
        ↓
Investigate the user and source system
```

This is the first completed **custom detection-engineering workflow** in the SOC home lab.
