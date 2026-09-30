# Day 5 — Windows Event Forwarding Troubleshooting

| Field | Value |
|---|---|
| Date | Not recorded |
| Status | Blocked |
| Phase | Centralized Windows logging and WEF troubleshooting |

## Summary

Day 5 began the build of a centralized Windows logging architecture using Windows Event Forwarding (WEF). A Windows Server 2022 collector was deployed, the Windows Event Collector (WEC) and WinRM paths were configured, and a collector-initiated subscription was created for selected Sysmon events from `WIN11-CLIENT01`.

Testing validated network reachability, TCP 5985, WinRM authentication, remote access to the Sysmon Operational log, the Event Forwarding WinRM plugin, and the WEC subscription configuration. The subscription reported `Active` with `LastError: 0`, but its event source remained `Trying` and the Forwarded Events log remained empty. WEF was therefore not operational at the end of the session. The leading hypothesis was a workgroup authentication limitation, and the planned next step was to introduce Active Directory Domain Services (AD DS).

## Objectives

- [x] Deploy a Windows Server collector on the same lab subnet as the Windows 11 endpoint.
- [x] Initialize and validate the Windows Event Collector service.
- [x] Configure and test WinRM between the collector and endpoint.
- [x] Create a collector-initiated subscription for Sysmon Event IDs `1`, `3`, `13`, and `22`.
- [x] Validate authenticated remote access to the Sysmon Operational log.
- [ ] Forward Sysmon events into the collector's Forwarded Events log.

## Environment

| Component | Details |
|---|---|
| Host | Ubuntu 24.04 |
| Virtualization | KVM/QEMU; libvirt default NAT network |
| Collector | `WINSRV-COLLECTOR01`, Windows Server 2022 Standard Evaluation (Desktop Experience), `192.168.122.129` |
| Collector VM | 4096 MiB memory, 2 CPUs, 40 GiB disk |
| Endpoint | `WIN11-CLIENT01`, Windows 11, `192.168.122.190` |
| Security tooling | Sysmon; Microsoft-Windows-Sysmon/Operational log |
| Collection tooling | Windows Event Collector, Windows Event Forwarding, WinRM, Event Viewer |
| Authentication context | Workgroup systems using local account `WIN11-CLIENT01\SOCAdmin` with Negotiate/NTLM |

## Work Completed

- Built `WINSRV-COLLECTOR01` as the centralized event collector.
- Initialized the Windows Event Collector service and confirmed that `Wecsvc` was running.
- Identified and corrected an ICMP firewall restriction on the collector.
- Changed the endpoint network profile from Public to Private and enabled PowerShell remoting.
- Validated WinRM by hostname and IP address.
- Created the collector-initiated `SOC-Lab-Sysmon` subscription manually after the Event Viewer computer picker failed in the non-domain environment.
- Replaced the unresolved hostname source with the endpoint IP address.
- Configured `TrustedHosts` and allowed unencrypted HTTP for the isolated lab.
- Restored the endpoint WinRM service to a running, automatic-start state.
- Validated credentialed Negotiate authentication and remote Sysmon log access.
- Verified that the Event Forwarding WinRM plugin was installed and enabled.
- Reviewed subscription configuration and runtime state.
- Documented the unresolved difference between the subscription's `Active` state and the source's `Trying` state.

## Implementation and Validation

### Collector build and WEC initialization

The Windows Server 2022 VM was placed on the same `192.168.122.0/24` lab subnet as the endpoint. WEC was initialized with `wecutil qc` and checked with `Get-Service Wecsvc`.

```text
Status: Running
Name: Wecsvc
DisplayName: Windows Event Collector
```

This established that the collector service itself was available.

### Network and firewall validation

Initial ping tests from `WIN11-CLIENT01` to the collector failed. An inbound ICMPv4 echo rule was added on the collector, after which ping succeeded. This isolated the initial failure to host firewall behavior rather than a broken virtual network path.

TCP connectivity from the collector to endpoint WinRM was then tested directly:

```text
TcpTestSucceeded: True
```

The successful TCP 5985 test demonstrated that the endpoint was reachable and that WinRM traffic was not blocked at the network or host-firewall layer.

