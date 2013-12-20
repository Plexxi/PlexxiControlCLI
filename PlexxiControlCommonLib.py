#
# Copyright 2013 Plexxi, Inc.  All rights reserved.
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
from plexxi.core.api.util import *
from plexxi.core.api.dto import VlanInterfaceDto
import cmd 
import re 
import operator

############## globals so that the user can set the switch and port they are working on
configureSwitch = None
configureAffinityGroup = None
configurePort = 0
enable = False
config = False


#################Configuration commands to define or get persistant switch parameters


def getIdsByAG(agName):
  ags = AffinityGroup.getAll()
  for ag in ags:
    if ag.getName() == agName:
      return ag.getAffinityGroupElements()
  print 'AG not found', agName
  return None
      
def findSwitchFromNameMacorUuid(switchId):
    global configureSwitch
    if not switchId: 
        if configureSwitch == None:
            print ('Please specify switch')
            return False
        else:
            return configureSwitch
    switches = PlexxiSwitch.getAll()
    for switch in switches:
        if switch.getForeignUuid() == switchId:
            return switch
        if switch.getName() == switchId:
            return switch
#    if switch == switchId:
#      return switch
    print ("switch %s not found"%switchId)
    return False

def checkPortRange(port):
  if int(port) < 1 or int(port) >40:
    print ("port %s out of range 1-40"%port)
    return False
  else:  
    return port


def portIdList(startList):
  """
  Accepts a string of the format "1-5,7,8,10-13"
  and returns a list [1,2,3,4,5,7,8,10,11,12,13]
  """

  endList=[]
  if re.search(" ",startList):
    print('Please follow the format "1,2,3,6-9"(no spaces)')
    return
  myList = startList.split(",")
  for l in myList:
    if '-' in l:
      nums=l.split("-")
      for num in range(int(nums[0]),int(nums[1])+1):
        endList.append(num)
      continue
    endList.append(int(l))
  return endList

def deleteAllL2L3():
  """ Clears all Vlans & IPs from configuration """
  for v in VirtualRouter.getAll():
    v.delete()
  for v in VlanInterface.getAll():
    v.delete()
  for i in Ipv4Interface.getAll():
    i.delete()

def ipv4InterfaceCreateDto(ipstring, subnet, vlan):
  """
  accepts ip address string and returns dto
  """
  ip = InetAddress.getByName(ipstring)
  dto = Ipv4InterfaceDto()
  dto.setName(ipstring)
  dto.setEnabled(True)
  dto.setIpAddress(ip)
  dto.setSubnet(subnet)
  dto.setVlanInterfaceId(vlan)
  return dto

def ipv4InterfaceCreate(ipstring, subnet, vlan):
  """
  accepts ip address string and creates an ip address instance
  """
  dto = ipv4InterfaceCreateDto(ipstring, subnet,vlan)
  ip = Ipv4Interface.create(dto)
  return ip

def vlanCreateDto(vlanId):
  name = "VLAN-" + str(vlanId)
  dto = VlanInterfaceDto()
  dto.name = name
  dto.userLabel = name
  dto.vlan = vlanId
  return dto

def vlanCreate(vlanId):
  job=Job.create(name="Create vlanId %s"%vlanId)
  job.begin()
  vlan = VlanInterface.create(vlan=vlanId)
  job.commit()
  return vlan

def printVlan(vlan, indent=""):
  if vlan.isNativeVlan():
    nativeDetails = " Native "
  else:
    nativeDetails = "  "

  details = ": vlan " + str(vlan.getVlan()) + nativeDetails

  lags = vlan.getLinkAggregationGroupInPorts()
  details += "Ports: "
  portList = []
  for lag in lags:
    for port in lag.getAllSwitchFabricInPorts():
      portList.append(int(port.getHwId()))
  sortedList = sorted(portList)
  details += formatPageList(sortedList)
  printVlanObjectSummary(vlan, indent, details)

def formatPageList(numberlist):
    prev_number = min(numberlist) if numberlist else None
    pagelist = list()

    for number in sorted(numberlist):
        if number != prev_number+1:
            pagelist.append([number])
        elif len(pagelist[-1]) > 1:
            pagelist[-1][-1] = number
        else:
            pagelist[-1].append(number)
        prev_number = number

    return ','.join(['-'.join(map(str,page)) for page in pagelist])

def vlanGetSwitch(vlan):
  vlanTrunk = vlan.getVlanTrunkInterface()
  if vlanTrunk:
    lags = vlanTrunk.getLinkAggregationGroupInPorts()
    switch = getSwitchFromLags(lags)
    if switch:
      return switch
  lags = vlan.getLinkAggregationGroupInPorts()
  return getSwitchFromLags(lags)

def vlanTrunkGetSwitch(trunk):
  lags = trunk.getLinkAggregationGroupInPorts()
  return getSwitchFromLags(lags)

def vlanGetAllFloating():
  vlans = Set()
  for vlan in VlanInterface.getAll():
    switch = vlanGetSwitch(vlan)
    if switch == None:
      vlans.add(vlan)
  return setToList(vlans)


def getSwitchFromLag(lag):
  if lag:
    sfips = lag.getAllSwitchFabricInPorts()
    for sfip in sfips:
      sfip = sfips[0]
      fabric = sfip.getComponent()
      if fabric:
        switch = fabric.getPlexxiSwitch()
        if switch:
          return switch
  return None

def getSwitchFromLags(lags):
  for lag in lags:
    switch = getSwitchFromLag(lag)
    if switch:
      return switch
  return None

def setVlanObjectSummary(object, indent=""):
  global objectSummary
  #objectSummary = indent + "VlanInterface" + ": " + object.getName()
  objectSummary = indent + object.getName()
  return objectSummary

def printVlanObjectSummary(object, indent="", details=""):
  setVlanObjectSummary(object, indent)
  print objectSummary, details

