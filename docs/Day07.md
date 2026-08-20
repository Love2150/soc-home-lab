Day 7 — Active Directory Authentication Monitoring with Wazuh

Date: August 19, 2026
Lab: SPC Home Lab
Primary Endpoint: WIN11-CLIENT01
Domain: soclab.local
Domain Controller: WIN-06D5PF8239K
SIEM: Wazuh
Telemetry: Windows Security + Sysmon


⸻


Day 7 Objective

The goal of Day 7 was to validate domain authentication on WIN11-CLIENT01, repair the broken Active Directory trust relationship, generate failed and successful domain logons, and investigate both events in Wazuh.

By the end of the lab, the following path was validated:

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


⸻


Crawl — Validate Domain State

The first step was to verify the workstation identity, domain membership, current user, and secure-channel health.

Commands used:

hostname

Get-ComputerInfo | Select-Object CsName,CsDomain,CsDomainRole

whoami

Test-ComputerSecureChannel -Verbose

Observed results:

Computer: WIN11-CLIENT01

Domain: soclab.local

Role: MemberWorkstation

The secure-channel test returned:

False

The workstation reported that the secure channel between the local computer and soclab.local was broken.


⸻


Breakout — Troubleshooting a Broken Active Directory Trust Relationship

Memory Aid

Use this sequence:

DNS → DC → TRUST → REPAIR

The goal is to troubleshoot in order instead of immediately removing and rejoining the workstation to the domain.


⸻


Step 1 — DNS

Question to Ask

Can the workstation resolve the Active Directory domain?

Run:

nslookup soclab.local

Also check the workstation’s network configuration:

ipconfig /all

Questions to ask:

    Is the domain controller powered on?
    What DNS server is the workstation using?
    Is the workstation using the domain controller as its DNS server?
    Did the domain controller IP address change?
    Is DNS available on the domain controller?

During this lab, WIN11-CLIENT01 was configured to use:

DNS Server: 192.168.122.129

Initially, DNS requests timed out because the Windows Server/domain controller had not yet been brought back into the lab after the switch to Wazuh.


⸻


Step 2 — Domain Controller Discovery

Question to Ask

Can the workstation locate a domain controller?

Run:

nltest /dsgetdc:soclab.local

Successful output included:

DC: \\WIN-06D5PF8239K.soclab.local

Address: \\192.168.122.129

Dom Name: soclab.local

Forest Name: soclab.local

The command completed successfully

Questions to ask if it fails:

    Is DNS working?
    Can the workstation reach the domain controller?
    Is the domain controller powered on?
    Is the domain name correct?
    Is Active Directory Domain Services available?


⸻


Step 3 — Trust

Question to Ask

Is the secure channel between the workstation and Active Directory healthy?

Run:

Test-ComputerSecureChannel -Verbose

Broken result:

False

or:

The secure channel between the local computer and the domain soclab.local is broken.


⸻


Step 4 — Repair

Question to Ask

Can the trust relationship be repaired without removing the workstation from the domain?

Run:

Test-ComputerSecureChannel -Repair -Credential (Get-Credential SOCLAB\Administrator)

Then verify:

Test-ComputerSecureChannel -Verbose

Successful result:

The secure channel between the local computer and the domain soclab.local is in good condition.


⸻


Active Directory Trust Troubleshooting Questions

When dealing with a broken trust relationship, work through these questions in order:

    Is the domain controller powered on and reachable?
    What DNS server is the workstation using?
    Can the workstation resolve the domain name?
    Can the workstation locate a domain controller?
    Is the workstation still joined to the domain?
    Is the secure channel actually broken?
    Can the secure channel be repaired without removing the machine from the domain?
    After repair, does the secure channel test successfully?
    Can a domain user authenticate afterward?
    Are the authentication events visible in the SIEM?

Quick Reference

DNS → DC → TRUST → REPAIR

Commands:

nslookup soclab.local

nltest /dsgetdc:soclab.local

Test-ComputerSecureChannel -Verbose

Test-ComputerSecureChannel -Repair -Credential (Get-Credential SOCLAB\Administrator)

Test-ComputerSecureChannel -Verbose


⸻


Walk — Generate Authentication Events

The goal of the Walk section was to generate both:

4625 = Failed logon

4624 = Successful logon

and investigate them in Wazuh.


⸻


Failed Authentication — Event ID 4625

A failed domain sign-in was generated for:

SOCLAB\SOCAdmin

The event was located in Wazuh Threat Hunting.

Relevant fields observed:

agent.name: WIN11-CLIENT01

targetDomainName: SOCLAB

targetUserName: SOCAdmin

workstationName: WIN11-CLIENT01

eventID: 4625

authenticationPackageName: Negotiate

logonProcessName: User32

logonType: 2

ipAddress: 127.0.0.1

Analyst Interpretation

