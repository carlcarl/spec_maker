# CM LOG SPEC
##### Feature Description:
This feature reports important cm event or information via syslog.
To easily indicate which category the logs belong to, all log will add a fixed prefix "[CM]".
##### Log Format:
- [CM]SIM - detect ... inserted/removed
- [CM]SIM - pin verify ... ok/fail
- [CM]SIM - pin modify ... ok/fail
- [CM]SIM - pin enable ... ok/fail
- [CM]SIM - pin disable ... ok/fail
- [CM]SIM - puk verify ... ok/fail
- [CM]SIM - locked/unlocked, blocked/unblocked, failure/valid
- [CM]STATUS - search/connecting/limited/error
- [CM]SEARCH - %RAT,%plmnlists
- [CM]CONNECT - ok,%RAT,%band,%plmn,%cellid,%rsrp,%rssi,%sinr,%apnmode,%pdptype,%ip_allocation
- [CM]CONNECT - fail,%RAT,%band,%plmn,%cellid,%rsrp,%rssi,%sinr,%apnmode,%pdptype,%reject_reason
- [CM]DISCONNECTED - %RAT,%band,%plmn,%cellid,%rsrp,%rssi,%sinr,%txpower,%DLMCS,%ULMCS,%BLER,%reason
- [CM]HANDOVER - from "%servingRAT,%servingPLMN,%cellid,%rsrp,%rssi,%sinr" to "%servingRAT,%servingPLMN,%cellid,%rsrp,%rssi,%sinr"
>Note: The words after "%" means variable's definition

##### Example Logs:
[CM]SIM - detect ... inserted
[CM]SIM - unlocked,unblocked,valid
[CM]STATUS - search
[CM]SEARCH - lte,46692;46601
[CM]STATUS - connecting
[CM]CONNECT - ok,lte,3,46692,10,-90dBm,-70dBm,15dB,auto,IPv6,192.168.50.11

##### Supported Platform:
- Qualcomm
- Altair
- Hisilicon