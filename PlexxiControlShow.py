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
#   
#    Version specific 1.3.1


from plexxi.core.api.binding import *
from plexxi.core.api.session import *
from plexxi.core.api.util import *
from PlexxiControlCommonLib import *
import re
from pydoc import help
from plexxi.core.api.util.VlanType import VlanType

#################Operational Show commands to get ring information
def showSwitchIps():
    """ Prints IP addresses of all switches """
    switches = PlexxiSwitch.getAll()
    print 'Name','\t\t\t','IP address\n'
    for s in switches:
        print s.getName(),'\t\t',s.getIpAddress()

def showSwitchPorts(switchId=None):
    """ Prints a switch port summary
    switchId - can be name, or mac of switch """
  
    False = 0
    switch = findSwitchFromNameMacorUuid(switchId)
    if not isinstance(switch,PlexxiSwitch):
        return 
    print ' '
    print 'Switch Name: ', switch.getName()
    print 'stationMac: ', switch.getForeignUuid()
    print 'uuid: ', switch.getUuid()
    print ' '
    fabric = switch.getAllSwitchFabrics()[0]
    inPorts = fabric.getAllSwitchFabricInPorts()
    print 'Switch InPorts:'
    for port in inPorts:
        type = 'None'
        link = 'Unknown'
        if(port.isAccessPort() == True):
            type = 'Access'
        else:
            type = 'Uplink'
        if(port.isLinkDown() == True):
            link = 'Down'
        else:
            link = 'Up'
        if(port.isAdminStateEnabled() == True):
            adminState = 'Enabled'
        else:
            adminState = 'Disabled'
        input=port.getInput()
        comp=input.getComponent()
        if type == 'Access':
            formFactor = comp.getFormFactor()
        else:
            formFactor = 'Lightwave'
        print ' Name:', port.getName(),'- Type:', type, '- Status:', link, '/', adminState, '- Speed:', port.getLineSpeed(), formFactor

def showSwitchSummary(switchId=None):
    """ Prints a switch port summary

    switchId - can be name, or mac of switch """
    switch = findSwitchFromNameMacorUuid(switchId)
    if not isinstance(switch,PlexxiSwitch):
        return
    print '\n\t\tSwitch: ', switch.getName(), ', stationMac: ', switch.getForeignUuid(), ' - ', switch.getOperationalStage(), ' - ', switch.getStatus()


def showRingSummary():
    """ Prints a ring/switch status summary """
    rings = PlexxiRing.getAll()
    print ' '
    print '                  Number of Plexxi Rings = ', len(rings)
    for ring in rings:
        print ' '
        print 'Ring Name: ', ring.name
        if ring.getNumConfluentRings() == None:
            print '***Invalid Ring - NumConflentRings == None***'
        else:
            print '      NumConfluentRings: ' , ring.getNumConfluentRings()
        switches=ring.getAllPlexxiSwitchesInRing()
        print ' '
        print '      Active switches (' , len(switches), ')'
        for target in switches:
            showSwitchSummary(target.getName())


def showSwitchNames():
    """ Prints a list of switch Names """
    switches = PlexxiSwitch.getAll()
    for switch in switches:
        print 'Switch : ',switch.getName()