4625 indicates a failed logon.

Logon Type 2 indicates an interactive or local sign-in.

The source address:

127.0.0.1

is the loopback address and supports that the sign-in attempt originated locally on the workstation rather than from a remote system.

The failed account was:

SOCLAB\SOCAdmin

During the investigation, it was discovered that SOCAdmin did not yet exist in Active Directory.

The domain initially contained:

Administrator

Guest

krbtgt


⸻


Creating the SOCAdmin Domain Account

The SOCAdmin account was created on the domain controller.

Single-line PowerShell command:

New-ADUser -Name "SOCAdmin" -SamAccountName "SOCAdmin" -UserPrincipalName "SOCAdmin@soclab.local" -AccountPassword (Read-Host -AsSecureString "Enter password") -Enabled $true

Verify the account:

Get-ADUser SOCAdmin

The account was then used to successfully sign in to WIN11-CLIENT01.


⸻


Successful Authentication — Event ID 4624

The successful login was located in Wazuh.

Relevant fields observed:

agent.name: WIN11-CLIENT01

targetDomainName: SOCLAB

targetUserName: SOCAdmin

workstationName: WIN11-CLIENT01

eventID: 4624

authenticationPackageName: Negotiate

logonProcessName: User32

ipAddress: 127.0.0.1

This confirmed a successful domain authentication for:

SOCLAB\SOCAdmin

on:

WIN11-CLIENT01


⸻


Wazuh DQL Queries Used

Filter for the Windows endpoint:

agent.name:"WIN11-CLIENT01"

Search for both failed and successful logons:

agent.name:"WIN11-CLIENT01" AND (data.win.system.eventID:4624 OR data.win.system.eventID:4625)

Search for a successful SOCAdmin login:

agent.name:"WIN11-CLIENT01" AND data.win.system.eventID:4624 AND data.win.eventdata.targetUserName:"SOCAdmin"

Search for a failed SOCAdmin login:

agent.name:"WIN11-CLIENT01" AND data.win.system.eventID:4625 AND data.win.eventdata.targetUserName:"SOCAdmin"


⸻


Run — Authentication Investigation

Scenario

Wazuh recorded a failed interactive logon for SOCLAB\SOCAdmin, followed later by a successful interactive logon for the same account on WIN11-CLIENT01.

Investigation Questions

1. Which account failed to authenticate?

SOCAdmin

2. Which account later authenticated successfully?

SOCAdmin

3. Were the attempts local or remote? What fields support the conclusion?

Local

Supporting evidence:

workstationName: WIN11-CLIENT01

ipAddress: 127.0.0.1

logonType: 2

logonProcessName: User32

4. What logon type was used?

2

Interpretation:

Interactive / local logon

5. How should the activity be classified?

Benign

Reasoning

A single failed interactive logon followed by a successful login for the same account is consistent with normal user behavior such as entering the wrong password once and then correcting it.

There was no evidence in this exercise of:

Repeated failed logons

Password spraying

Remote authentication

Brute-force behavior

Additional suspicious activity


⸻


Analyst Conclusion

A failed interactive logon for SOCLAB\SOCAdmin was followed by a successful interactive logon on WIN11-CLIENT01.

The activity was local, as shown by:

Logon Type 2

User32 logon process

WIN11-CLIENT01 workstation

127.0.0.1 loopback address

Because only one failed attempt occurred before the successful authentication and no additional suspicious behavior was identified, the activity is best classified as:

Benign


⸻


Key Lessons

    Domain trust problems should be approached methodically.
    DNS is critical to Active Directory.
    The client must be able to locate a domain controller before repairing domain trust.
    Do not immediately remove and rejoin a workstation to the domain.
    Event ID 4625 represents a failed authentication.
    Event ID 4624 represents a successful authentication.
    Logon Type 2 represents an interactive/local sign-in.
    A single failed login does not automatically indicate malicious activity.
    Context determines whether authentication activity is benign or suspicious.
    Wazuh DQL can be used to compare successful and failed logons.
    Source IP, logon type, account name, and workstation name are important authentication investigation fields.


⸻


Day 7 Completion Status

Objective
	

Status

Verify domain membership
	

✅ Complete

Identify broken secure channel
	

✅ Complete

Verify DNS
	

✅ Complete

Locate domain controller
	

✅ Complete

Repair domain trust
	

✅ Complete

Generate 4625 failed logon
	

✅ Complete

Create SOCAdmin domain account
	

✅ Complete

Generate 4624 successful logon
	

✅ Complete

Locate both events in Wazuh
	

✅ Complete

Analyze local vs remote authentication
	

✅ Complete

Classify activity
	

✅ Complete

Complete Crawl-Walk-Run investigation
	

✅ Complete


⸻


Stopping Point

Day 7 is complete.

The environment now has:

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
