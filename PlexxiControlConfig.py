# # Copyright 2013 Plexxi, Inc.  All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from plexxi.core.api.binding import *
from plexxi.core.api.session import *
from plexxi.core.api.util import *
from PlexxiControlCommonLib import *
import cmd ,re


def defVLANName(vlan, name):
    """ Gives the VLAN a user defined name
    vlan (integer) - needs to be existing VLAN
    name (string) - name of VLAN """

    print 'Set VLAN %s, %s'%(vlan, name)
    tags = VlanInterface.getAll()
    vlanFound = False
    for tag in tags:
        if tag.getVlan() == int(vlan):
            vlanFound = True
            print("Set Name VLAN", vlan, name)
            joby = Job.create(name="Set Name VLAN %s, %s"%(vlan, name))
            joby.addUserSequentialGroupItem("vlan")
            joby.begin()
            tag.setName(name)
            joby.commit()
            return 0
    if vlanFound == False:
        print("Vlan not found", vlan)
        return 1

def getPortVLAN(switchId, portId):
    """ returns a JSON with all VLANs on specified switch/port
    switchId - name, mac or uuid of switch
    portId (integer) - hardware port number
    JSON format {tag(integer):{Name:'string'}}"""

    switch = findSwitchFromNameMacorUuid(switchId)
    if not switch:
        return
    port = checkPortRange(portId)
    if not port:
        return

    fabric = switch.getAllSwitchFabrics()
    fabric1 = fabric[0]
    ports = fabric1.getAllSwitchFabricInPorts()
    for port in ports:
        if int(port.getHwId()) == portId:
            port1 = port
            break
    if not port1:
        print 'Port not found'
        return 1
    lag = port1.getLagInPort()
    vlans = lag.getAllVlanInterfaces()
    vlanJson = {}
    for vlan in vlans:
        vlanJson[vlan.getVlan()] = {}
        vlanJson[vlan.getVlan()]['Name'] = vlan.getName()
    return vlanJson

def defPortName(switchId, portId, name):
    """ Gives the Switch port a user defined name
    switchId (name, MAC or UUID)
    port (integer) - hardware port ID
    name (string) - name of port """

    print 'Set port %s, %s'%(portId, name)

    switch = findSwitchFromNameMacorUuid(switchId)
    if not switch:
        return
    port = checkPortRange(portId)
    if not port:
        return

    fabric = switch.getAllSwitchFabrics()
    fabric1 = fabric[0]
    port1 = None
    ports = fabric1.getAllSwitchFabricInPorts()
    for port in ports:
        if int(port.getHwId()) == portId:
            port1 = port
            break
    if not port1:
        print 'Port not found'
        return 1

    print("Set Name Port", port1, name)
    joby = Job.create(name="Set Name Port %s, %s"%(port , name))
    joby.addUserSequentialGroupItem("port")
    joby.begin()
    port1.setName(name)
    joby.commit()
    return 0


def getPortName(switchId, portId):
    """ Get the Switch port name
    switchId (name, MAC or UUID)
    port (integer) - hardware port ID """

    switch = findSwitchFromNameMacorUuid(switchId)
    if not switch:
        return
    port = checkPortRange(portId)
    if not port:
        return

    fabric = switch.getAllSwitchFabrics()
    fabric1 = fabric[0]
    port1 = None
    ports = fabric1.getAllSwitchFabricInPorts()
    for port in ports:
        if int(port.getHwId()) == portId:
            port1 = port
            break
    if not port1:
        print 'Port not found'
        return 1
    return port1.getName()
