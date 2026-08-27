# Day 7 — Active Directory Authentication Monitoring with Wazuh

| Field | Value |
|---|---|
| Date | 2026-08-19 |
| Status | Complete |
| Phase | Crawl–Walk–Run authentication monitoring and investigation |

## Summary

Day 7 validated domain authentication on `WIN11-CLIENT01`, repaired its broken Active Directory trust relationship, generated failed and successful domain logons, and investigated both events in Wazuh. The completed path was:

```text
WIN11-CLIENT01
  ↓
soclab.local
  ↓
Domain authentication
  ↓
Windows Security events
  ↓
Wazuh Agent
  ↓
Wazuh Manager
  ↓
Threat Hunting / DQL
```

The lab stopped after the Crawl–Walk–Run authentication investigation was completed and the activity was classified as benign.

## Objectives

- [x] Verify workstation identity, domain membership, current user, and secure-channel health.
- [x] Troubleshoot and repair the broken Active Directory trust relationship.
- [x] Generate and locate a failed domain logon (`4625`) in Wazuh.
- [x] Create the `SOCAdmin` domain account.
- [x] Generate and locate a successful domain logon (`4624`) in Wazuh.
- [x] Determine whether the authentication attempts were local or remote.
- [x] Classify the observed activity using the available evidence.

## Environment

| Component | Details |
|---|---|
| Lab | SOC Home Lab |
| Primary endpoint | `WIN11-CLIENT01` |
| Domain | `soclab.local` |
| Domain controller | `WIN-06D5PF8239K` (`192.168.122.129`) |
| SIEM | Wazuh |
| Telemetry | Windows Security and Sysmon |

## Work Completed

- Confirmed that `WIN11-CLIENT01` was a member workstation in `soclab.local`.
- Identified a broken secure channel between the workstation and the domain.
- Restored domain controller availability and confirmed DNS and domain controller discovery.
- Repaired and validated the workstation's secure channel without removing and rejoining it to the domain.
- Generated a failed interactive logon for `SOCLAB\SOCAdmin` and found event ID `4625` in Wazuh.
- Determined that `SOCAdmin` did not yet exist in Active Directory, created the account, and verified it.
- Used `SOCLAB\SOCAdmin` to sign in successfully to `WIN11-CLIENT01` and found event ID `4624` in Wazuh.
- Compared the failed and successful logons with DQL and completed the authentication investigation.

## Implementation and Validation

### Crawl — Validate Domain State

The workstation identity, domain membership, current user, and secure-channel health were checked first. The observed state was:

| Item | Observed result |
|---|---|
| Computer | `WIN11-CLIENT01` |
| Domain | `soclab.local` |
| Role | `MemberWorkstation` |
| Secure channel | `False` |

The secure-channel test reported that the secure channel between the local computer and `soclab.local` was broken.

The trust issue was investigated in this order:

```text
DNS → DC → TRUST → REPAIR
```

This sequence was used to avoid immediately removing and rejoining the workstation to the domain.

#### Step 1 — DNS

The first question was whether the workstation could resolve the Active Directory domain. `WIN11-CLIENT01` was configured to use `192.168.122.129` as its DNS server. Initially, DNS requests timed out because the Windows Server/domain controller had not yet been brought back into the lab after the switch to Wazuh.

The checks considered:

- Is the domain controller powered on?
- What DNS server is the workstation using?
- Is the workstation using the domain controller as its DNS server?
- Did the domain controller IP address change?
- Is DNS available on the domain controller?

#### Step 2 — Domain Controller Discovery

After restoring domain controller availability, the workstation successfully located the domain controller. The output included:

```text
DC: \\WIN-06D5PF8239K.soclab.local
Address: \\192.168.122.129
Dom Name: soclab.local
Forest Name: soclab.local
The command completed successfully
```

If discovery had failed, the relevant questions were:

- Is DNS working?
- Can the workstation reach the domain controller?
- Is the domain controller powered on?
- Is the domain name correct?
- Is Active Directory Domain Services available?

#### Step 3 — Trust

A repeated secure-channel test returned `False`, confirming that the trust relationship itself was broken:

```text
The secure channel between the local computer and the domain soclab.local is broken.
```

#### Step 4 — Repair

The secure channel was repaired with domain administrator credentials and tested again. Validation returned:

```text
The secure channel between the local computer and the domain soclab.local is in good condition.
```

### Walk — Generate Authentication Events

The Walk phase generated and investigated both required authentication events:

- Event ID `4625`: failed logon
- Event ID `4624`: successful logon

#### Failed Authentication — Event ID 4625

A failed domain sign-in was generated for `SOCLAB\SOCAdmin` and located in Wazuh Threat Hunting. The event showed a failed interactive logon originating locally on `WIN11-CLIENT01`.