def showSwitchPeers(switchId=None):
    """ 
    Prints a list of switch Peers

    switchId - name or mac of switch, str 'All' for all switches
    
    Goes through uplink (ring port) cable and prints the peer switch at the end of that cable
    This gives a complete map of switch uplink port to port connectivity through the Ring    
    """
    switchFound = False
    if switchId == 'All':
        switchFound = True
    for switch in PlexxiSwitch.getAll():
        if switchId != 'All':
            if str(switch.name) != switchId:
                continue
            else:
                print 'switchFound =', switch.name
                switchFound = True
        fabrics = switch.getAllSwitchFabrics()
        peerOutPortsMap = {}
        peerInPortsMap = {}
        outportCount = 0
        inportCount = 0
        if(len(fabrics) >=1):
            fabric = fabrics[0]
            outPorts = fabric.getAllSwitchFabricOutPorts()
            inPorts = fabric.getAllSwitchFabricInPorts()
            for port in outPorts:
                swId = port.getSwId()
                hwId = port.getHwId()
                isAccessPort = port.isAccessPort()
                if(isAccessPort == False):
                    outportCount = outportCount + 1
                    peerPorts = port.getAllPeerSwitchPorts()
                    for peerPort in peerPorts:
                        peerSwId = peerPort.getSwId()
                        peerHwId = peerPort.getHwId()
                        component = peerPort.getComponent()
                        peerSwitch = component.getPlexxiSwitch()
                        peerSwitchName = peerSwitch.getName()
                        peerDisplayString = peerSwitchName + '.(' + str(peerSwId) + ')'
                        peerOutPortsMap[swId] = peerDisplayString
            for port in inPorts:
                swId = port.getSwId()
                hwId = port.getHwId()
                isAccessPort = port.isAccessPort()
                if(isAccessPort == False):
                    inportCount = inportCount + 1
                    peerPorts = port.getAllPeerSwitchPorts()
                    for peerPort in peerPorts:
                        peerSwId = peerPort.getSwId()
                        peerHwId = peerPort.getHwId()
                        component = peerPort.getComponent()
                        peerSwitch = component.getPlexxiSwitch()
                        peerSwitchName = peerSwitch.getName()
                        peerDisplayString = peerSwitchName + '.(' + str(peerSwId) + ')'
                        peerInPortsMap[swId] = peerDisplayString
        sortedOutPeerMap = sorted(peerOutPortsMap)
        sortedInPeerMap  = sorted(peerInPortsMap)
        print '\nPeering on switch [ ', switch.getName(), ']'
        print '\n'
        print '\tOutport', 'PeerSwitch.InPort'
        print '\t-------', '-------------------'
        for key in sortedOutPeerMap:
            print '\t', key, '\t', peerOutPortsMap.get(key)
        print ' '
        print '\tNumber of OutPorts with peers:', len(sortedOutPeerMap), ', out of total uplink outPorts: ', outportCount
        print '\n'
        print '\tInPort', 'PeerSwitch.OutPort'
        print '\t-------', '-------------------'
        for key in sortedInPeerMap:
            print '\t', key, '\t', peerInPortsMap.get(key)
        print ' '
        print '\tNumber of InPorts with peers:', len(sortedInPeerMap), ', out of total uplink inPorts: ', inportCount
        print ' '
    if switchFound == False:
        print 'Switch Not Found', switchId

def showMac(macSearch):
    """ Prints extended Mac attachment information

    macSearch - mac string in the format "08:00:00:00:00:01"
    checks to see if the mac argument is found as a switch port mac attachment
    if its found, then displays all meta-data we have on this mac
    switch, port, and harvested information such as virtual machine or host
    """
    print ('showMac', macSearch)
    for ring in PlexxiRing.getAll():
        if len(ring.getAllPlexxiSwitchesInRing()) == 0:
            print 'ring bad'
            continue
        try:
            macIn = MacAddress(macAddress=macSearch)
        except:
            print 'something badly wrong'
            macIn = MacAddress.create(macIn)

        macs = AttachedNetworkDevice.getAllByMacAddress(macIn)
        if not macs:
            print 'Mac not found', macIn
            return 0
        for mac in macs:
            mac2 = str(mac.getMacAddress())
            if macSearch == mac2:
                lags = mac.getAllLogicalSwitchInPorts()
                if not lags:
                    print 'LogicalSwitchInPort not found'
                    return None
                for lag in lags:
                    ports = lag.getAllSwitchFabricInPorts()
                    if not ports:
                        print 'Ports not found - something bad'
                        return None
                    for port in ports:
                        switch = mac.getPrimarySwitch(macIn, 1, ring)
                        print 'Mac %s is on Plexxi Switch %s, port %s'%(str(mac.getMacAddress()), switch.getName(), port.getHwId()), 'VLAN ', mac.getVlan()
                        if(port.isLinkDown() == True):
                            link = 'Down'
                        else:
                            link = 'Up'
                        if port.isAdminStateEnabled() == True:
                            adminState = 'Enabled'
                        else:
                            adminState = 'Disabled'
                        print 'Port Link Status is %s, Admin State is %s'%(link, adminState)
  
                map = dict(lag.getAttachedNetworkDeviceMap())
                #print 'MAC MAP', map
                for key, value in map.iteritems():
                    #print str(key), str(mac.getMacAddress()), key, value
                    if str(key) == str(mac.getMacAddress()):
                        print 'List of harvested data for this Mac'
                        dicty = eval(value)
                        print 'HostName =', dicty["hostName"], '- VLANs =', dicty["vlanList"]
                return
                #return [switch, port.getHwId(), mac.getVlan(), map]
        print ''
        print 'Mac not found %s'%str(mac.getMacAddress())
        return None
    print 'Ring not found - something very bad'