### Endpoint WinRM configuration

The endpoint's network category was initially `Public`. It was changed to `Private`, after which PowerShell remoting was enabled. `Test-WSMan` succeeded first with `WIN11-CLIENT01` and later with `192.168.122.190`.

During later troubleshooting, the endpoint's WinRM service was found stopped. It was configured for automatic startup and restarted after elevation issues were corrected. A subsequent service check showed WinRM running.

### WEF subscription creation

The Event Viewer GUI was initially used to create a collector-initiated subscription named `SOC-Lab-Sysmon`. The intended Sysmon event set was:

| Event ID | Sysmon event |
|---|---|
| 1 | Process Creation |
| 3 | Network Connection |
| 13 | Registry Value Set |
| 22 | DNS Query |

The GUI computer picker attempted to locate a domain computer object and failed because the systems were not domain joined. The subscription was therefore created manually with XML and `wecutil`. Enumeration with `wecutil es` returned `SOC-Lab-Sysmon`, confirming that the subscription object existed.

### Source addressing and workgroup configuration

The source was initially configured as `WIN11-CLIENT01`. Runtime status remained `Trying` and reported a hostname-resolution-related error. The hostname source was removed and replaced with `192.168.122.190`.

Because both systems were in a workgroup, the collector's `TrustedHosts` value was set to:

```text
WIN11-CLIENT01,192.168.122.190
```

Unencrypted HTTP was also enabled for this isolated lab, and validation returned:

```text
AllowUnencrypted: true
```

These changes removed hostname trust and transport-policy variables from the immediate troubleshooting path, but they did not cause WEF event delivery to begin.

### Credentialed authentication and remote Sysmon validation

A credential object was created for `WIN11-CLIENT01\SOCAdmin`. Credentialed `Test-WSMan` with Negotiate authentication succeeded against `192.168.122.190`. This validated the local account credentials and showed that Negotiate/NTLM authentication worked for an explicit WinRM request.

The collector then remotely queried the endpoint's Sysmon Operational log. The command returned an event with the following fields:

```text
Event ID: 13
Provider: Microsoft-Windows-Sysmon
LogName: Microsoft-Windows-Sysmon/Operational
Computer: WIN11-CLIENT01
```

This proved that the collector could reach the endpoint, authenticate with explicit credentials, and read the exact log required by the subscription. It did not prove that the WEF subscription authentication context could perform the same operation.

### Event Forwarding plugin validation

The endpoint's Event Forwarding WinRM plugin returned `Enabled: true`, and its Resources path contained a registered resource. This confirmed that the WEF-specific WinRM plugin was installed and enabled.

### Subscription configuration and runtime validation

`wecutil gs "SOC-Lab-Sysmon" /f:xml` showed the important subscription values:

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

The Sysmon event query was:

```xml
*[System[(EventID=1 or EventID=3 or EventID=13 or EventID=22)]]
```

The subscription-level runtime state was:

```text
RunTimeStatus: Active
LastError: 0
```

The source-level runtime state was still:

```text
192.168.122.190
RunTimeStatus: Trying
```

The Forwarded Events log remained empty. The `Active` subscription state therefore indicated that the subscription was enabled and running, not that the source connection or event-delivery path was operational.

## Commands and Queries

The principal commands, in troubleshooting order, were:

