SOC Home Lab Progress Write-Up

Wazuh + Sysmon Integration and Threat Hunting Validation

Date: August 16, 2026
Environment: SPC Home Lab
Primary Endpoint: WIN11-CLIENT01
Wazuh Manager: Ubuntu host grim50reaper-HP-Laptop-15-dy1xxx
Windows Domain: soclab.local


1. Session Objective

The goal of this session was to move past the Windows Event Forwarding (WEF) troubleshooting from the previous lab work and establish a reliable endpoint telemetry pipeline using:

Sysmon → Wazuh Agent → Wazuh Manager → Wazuh Dashboard

The priority was to get back to practical SOC investigation work instead of continuing to spend time troubleshooting WEF.


2. Previous Stopping Point

The previous lab session focused heavily on Windows Event Forwarding. The WEF subscription could be created and showed as active, but the Windows client remained in a Trying state and continued returning WinRM-related errors.

Several areas had already been tested during troubleshooting, including:

● Domain membership and Group Policy

● DNS and time synchronization

● WinRM connectivity

● Kerberos/SPN-related configuration

● Source-initiated and collector-initiated subscriptions

Because WEF was consuming too much lab time without producing reliable results, the decision was made to stop troubleshooting WEF and use the Wazuh agent to collect Sysmon telemetry directly from the Windows endpoint.


3. Wazuh Manager Rebuild

The previous Wazuh installation on Ubuntu had service startup problems, so the manager was rebuilt from scratch using the Wazuh all-in-one installation.

After installation, the following services were verified as active:

```bash
sudo systemctl is-active wazuh-manager
sudo systemctl is-active wazuh-indexer
sudo systemctl is-active wazuh-dashboard
```

All three services returned:

```text
active
```

Wazuh Manager Network Address

The Ubuntu host had multiple interfaces. The libvirt address used for Windows VM communication was:

```text
192.168.122.1
```

The dashboard was accessed from the Ubuntu host using:

```text
https://192.168.1.136
```


4. Windows Wazuh Agent Installation

The Windows 11 VM did not have Internet access, so the Wazuh agent installer was downloaded on Ubuntu and transferred locally to the Windows VM.

The installer was served from Ubuntu using:

```bash
python3 -m http.server 8000 --bind 192.168.122.1
```

The Windows client successfully downloaded the Wazuh MSI.

The Wazuh service was installed and verified with:

```powershell
Get-Service WazuhSvc
```

The service showed:

```text
Running
```


5. Wazuh Manager Address Correction

The agent was initially installed with an incorrect manager address:

```xml
<address>192.168.1</address>
```

The configuration was corrected to:

```xml
<address>192.168.122.1</address>
```

The service was then restarted.

The agent log confirmed successful communication with the manager:

```text
wazuh-agent: INFO: Agent is now online. Process unlocked, continuing...
```


6. Agent Registration Validation

On the Ubuntu Wazuh manager, the following command was used:

```bash
sudo /var/ossec/bin/agent_control -l
```

The result showed:

```text
ID: 000, Name: grim50reaper-HP-Laptop-15-dy1xxx (server), IP: 127.0.0.1, Active/Local
ID: 001, Name: WIN11-CLIENT01, IP: any, Active
```

Result

WIN11-CLIENT01 was successfully registered and communicating with the Wazuh manager.

Status: ACTIVE


7. Sysmon Integration

The Windows Wazuh agent configuration was updated to collect the Sysmon Operational event channel directly.

The following block was added to:

```text
C:\Program Files (x86)\ossec-agent\ossec.conf
```

```xml
<localfile>
  <location>Microsoft-Windows-Sysmon/Operational</location>
  <log_format>eventchannel</log_format>
</localfile>
```

The Wazuh agent was restarted:

```powershell
Restart-Service WazuhSvc
```


8. Sysmon Local Validation