def showFsat():
    """ prints out all the FSATs for all the Switches """
    print "%-17s    %-17s %-3s %-5s %-16s"%("Src Mac", "Dst Mac", "Wght", "Valid?", "Topology")
    print "-------------------------------------------------------------------------------------"
    for i in FullySpecifiedAffinityTopology.getAll():
        for j in i.getAffinityFlows():
            SrcMac = j.getSrcMacAddress()
            DstMac = j.getDstMacAddress()
        for j in i.getCandidateForwardingTopologies():
#            print "Candidate Topology:", j.getName()
            weight = j.getWeight()
            valid = j.getValidity()
            fwdt = j.getForwardingTopology()
            fwdTopo = fwdt.getName()
            ics = fwdt.getInterconnects()
            print "%17s -> %17s %3s %5s %16s"%(SrcMac,DstMac,weight,valid,fwdTopo)
            for ic in ics:
                print "     (%s)"%(ic.getName()),
                inport = ic.getInPort()
                print "- Leaving:",
                swId = inport.getSwId()
                hwId = inport.getHwId()
                peerPorts = inport.getAllPeerSwitchPorts()
                for peerPort in peerPorts:
                    peerSwId = peerPort.getSwId()
                    peerHwId = peerPort.getHwId()
                    component = peerPort.getComponent()
                    peerSwitch = component.getPlexxiSwitch()
                    peerSwitchName = peerSwitch.getName()
                    peerDisplayString = peerSwitchName + '/port' + str(peerSwId)
                    print peerDisplayString,
                outport = ic.getOutPort()
                print "Arriving:",
                swId = outport.getSwId()
                hwId = outport.getHwId()
                peerPorts = outport.getAllPeerSwitchPorts()
                for peerPort in peerPorts:
                    peerSwId = peerPort.getSwId()
                    peerHwId = peerPort.getHwId()
                    component = peerPort.getComponent()
                    peerSwitch = component.getPlexxiSwitch()
                    peerSwitchName = peerSwitch.getName()
                    peerDisplayString = peerSwitchName + '/port' + str(peerSwId)
                    print peerDisplayString
def showVlans():
    """ prints out all the VLANs for all Switches """
    totalVlans = VlanInterface.getCount()
    totalVlansUnassociated = len(VlanInterface.getAllUnassociated())
    totalVlansAssigned = 0
    switches = PlexxiSwitch.getAll()
    sortedSwitches = sorted(switches, key=operator.methodcaller("getName"))
    for switch in sortedSwitches:
        vlans = switch.getAllVlanInterfaces(VlanType.ALL)
        vlanCount = len(vlans)
        print "Switch " + switch.getName() + " - " + switch.getForeignUuid() + " (" + str(vlanCount) + " vlans)"
        sortedList = sorted(vlans, key=operator.methodcaller("getVlan"))
        for vlan in sortedList:
            printVlan(vlan, "  ")
        print '\n'
        totalVlansAssigned += vlanCount
    totalVlansUnassigned = totalVlans - totalVlansUnassociated - totalVlansAssigned
    message = "Vlans in system: " + str(totalVlans)
    message += " (unassociated " + str(totalVlansUnassociated) + ")"
    message += ", assigned: " + str(totalVlansAssigned)
    message += ", unassigned: " + str(totalVlansUnassigned)
    print message