During the investigation, it was discovered that `SOCAdmin` did not yet exist in Active Directory. At that time, the domain contained:

- `Administrator`
- `Guest`
- `krbtgt`

#### Creating the SOCAdmin Domain Account

The `SOCAdmin` account was created on the domain controller and verified with `Get-ADUser SOCAdmin`. The account was then used to sign in successfully to `WIN11-CLIENT01`.

#### Successful Authentication — Event ID 4624

The successful logon was located in Wazuh. It confirmed successful domain authentication for `SOCLAB\SOCAdmin` on `WIN11-CLIENT01`.

### Run — Authentication Investigation

Wazuh recorded a failed interactive logon for `SOCLAB\SOCAdmin`, followed later by a successful interactive logon for the same account on `WIN11-CLIENT01`.

| Investigation question | Answer | Supporting evidence |
|---|---|---|
| Which account failed to authenticate? | `SOCAdmin` | Event ID `4625` and `targetUserName: SOCAdmin` |
| Which account later authenticated successfully? | `SOCAdmin` | Event ID `4624` and `targetUserName: SOCAdmin` |
| Were the attempts local or remote? | Local | `workstationName: WIN11-CLIENT01`, `ipAddress: 127.0.0.1`, `logonType: 2`, and `logonProcessName: User32` |
| What logon type was used? | `2` | Interactive/local logon |
| How should the activity be classified? | Benign | One failed interactive logon followed by a successful logon, with no additional suspicious behavior observed |

## Commands and Queries

### Domain State and Trust Troubleshooting

Run on the workstation in the following order:

```powershell
hostname
Get-ComputerInfo | Select-Object CsName,CsDomain,CsDomainRole
whoami
Test-ComputerSecureChannel -Verbose
nslookup soclab.local
ipconfig /all
nltest /dsgetdc:soclab.local
Test-ComputerSecureChannel -Verbose
Test-ComputerSecureChannel -Repair -Credential (Get-Credential SOCLAB\Administrator)
Test-ComputerSecureChannel -Verbose
```

Quick-reference sequence:

```text
DNS → DC → TRUST → REPAIR
```

Quick-reference commands:

```powershell
nslookup soclab.local
nltest /dsgetdc:soclab.local
Test-ComputerSecureChannel -Verbose
Test-ComputerSecureChannel -Repair -Credential (Get-Credential SOCLAB\Administrator)
Test-ComputerSecureChannel -Verbose
```

### Domain Account Creation and Verification

Run on the domain controller:

```powershell
New-ADUser -Name "SOCAdmin" -SamAccountName "SOCAdmin" -UserPrincipalName "SOCAdmin@soclab.local" -AccountPassword (Read-Host -AsSecureString "Enter password") -Enabled $true
Get-ADUser SOCAdmin
```

### Wazuh DQL Queries

Filter for the Windows endpoint:

```text
agent.name:"WIN11-CLIENT01"
```

Search for failed and successful logons:

```text
agent.name:"WIN11-CLIENT01" AND (data.win.system.eventID:4624 OR data.win.system.eventID:4625)
```

Search for a successful `SOCAdmin` logon:

```text
agent.name:"WIN11-CLIENT01" AND data.win.system.eventID:4624 AND data.win.eventdata.targetUserName:"SOCAdmin"
```

Search for a failed `SOCAdmin` logon:

```text
agent.name:"WIN11-CLIENT01" AND data.win.system.eventID:4625 AND data.win.eventdata.targetUserName:"SOCAdmin"
```

## Evidence

### Failed Logon

The failed authentication event contained these fields:

| Field | Value |
|---|---|
| `agent.name` | `WIN11-CLIENT01` |
| `targetDomainName` | `SOCLAB` |
| `targetUserName` | `SOCAdmin` |
| `workstationName` | `WIN11-CLIENT01` |
| `eventID` | `4625` |
| `authenticationPackageName` | `Negotiate` |
| `logonProcessName` | `User32` |
| `logonType` | `2` |
| `ipAddress` | `127.0.0.1` |

Event ID `4625` indicates a failed logon. Logon type `2` indicates an interactive/local sign-in. The loopback address `127.0.0.1` supports that the attempt originated locally on the workstation rather than from a remote system.

### Successful Logon

The successful authentication event contained these fields:

| Field | Value |
|---|---|
| `agent.name` | `WIN11-CLIENT01` |
| `targetDomainName` | `SOCLAB` |
| `targetUserName` | `SOCAdmin` |
| `workstationName` | `WIN11-CLIENT01` |
| `eventID` | `4624` |
| `authenticationPackageName` | `Negotiate` |
| `logonProcessName` | `User32` |
| `ipAddress` | `127.0.0.1` |

Event ID `4624` confirmed a successful domain authentication for `SOCLAB\SOCAdmin` on `WIN11-CLIENT01`.