Sysmon events were verified directly on WIN11-CLIENT01 using:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-Sysmon/Operational" -MaxEvents 5 |
Select-Object TimeCreated,Id,ProviderName
```

The output showed multiple:

```text
Event ID: 1
Provider: Microsoft-Windows-Sysmon
```

Result

Sysmon was operating correctly and recording process creation events locally.


9. End-to-End Telemetry Validation

To prove that all Sysmon events were reaching the Wazuh manager, temporary JSON archive logging was enabled on the manager:

```xml
<logall_json>yes</logall_json>
```

After restarting the Wazuh manager, the archive was monitored with:

```bash
sudo tail -f /var/ossec/logs/archives/archives.json | grep -i sysmon
```

The manager displayed Sysmon JSON events containing:

```text
Microsoft-Windows-Sysmon
Microsoft-Windows-Sysmon/Operational
EventID: 1
```

Confirmed Pipeline

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

Status: OPERATIONAL

Archive logging was only used for validation and can remain disabled during normal lab operation to avoid unnecessary disk usage.


10. Wazuh Dashboard Access

The Wazuh dashboard was successfully accessed at:

```text
https://192.168.1.136
```

The Threat Hunting interface showed alerts from WIN11-CLIENT01.

The endpoint filter used was:

```text
agent.name:"WIN11-CLIENT01"
```

Once a high-severity-only filter was removed, the dashboard displayed dozens of alerts from the Windows endpoint.


11. DQL Threat Hunting

DQL was successfully used to search Wazuh alerts.

Example query:

```text
agent.name:"WIN11-CLIENT01" AND data.win.system.eventID:1
```

The Wazuh Events view returned Sysmon telemetry and allowed individual records to be expanded for investigation.


12. First Sysmon Investigation

A Sysmon Event ID 1 process creation alert was opened in Wazuh.

Endpoint

```text
WIN11-CLIENT01.soclab.local
```

Event

```text
Sysmon Event ID: 1
Provider: Microsoft-Windows-Sysmon
```

Process

```text
C:\Windows\SysWOW64\net1.exe
```

Command Line

```text
C:\WINDOWS\system32\net1 user
```

Parent Process

```text
C:\Windows\SysWOW64\net.exe
```

Parent Command Line

```text
net user
```

User

```text
NT AUTHORITY\SYSTEM
```

Wazuh Detection

```text
Rule ID: 92031
Rule Level: 3
Rule Description: Discovery activity executed
Rule Groups: sysmon, sysmon_eid1_detections, windows
```


13. Initial Analyst Assessment

The command:

```text
net user
```

is commonly used to enumerate Windows user accounts.

This behavior can be legitimate administrative activity, but it is also commonly observed during attacker discovery and reconnaissance.

The event alone was not enough to classify the activity as malicious.

The investigation therefore moved to surrounding activity to establish context.


14. Surrounding Activity Observed

Additional activity near the net user event included:

```text
net.exe / net1.exe
powershell.exe
secedit.exe
```

A Sysmon Event ID 11 file creation event was also observed involving a path under:

```text
C:\Windows\SystemTemp\
```

The activity was running under:

```text
NT AUTHORITY\SYSTEM
```

This provides a useful investigation chain for future timeline analysis.

At this stage, the activity should be treated as requiring context, not automatically malicious.


15. Key SOC Skills Practiced

This session provided hands-on experience with:

● Deploying and validating a Wazuh endpoint agent

● Troubleshooting SIEM agent connectivity

● Configuring Windows Event Channel collection

● Sending Sysmon telemetry to a SIEM

● Validating telemetry at both the source and manager

● Accessing and navigating the Wazuh dashboard

● Filtering endpoint telemetry

● Writing DQL queries

● Investigating Sysmon Event ID 1

● Reviewing command-line execution

● Identifying parent/child process relationships

● Reviewing process execution under NT AUTHORITY\SYSTEM

● Building an investigation timeline from surrounding events

● Distinguishing a detection from a confirmed security incident


16. Important Lesson

A SIEM alert does not automatically mean a system is compromised.

The Wazuh rule identified:

```text
Discovery activity executed
```

because net user is behavior associated with account discovery.

A SOC analyst still needs to answer:

● What process launched the command?

● What account executed it?

● What occurred before it?

● What occurred after it?

● Is the behavior expected on this system?

● Are there additional suspicious commands in the same process chain?

This is the difference between alert review and investigation.


17. Known Issue

The Windows client continues to display domain trust-related warnings involving:

```text
The trust relationship between this workstation and the primary domain failed.
```

This issue is currently not blocking Wazuh or Sysmon telemetry.

Because the core SOC telemetry pipeline is functioning, the domain trust issue will not be worked unless it blocks a future lab objective.


18. Windows Server Plan

The Windows Server created earlier will still be used in the lab.

It will no longer be used primarily as the WEF collector.

Planned roles include:

● Active Directory / domain services

● Windows Security event generation

● Authentication monitoring

● Account and group activity

● A second Windows system monitored by Wazuh

● Future workstation-to-server attack and investigation scenarios

The next infrastructure step involving the server should be installing the Wazuh agent and collecting its Windows Security events.


Current Lab Status

|Component                      |Status                       |
|-------------------------------|-----------------------------|
|Ubuntu Wazuh Manager           |✅ Operational                |
|Wazuh Indexer                  |✅ Operational                |
|Wazuh Dashboard                |✅ Operational                |
|WIN11-CLIENT01 Wazuh Agent     |✅ Active                     |
|Sysmon                         |✅ Operational                |
|Sysmon → Wazuh ingestion       |✅ Confirmed                  |
|Wazuh Threat Hunting           |✅ Working                    |
|DQL queries                    |✅ Working                    |
|Sysmon Event ID 1 investigation|✅ Working                    |
|Windows Server                 |⏳ Future integration         |
|WEF                            |⚠️ Discontinued for now       |
|Domain trust warning           |⚠️ Unresolved but non-blocking|


Stopping Point

This is a strong stopping point for the session.

The core lab infrastructure is now operational, and the environment has transitioned from setup/troubleshooting into actual SOC investigation work.

The most important accomplishment is that we can now:

```text
Generate Windows activity
        ↓
Capture it with Sysmon
        ↓
Send it through the Wazuh agent
        ↓
Detect/index it in Wazuh
        ↓
Search it with DQL
        ↓
Investigate process and command-line activity
```
Next Session

The next session should begin with the working environment exactly as it is now.

Recommended next investigation sequence:

1. Build a short timeline around the net user discovery alert.

2. Examine the PowerShell and secedit.exe activity near the same timestamp.

3. Practice distinguishing benign administrative behavior from suspicious discovery.

4. Generate controlled Sysmon Event IDs 1, 3, 11, 13, and 22.

5. Investigate those events using Wazuh Threat Hunting.

6. Document evidence and analyst conclusions.

7. After completing the endpoint investigation block, add the Windows Server as a second Wazuh-monitored Windows host.


Session Completion

Lab telemetry pipeline: COMPLETE
Wazuh/Sysmon integration: COMPLETE
Threat Hunting validation: COMPLETE
Ready for practical SOC investigations: YES

