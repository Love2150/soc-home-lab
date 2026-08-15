Day 5 – Windows Event Forwarding Troubleshooting

Objective

The objective of Day 5 was to begin building a centralized Windows logging architecture using Windows Event Forwarding (WEF).

The goal was to forward selected Sysmon events from WIN11-CLIENT01 to a Windows Server collector and review them in the Forwarded Events log.


Lab Environment

● Ubuntu 24.04 host

● KVM/QEMU virtualization

● WIN11-CLIENT01

● WINSRV-COLLECTOR01

● Windows Server 2022 Standard Evaluation

● Sysmon

● Windows Event Collector

● WinRM

● Windows Event Viewer


Collector Build

A new Windows Server 2022 virtual machine was created to act as the centralized event collector.

VM Configuration

● VM Name: WINSRV-COLLECTOR01

● Operating System: Windows Server 2022 Standard Evaluation (Desktop Experience)

● Memory: 4096 MiB

● CPUs: 2

● Disk: 40 GiB

● Network: libvirt default NAT network

The server received an address on the same subnet as the Windows 11 client.

Example:

```text
WINSRV-COLLECTOR01
192.168.122.129
```

The Windows 11 endpoint was:

```text
WIN11-CLIENT01
192.168.122.190
```


Windows Event Collector Configuration

The Windows Event Collector service was initialized with:

```powershell
wecutil qc
```

The service was verified with:

```powershell
Get-Service Wecsvc
```

Result:

```text
Status: Running
Name: Wecsvc
DisplayName: Windows Event Collector
```


Network Connectivity Testing

Initial ping testing from WIN11-CLIENT01 to the collector failed.

The collector firewall was configured to allow ICMP echo requests:

```powershell
New-NetFirewallRule -DisplayName "SOC Lab - Allow ICMPv4 Echo" -Protocol ICMPv4 -IcmpType 8 -Direction Inbound -Action Allow
```

After the firewall rule was created, ping testing succeeded.

Finding

The failed ping was caused by host firewall behavior rather than a broken network path.

This demonstrated the importance of distinguishing between:

● Network connectivity problems

● Host firewall restrictions

● Service-level failures


WinRM Configuration

WinRM was enabled on WIN11-CLIENT01.

Commands used included:

```powershell
winrm quickconfig
```

```powershell
Get-Service WinRM
```

The client network profile was initially identified as:

```text
NetworkCategory: Public
```

It was changed to:

```text
NetworkCategory: Private
```

using:

```powershell
Set-NetConnectionProfile -InterfaceAlias "Ethernet" -NetworkCategory Private
```

PowerShell remoting was then enabled:

```powershell
Enable-PSRemoting -Force
```

WinRM connectivity was successfully verified using:

```powershell
Test-WSMan WIN11-CLIENT01
```

and later:

```powershell
Test-WSMan 192.168.122.190
```


WEF Subscription Creation

The Event Viewer GUI was initially used to create a collector-initiated subscription named:

```text
SOC-Lab-Sysmon
```

The intended Sysmon Event IDs were:

```text
1,3,13,22
```

These represent:

● Event ID 1 – Process Creation

● Event ID 3 – Network Connection

● Event ID 13 – Registry Value Set

● Event ID 22 – DNS Query

The GUI computer picker failed because it attempted to locate a domain computer object.

The subscription was therefore created manually using XML and wecutil.

The subscription was verified with:

```powershell
wecutil es
```

Result:

```text
SOC-Lab-Sysmon
```


Event Source Configuration

The source was initially added by hostname:

```text
WIN11-CLIENT01
```

Runtime status showed:

```text
RunTimeStatus: Trying
```

with a hostname resolution related error.

The hostname source was removed and replaced with the IP address:

```text
192.168.122.190
```


TrustedHosts and Workgroup WinRM Configuration

Because the systems were operating in a workgroup rather than a domain, the collector was configured with TrustedHosts:

```powershell
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "WIN11-CLIENT01,192.168.122.190" -Force
```

Verification:

```powershell
Get-Item WSMan:\localhost\Client\TrustedHosts
```

Result:

```text
WIN11-CLIENT01,192.168.122.190
```

Unencrypted HTTP was also enabled for this isolated lab:

```powershell
Set-Item WSMan:\localhost\Client\AllowUnencrypted -Value $true
```

Verification showed:

```text
AllowUnencrypted: true
```