```powershell
# Collector: initialize and verify WEC
wecutil qc
Get-Service Wecsvc

# Collector: permit ICMP echo for connectivity testing
New-NetFirewallRule -DisplayName "SOC Lab - Allow ICMPv4 Echo" -Protocol ICMPv4 -IcmpType 8 -Direction Inbound -Action Allow

# Endpoint: configure and verify WinRM/remoting
winrm quickconfig
Get-Service WinRM
Set-NetConnectionProfile -InterfaceAlias "Ethernet" -NetworkCategory Private
Enable-PSRemoting -Force

# WinRM validation
Test-WSMan WIN11-CLIENT01
Test-WSMan 192.168.122.190

# Collector: enumerate the manually created subscription
wecutil es

# Collector: configure workgroup trust and isolated-lab HTTP transport
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "WIN11-CLIENT01,192.168.122.190" -Force
Get-Item WSMan:\localhost\Client\TrustedHosts
Set-Item WSMan:\localhost\Client\AllowUnencrypted -Value $true

# Collector: test the endpoint WinRM port
Test-NetConnection 192.168.122.190 -Port 5985

# Endpoint: restore WinRM service state
Set-Service WinRM -StartupType Automatic
Start-Service WinRM
Get-Service WinRM

# Collector: test explicit workgroup credentials
$cred = Get-Credential
Test-WSMan 192.168.122.190 -Authentication Negotiate -Credential $cred

# Collector: test remote access to the source Sysmon log
Invoke-Command -ComputerName 192.168.122.190 -Credential $cred -Authentication Negotiate -ScriptBlock { Get-WinEvent -LogName "Microsoft-Windows-Sysmon/Operational" -MaxEvents 1 }

# Endpoint: verify the WEF WinRM plugin
Get-Item "WSMan:\localhost\Plugin\Event Forwarding Plugin\Enabled"
Get-ChildItem "WSMan:\localhost\Plugin\Event Forwarding Plugin\Resources"

# Collector: inspect subscription configuration
wecutil gs "SOC-Lab-Sysmon" /f:xml
```

## Evidence

### Linked screenshots

- [Windows client VM state](../screenshots/day05/windows-client-vm-state.png) — records the original `WIN11-CLIENT01` virtual-machine state before the collector build.
- [Windows Server VM creation](../screenshots/day05/windows-server-vm-creation.png) — records the Virtual Machine Manager workflow used to begin creating the collector VM.
- [Collector host and WEC service status](../screenshots/day05/collector-host-and-wecsvc-status.png) — confirms the collector hostname, `192.168.122.129` address, and initial stopped state of `Wecsvc`.
- [Collector ICMP firewall rule](../screenshots/day05/collector-icmp-firewall-rule.png) — shows successful creation of the inbound ICMPv4 echo rule.
- [Ping before and after the firewall change](../screenshots/day05/collector-ping-before-and-after-firewall.png) — records the transition from 100% packet loss to successful replies.
- [WEF hostname source in `Trying`](../screenshots/day05/wef-hostname-source-trying.png) — shows an active subscription whose hostname source remained in `Trying` with a WinRM trust error.
- [WinRM `TrustedHosts` configuration](../screenshots/day05/winrm-trustedhosts-configuration.png) — confirms `WIN11-CLIENT01` was added to the collector's trusted-host list.
- [WinRM IP test and WEF status](../screenshots/day05/winrm-ip-test-and-wef-status.png) — shows successful `Test-WSMan` connectivity by IP while the event source remained in `Trying`.
- [WinRM transport and authentication tests](../screenshots/day05/winrm-transport-and-authentication-tests.png) — confirms unencrypted lab transport, TCP 5985 reachability, and credentialed Negotiate authentication.
- [Event Forwarding plugin validation](../screenshots/day05/event-forwarding-plugin-validation.png) — confirms that the endpoint's Event Forwarding WinRM plugin was enabled with a registered resource.

### Additional recorded validation

- WEC service: `Running` on `WINSRV-COLLECTOR01`.
- Endpoint WinRM service: restored to running with automatic startup.
- Remote log access: returned a Sysmon event from `Microsoft-Windows-Sysmon/Operational` on `WIN11-CLIENT01`.
- Subscription runtime: `Active`, `LastError: 0`; source runtime: `Trying`; Forwarded Events remained empty.

## Challenges and Troubleshooting

