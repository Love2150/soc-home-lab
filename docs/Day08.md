# Day 8 — Multi-Host Authentication Correlation in Wazuh

## Objective

The goal for Day 8 was to move beyond single-endpoint investigation and begin correlating the same user activity across multiple systems.

The lab focused on:

- `WIN11-CLIENT01` as the workstation
- `WINSRV-DC01` as the domain controller
- Wazuh as the central SIEM
- `SOCLAB\SOCAdmin` as the domain user being investigated

This was the first point in the lab where authentication activity was traced across both an endpoint and Active Directory infrastructure.

---

## Lab Environment

```text
Wazuh Manager
192.168.122.1

WIN11-CLIENT01
192.168.122.190
Wazuh Agent ID: 001

WINSRV-DC01
192.168.122.129
Wazuh Agent ID: 002

Domain:
soclab.local

Domain User:
SOCLAB\SOCAdmin
```

Both Wazuh agents were confirmed active:

```text
ID: 001, Name: WIN11-CLIENT01, Active
ID: 002, Name: WINSRV-DC01, Active
```

---

# Part 1 — Verify Domain Controller Telemetry

In Wazuh Threat Hunting, the domain controller was filtered with:

```text
agent.name:"WINSRV-DC01"
```

The DC immediately showed Windows Security telemetry, including:

```text
Windows Logon Success
Windows User Logoff
```

This confirmed that `WINSRV-DC01` was successfully forwarding its Windows Security Event Channel into Wazuh.

Because the events were already present, no additional `ossec.conf` changes were required.

---

# Part 2 — Identify the Workstation Logon

The first event of interest was located on:

```text
WIN11-CLIENT01
```

The event contained:

```text
Event ID: 4624
Channel: Security
Target User: SOCAdmin
Target Domain: SOCLAB
Workstation: WIN11-CLIENT01
Computer: WIN11-CLIENT01.soclab.local
```

### Event ID 4624

Windows Event ID `4624` indicates:

```text
An account was successfully logged on.
```

This confirmed that:

```text
SOCLAB\SOCAdmin
```

successfully established a session on `WIN11-CLIENT01`.

---

# Part 3 — Pivot to the Domain Controller

The next investigation step was to search for the same username on the DC:

```text
agent.name:"WINSRV-DC01" AND data.win.eventdata.targetUserName:"SOCAdmin"
```

An initial event found was:

```text
Event ID: 4634
Target User: SOCAdmin
Target Domain: SOCLAB
Logon Type: 3
Computer: WINSRV-DC01.soclab.local
```

### Event ID 4634

Event `4634` represents:

```text
An account was logged off.
```

This was useful because it confirmed that `SOCAdmin` had an authenticated session involving the DC, but it did not represent the original successful authentication.

---

# Part 4 — Find the Successful DC Logon

A matching successful authentication event was then located on `WINSRV-DC01`.

The event contained:

```text
Event ID: 4624
Target User: SOCAdmin
Target Domain: SOCLAB.LOCAL
Logon Type: 3
Logon Process: Kerberos
Authentication Package: Kerberos
Channel: Security
Rule Description: Windows Logon Success
```

The Windows message stated:

```text
An account was successfully logged on.
```

---

# Understanding Logon Type 3

The DC-side event used:

```text
Logon Type: 3
```

Logon Type 3 represents a:

```text
Network logon
```

This does **not** mean that `SOCAdmin` physically logged into the domain controller.

Instead, it shows that the account established an authenticated network session involving the DC.

That distinction is important during SOC investigations.

---

# Understanding Kerberos

The event showed:

```text
Logon Process: Kerberos
Authentication Package: Kerberos
```

This is consistent with authentication inside an Active Directory environment.

The authentication chain observed was therefore:

```text
SOCLAB\SOCAdmin
       |
       v
WIN11-CLIENT01
Event ID 4624
Successful workstation logon
       |
       | Domain authentication activity
       v
WINSRV-DC01
Event ID 4624
Logon Type 3
Kerberos
Successful network session
       |
       v
WINSRV-DC01
Event ID 4634
Session logged off
```

---

# Why This Matters to a SOC Analyst

Previously, investigations in the lab were mostly endpoint-focused.

Day 8 demonstrated that one user action can produce evidence across multiple systems.

For example:

```text
Endpoint
↓
User logged into workstation

Domain Controller
↓
Domain account generated authentication activity

SIEM
↓
Both events become searchable and correlatable
```

A SOC analyst should not assume that one alert or one event contains the entire story.

Instead, an investigation may require pivoting between:

- username
- hostname
- source IP
- destination system
- logon type
- authentication method
- event ID
- timestamps

---

# Important Event IDs Reviewed

| Event ID | Meaning |
|---|---|
| 4624 | Successful logon |
| 4634 | Account logged off |
| 4768 | Kerberos TGT requested |
| 4769 | Kerberos service ticket requested |
| 4776 | NTLM credential validation |

We successfully observed `4624` and `4634`.

The next phase of the lab was to investigate `4768` and `4769` so the Kerberos ticket process itself could be observed.

---

# Analyst Questions

### 1. Which user account was investigated?

```text
SOCAdmin
```

### 2. Which domain was involved?

```text
SOCLAB / soclab.local
```

### 3. Which workstation recorded the user logon?

```text
WIN11-CLIENT01
```

### 4. Which server recorded the related domain activity?

```text
WINSRV-DC01
```

### 5. What event identified the successful workstation logon?

```text
Event ID 4624
```

### 6. What logon type was observed on the domain controller?

```text
Logon Type 3
```

### 7. What does Logon Type 3 represent?

```text
A network logon.
```

### 8. Which authentication mechanism was observed?

```text
Kerberos
```

### 9. What event represented the later session termination?

```text
Event ID 4634
```

### 10. Was the observed authentication activity clearly malicious?

```text
No.
```

The reviewed telemetry was consistent with expected domain authentication activity.

---

# Analyst Conclusion

A successful logon involving the domain account `SOCLAB\SOCAdmin` was observed on `WIN11-CLIENT01`.

Related authentication activity was also identified on the domain controller `WINSRV-DC01`.

The workstation recorded Event ID `4624`, showing the successful user session.

The domain controller also recorded Event ID `4624` for `SOCAdmin`, with:

```text
Logon Type: 3
Authentication Package: Kerberos
```

This indicates a successful network-authenticated session involving the domain controller.

A corresponding `4634` event showed the later termination of a `SOCAdmin` session.

The activity reviewed during this investigation was consistent with expected Active Directory authentication behavior. No evidence reviewed during this exercise indicated a failed or clearly anomalous authentication.

---

# SOC Skill Developed

**Multi-host event correlation**

Instead of asking only:

```text
"What happened on this computer?"
```

the analyst begins asking:

```text
"What other systems should have evidence of this activity?"
```

That is an important shift from basic log review toward actual SOC investigation.

---

# Day 8 Completion Status

```text
[✓] Wazuh multi-agent environment operational
[✓] Windows workstation telemetry available
[✓] Domain controller telemetry available
[✓] Successful logon identified
[✓] User activity pivoted by username
[✓] Endpoint and DC events correlated
[✓] Logon Type 3 interpreted
[✓] Kerberos authentication identified
[✓] Benign activity classification completed
```

## Next Session

Continue with **Kerberos authentication correlation**, specifically:

```text
4768 — Kerberos TGT request
4769 — Kerberos service ticket request
```

That expands the chain from:

```text
User logon
→ workstation session
→ domain authentication
```

into:

```text
User logon
→ TGT request
→ service ticket request
→ authenticated access
```