WinRM Port Testing

TCP connectivity to WinRM was verified with:

```powershell
Test-NetConnection 192.168.122.190 -Port 5985
```

Result:

```text
TcpTestSucceeded: True
```

This confirmed that:

● The endpoint was reachable

● TCP port 5985 was open

● WinRM traffic was not being blocked at the network layer


WinRM Service Troubleshooting

During testing, WIN11-CLIENT01 showed:

```text
WinRM: Stopped
```

The service was restarted and configured to start automatically.

Commands:

```powershell
Set-Service WinRM -StartupType Automatic
```

```powershell
Start-Service WinRM
```

```powershell
Get-Service WinRM
```

After elevation issues were corrected, WinRM returned to a running state.


Credentialed WinRM Testing

A credential object was created securely:

```powershell
$cred = Get-Credential
```

The account used was:

```text
WIN11-CLIENT01\SOCAdmin
```

WinRM authentication was tested using:

```powershell
Test-WSMan 192.168.122.190 -Authentication Negotiate -Credential $cred
```

The test succeeded.

This confirmed:

● The account credentials were valid

● NTLM/Negotiate authentication worked

● The collector could authenticate to the Windows 11 endpoint


Remote Sysmon Log Access Test

The collector was then used to remotely query the Sysmon Operational log.

Command:

```powershell
Invoke-Command -ComputerName 192.168.122.190 -Credential $cred -Authentication Negotiate -ScriptBlock { Get-WinEvent -LogName "Microsoft-Windows-Sysmon/Operational" -MaxEvents 1 }
```

The command successfully returned a Sysmon event.

The returned event included:

```text
Event ID: 13
Provider: Microsoft-Windows-Sysmon
LogName: Microsoft-Windows-Sysmon/Operational
Computer: WIN11-CLIENT01
```

Finding

This proved that the collector could:

1. Reach the Windows 11 endpoint

2. Authenticate successfully

3. Remotely access the exact Sysmon log required for WEF


Event Forwarding Plugin Verification

The Windows Event Forwarding WinRM plugin was checked on WIN11-CLIENT01.

Command:

```powershell
Get-Item "WSMan:\localhost\Plugin\Event Forwarding Plugin\Enabled"
```

Result:

```text
Enabled: true
```

The plugin resource was also verified:

```powershell
Get-ChildItem "WSMan:\localhost\Plugin\Event Forwarding Plugin\Resources"
```

A registered resource was present.

This confirmed that the WEF-specific WinRM plugin was installed and enabled.


Subscription Configuration Review

The subscription configuration was displayed with:

```powershell
wecutil gs "SOC-Lab-Sysmon" /f:xml
```

Important configuration values included:

```text
SubscriptionType: CollectorInitiated
Enabled: true
ConfigurationMode: Normal
TransportName: HTTP
ContentFormat: RenderedText
LogFile: ForwardedEvents
CredentialsType: Negotiate
CommonUserName: WIN11-CLIENT01\SOCAdmin
EventSource: 192.168.122.190
```

The Sysmon query was:

```xml
*[System[(EventID=1 or EventID=3 or EventID=13 or EventID=22)]]
```


Runtime Status

The subscription itself reported:

```text
RunTimeStatus: Active
LastError: 0
```

However, the source continued to report:

```text
192.168.122.190
RunTimeStatus: Trying
```

Forwarded Events remained empty.


Current Finding

The underlying Windows networking and remote-management components were successfully validated.

The following were confirmed working:

● IP connectivity

● ICMP connectivity

● TCP 5985

● WinRM service

● TrustedHosts

● Negotiate authentication

● Local administrator credentials

● Remote Sysmon log access

● Event Forwarding Plugin

● WEC service

● WEF subscription creation

Despite this, the collector-initiated WEF event source remained in a Trying state.

The most likely remaining issue is the authentication model of the workgroup environment.

Collector-initiated WEF is designed primarily around domain identities or machine accounts. The current setup uses two non-domain systems and a local account.


Planned Next Step

Tomorrow, the lab will introduce Active Directory Domain Services.

Planned sequence:

1. Install AD DS on WINSRV-COLLECTOR01

2. Promote the server to a domain controller

3. Create a lab domain

4. Join WIN11-CLIENT01 to the domain

5. Verify domain authentication

6. Reconfigure or recreate the WEF subscription

...

[Message clipped]  View entire message