| Problem | Investigation | Resolution or status |
|---|---|---|
| Ping to collector failed | Compared subnet placement with host firewall behavior | Added an inbound ICMPv4 echo rule; ping then succeeded |
| Endpoint network profile was Public | Checked `NetworkCategory` before enabling remoting | Changed the Ethernet profile to Private |
| Event Viewer computer picker failed | GUI attempted to locate a domain computer object | Bypassed the picker and created the subscription manually with XML and `wecutil` |
| Hostname source remained `Trying` | Runtime output indicated a hostname-resolution-related error | Replaced `WIN11-CLIENT01` with `192.168.122.190`; source still remained `Trying` |
| Workgroup WinRM trust requirements | Checked non-domain authentication and transport settings | Added hostname and IP to `TrustedHosts`; enabled unencrypted HTTP for the isolated lab |
| Endpoint WinRM service stopped | Checked service state during connection testing | Set automatic startup and restarted the service after correcting elevation issues |
| Possible invalid credentials or inaccessible Sysmon log | Used credentialed `Test-WSMan` and `Invoke-Command` with Negotiate | Credentials and direct remote Sysmon access validated successfully |
| Possible missing WEF plugin | Inspected the Event Forwarding Plugin and its resources | Plugin was enabled and a resource was registered |
| Subscription showed `Active` but source showed `Trying` | Reviewed XML configuration, runtime status, network layers, authentication, and remote log access | Unresolved; no events reached Forwarded Events |

## Findings and Analyst Notes

- The initial ping failure was caused by collector firewall behavior, not by a broken virtual network path.
- Successful TCP 5985 and `Test-WSMan` results separated network and WinRM transport health from the unresolved WEF source connection.
- Explicit credentials using Negotiate/NTLM were valid, and the collector could remotely read the target Sysmon log.
- The WEF-specific WinRM plugin, WEC service, subscription object, and event query were present and enabled.
- Subscription-level `Active` with `LastError: 0` did not mean forwarding had succeeded. Source-level `Trying` and an empty Forwarded Events log were the decisive operational indicators.
- The leading hypothesis was that collector-initiated WEF was failing because of the workgroup authentication model. Collector-initiated WEF is primarily designed around domain identities or machine accounts, while this configuration used two non-domain systems and a local account.
- The workgroup-authentication explanation remained a hypothesis, not a confirmed root cause. Introducing domain authentication was selected as the next controlled test.

## Decisions

- Use a manually defined XML subscription because the Event Viewer picker depended on domain computer discovery unavailable in the workgroup.
- Replace the hostname source with the IP address to remove hostname resolution from the active failure path.
- Permit `TrustedHosts` and unencrypted HTTP only within the isolated lab to test workgroup WinRM behavior; these settings were troubleshooting accommodations, not a production security recommendation.
- Treat WEF as blocked despite the subscription's `Active` state because the source remained `Trying` and no events were forwarded.
- Stop further workgroup-specific changes after validating the underlying layers and move the next test to domain-based authentication with AD DS.

## Skills Demonstrated

- Windows Server collector deployment
- Windows Event Collector and WEF subscription administration
- WinRM and PowerShell remoting configuration
- Windows Firewall and network-layer troubleshooting
- Workgroup authentication troubleshooting with TrustedHosts and Negotiate/NTLM
- Remote Windows Event Log validation with `Get-WinEvent`
- Sysmon event-channel and Event ID selection
- Layered fault isolation and precise interpretation of runtime status

## Current Status

| Component | Status |
|---|---|
| Collector VM | Operational |
| IP and ICMP connectivity | Operational |
| TCP 5985 | Operational |
| WEC service | Operational |
| Endpoint WinRM service | Operational |
| TrustedHosts configuration | Complete |
| Negotiate authentication with explicit local credentials | Operational |
| Remote Sysmon log access | Operational |
| Event Forwarding WinRM plugin | Operational |
| `SOC-Lab-Sysmon` subscription object | Active |
| Event source `192.168.122.190` | Trying / unresolved |
| Forwarded Events delivery | Blocked; no events received |
| Overall Day 5 objective | Blocked |

## Next Steps

1. Install Active Directory Domain Services on `WINSRV-COLLECTOR01`.
2. Promote the server to a domain controller.
3. Create a lab domain.
4. Join `WIN11-CLIENT01` to the domain.
5. Verify domain authentication between the collector and endpoint.
6. Reconfigure or recreate the WEF subscription under the domain authentication model.
7. Generate matching Sysmon activity and verify that Event IDs `1`, `3`, `13`, and `22` reach Forwarded Events.

---

[← Previous day](Day04.md) · [Documentation index](README.md) · [Next day →](Day06.md)
