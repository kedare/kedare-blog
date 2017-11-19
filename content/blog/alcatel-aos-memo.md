+++
title = "Tips: Alcatel AOS memo"
date = "2014-02-12"
tags = ["alcatel", "telco"]
description = "My small Alcatel AOS memo"
thumbnail = "images/blog/logo-alcatel-lucent.png"
+++

Here is a small introduction to Alcatel AOS with some examples.

<!--more-->

## Factory Reset

This does not remove users, passwords and stack configuration, to remove users and passwords, you must delete the UserTable2 file

{{< highlight bash >}}
delete working/boot.cfg
delete certified/boot.cfg
reload (or unplug)
{{< / highlight >}}

### Default Login

 * Login : admin
 * Password : switch

## Spanning Tree

Some sample commands

{{< highlight bash >}}
-> show spantree ports active
Vlan  Port  Oper Status  Path Cost  Role   Loop Guard   Note
-----+------+------------+---------+-------+-----------+---------
1  1/1        BLK             4    ALT         DIS
1  1/2       FORW             4   ROOT         DIS
1  1/3       FORW             4   DESG         DIS
1  1/48      FORW            19   DESG         DIS

-> show spantree 1
Spanning Tree Parameters for Vlan 1
Spanning Tree Status :                   ON,
Protocol             :       IEEE Rapid STP,
mode                 : 1X1 (1 STP per Vlan),
Priority             :       32768 (0x8000),
Bridge ID            :   8000-00:e0:b1:81:fe:b6,
Designated Root      :   0010-00:e0:b1:aa:fe:d8,
Cost to Root Bridge  :                    4,
Root Port            :   Slot 1 Interface 2,
Next Best Root Cost  :                    4,
Next Best Root Port  :   Slot 1 Interface 1,
TxHoldCount          :                    3,
Topology Changes     :                    7,
Topology age         :            00:05:13,
Current Parameters (seconds)
Max Age              =    20,
Forward Delay        =    15,
Hello Time           =     2
Parameters system uses when attempting to become root
System Max Age       =    20,
System Forward Delay =    15,
System Hello Time    =     2

-> bridge 1 protocol rstp
-> bridge 1 priority 16
{{< / highlight >}}

(Yes.. sometime it’s bridge, sometime its spantree and debug commands are “stp”… Nothing coherent !)

## Root Guard

Root guard on port 8/1 vlan 100

{{< highlight bash >}}
bridge 1x1 100 8/1 restricted-role enable
{{< / highlight >}}

## Link Aggregation

Creating a LAG does not create a logical interface (like on Cisco/Juniper/HP), the first physical interface of the LAG become the “Primary Port”, if 1/1 and 1/2 are on the same lag, even if you unplug 1/1, you could see it as root port on STP because 1/2 is still part of the LAG and is up (and is the primary port)

{{< highlight bash >}}
-> show linkagg 1

Static Aggregate
SNMP Id                  : 40000001,
Aggregate Number         : 1,
SNMP Descriptor          : Omnichannel Aggregate Number 1 ref 40000001 size 2,
Name                     : TOP-MIDDLE,
Admin State              : ENABLED,
Operational State        : UP,
Aggregate Size           : 2,
Aggregate Min-Size       : 1,
Number of Selected Ports : 2,
Number of Reserved Ports : 2,
Number of Attached Ports : 2,
Primary Port             : 1/1

-> show linkagg 1 port

Slot/Port Aggregate SNMP Id   Status   Agg  Oper Link Prim Standby
---------+---------+-------+----------+----+----+----+----+-------
1/1    Static      1001  ATTACHED     1  UP   UP   YES  NO
1/2    Static      1002  ATTACHED     1  UP   UP   NO   NO

-> static linkagg 1 size 2 admin state enable
-> static linkagg 1 name "TOP-MIDDLE"
-> static linkagg 2 size 2 admin state enable
-> static linkagg 2 name "TOP-BOTTOM"
-> static agg 1/1 agg num 1
-> static agg 1/2 agg num 1
-> static agg 1/3 agg num 2
-> static agg 1/4 agg num 2
{{< / highlight >}}