## Challenges and Troubleshooting

| Problem | Investigation | Resolution or status |
|---|---|---|
| DNS requests timed out | Checked domain resolution and `ipconfig /all`; the workstation used `192.168.122.129` for DNS | The Windows Server/domain controller had not been brought back into the lab after the switch to Wazuh; restoring it allowed discovery to continue |
| Workstation secure channel was broken | Confirmed domain membership, then used `Test-ComputerSecureChannel -Verbose`, which returned `False` | Repaired with `Test-ComputerSecureChannel -Repair` and validated that the channel was in good condition |
| Failed logon involved an unavailable account | Reviewed the `4625` event and checked existing Active Directory accounts | Created and verified the `SOCAdmin` domain account, then used it for a successful sign-in |

For future broken trust relationships, the troubleshooting questions are:

1. Is the domain controller powered on and reachable?
2. What DNS server is the workstation using?
3. Can the workstation resolve the domain name?
4. Can the workstation locate a domain controller?
5. Is the workstation still joined to the domain?
6. Is the secure channel actually broken?
7. Can the secure channel be repaired without removing the machine from the domain?
8. After repair, does the secure channel test successfully?
9. Can a domain user authenticate afterward?
10. Are the authentication events visible in the SIEM?

## Findings and Analyst Notes

- The failed account was `SOCLAB\SOCAdmin`; the account did not exist in Active Directory when the failed logon was generated.
- Event ID `4625` represented the failed authentication, and event ID `4624` represented the later successful authentication.
- The `workstationName`, `127.0.0.1` loopback address, logon type `2`, and `User32` logon process supported the conclusion that the attempts were local interactive logons.
- The activity was classified as **benign**. A single failed interactive logon followed by a successful logon for the same account is consistent with normal behavior such as entering an incorrect password once and then correcting it.
- No evidence was observed in this exercise of repeated failed logons, password spraying, remote authentication, brute-force behavior, or additional suspicious activity.

### Analyst Conclusion

A failed interactive logon for `SOCLAB\SOCAdmin` was followed by a successful interactive logon on `WIN11-CLIENT01`. The activity was local, as shown by logon type `2`, the `User32` logon process, workstation `WIN11-CLIENT01`, and loopback address `127.0.0.1`. Because only one failed attempt occurred before successful authentication and no additional suspicious behavior was identified, the activity was classified as benign.

### Key Lessons

- Domain trust problems should be approached methodically.
- DNS is critical to Active Directory.
- The client must be able to locate a domain controller before domain trust can be repaired.
- Do not immediately remove and rejoin a workstation to the domain.
- Event ID `4625` represents a failed authentication.
- Event ID `4624` represents a successful authentication.
- Logon type `2` represents an interactive/local sign-in.
- A single failed logon does not automatically indicate malicious activity.
- Context determines whether authentication activity is benign or suspicious.
- Wazuh DQL can compare successful and failed logons.
- Source IP, logon type, account name, and workstation name are important authentication investigation fields.

## Decisions

- Used the `DNS → DC → TRUST → REPAIR` sequence rather than immediately removing and rejoining the workstation to the domain.
- Created `SOCAdmin` only after confirming that it did not exist in Active Directory.
- Classified the authentication sequence as benign because the available evidence showed one local failed attempt followed by a successful attempt and no further suspicious behavior.

## Skills Demonstrated

- Active Directory domain and secure-channel validation
- DNS and domain controller discovery troubleshooting
- Active Directory trust repair
- PowerShell Active Directory account administration
- Windows Security event analysis for event IDs `4624` and `4625`
- Wazuh Threat Hunting and DQL filtering
- Authentication context analysis and evidence-based classification

## Current Status

| Component | Status |
|---|---|
| Verify domain membership | Complete |
| Identify broken secure channel | Complete |
| Verify DNS | Complete |
| Locate domain controller | Complete |
| Repair domain trust | Complete |
| Generate `4625` failed logon | Complete |
| Create `SOCAdmin` domain account | Complete |
| Generate `4624` successful logon | Complete |
| Locate both events in Wazuh | Complete |
| Analyze local versus remote authentication | Complete |
| Classify activity | Complete |
| Complete Crawl–Walk–Run investigation | Complete |

The environment now has this validated flow:

```text
Active Directory
  ↓
Healthy workstation trust
  ↓
Domain authentication
  ↓
Windows Security telemetry
  ↓
Wazuh
  ↓
DQL threat hunting
  ↓
Authentication investigation
```

## Next Steps

Day 7 is complete. The stopping point is a healthy workstation trust relationship, validated domain authentication telemetry in Wazuh, and a completed benign authentication investigation. No next-day task was recorded in the source journal.

---

[← Previous day](Day06.md) · [Documentation index](README.md)
