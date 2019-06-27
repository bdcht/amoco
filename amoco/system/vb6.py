# -*- coding: utf-8 -*-

# This code is part of Amoco
# Copyright (C) 2007 Axel Tillequin (bdcht3@gmail.com)
# published under GPLv2 license

from amoco.system.win32 import *
from amoco.system.structs import *

class VB6(PE):

    def __init__(self,p):
        PE.__init__(self,p)
        self.parseVB()


#------------------------------------------------------------------------------
with Consts("dwThreadFlags"):
    ApartmentModel = 0x1
    RequireLicense = 0x2
    Unattended     = 0x4
    SingleThreaded = 0x8
    Retained       = 0x10

@StructDefine("""
s*4  : szVbMagic
H    : wRuntimeBuild
s*14 : szLangDll
s*14 : szSecLangDll
H    : wRuntimeRevision
I    : dwLCID
I    : dwSecLCID
I    : lpSubMain
I    : lpProjectData
I    : fMdlIntCtls
I    : fMdlIntCtls2
I    : dwThreadFlags
I    : dwThreadCount
H    : wFormCount
H    : wExternalCount
I    : dwThunkCount
I    : lpGuiTable
I    : lpExternalTable
I    : lpComRegisterData
I    : bSZProjectDescription
I    : bSZProjectExeName
I    : bSZProjectHelpFile
I    : bSZProjectName
""",packed=True)
class EXEPROJECTINFO(StructFormatter):
    order = '<'
    def __init__(self,data="",offset=0):
        self.address_formatter('lpSubMain','lpProjectData')
        self.flag_formatter('fMdlIntCtls','fMdlIntCtls2')
        self.address_formatter('lpGuiTable','lpExternalTable')
        self.address_formatter('lpComRegisterData')
        self.flag_formatter('dwThreadFlags')
        if data:
            self.unpack(data,offset)
            assert self.szVbMagic == b'VB5!'
#------------------------------------------------------------------------------

with Consts("fControlType"):
    PictureBox = 0x1
    Label = 0x2
    TextBox = 0x4
    Frame = 0x8
    CommandButton = 0x10
    CheckBox = 0x20
    OptionButton = 0x40
    ComboBox = 0x80
    ListBox = 0x100
    HScrollBar = 0x200
    VScrollBar = 0x400
    Timer = 0x800
    Print = 0x1000
    Form = 0x2000
    Screen = 0x4000
    Clipboard = 0x8000
    Drive = 0x10000
    Dir = 0x20000
    FileListBox = 0x40000
    Menu = 0x80000
    MDIForm = 0x100000
    App = 0x200000
    Shape = 0x400000
    Line = 0x800000
    Image = 0x1000000
    DataQuery = 0x20
    OLE = 0x40
    UserControl = 0x100
    PropertyPage = 0x200
    Document = 0x400

#------------------------------------------------------------------------------

with Consts("dwThreadFlags"):
    ApartmentModel = 0x1
    RequireLicense = 0x2
    Unattended     = 0x4
    SingleThreaded = 0x8
    Retained       = 0x10

@StructDefine("""
I    : bRegInfo
I    : bSZProjectName
I    : bSZHelpDirectory
I    : bSZProjectDescription
c*16 : uuidProjectClsId
I    : dwTlbLcid
H    : wUnknown
H    : wTlbVerMajor
H    : wTlbVerMinor
""",packed=True)
class tagREGDATA(StructFormatter):
    order = '<'
    def __init__(self,data="",offset=0):
        if data:
            self.unpack(data,offset)
#------------------------------------------------------------------------------

with Consts("fObjectType"):
    Designer       = 0x2
    Class_Module   = 0x10
    User_Control   = 0x20
    User_Document  = 0x80

@StructDefine("""
I    : bNextObject
I    : bObjectName
I    : bObjectDescription
I    : dwInstancing
c*16 : uuidObject
I    : fIsInterface
I    : bUuidObjectIFace
I    : bUuidEventsIFace
I    : fHasEvents
I    : dwMiscStatus
b    : fClassType
b    : fObjectType
H    : wToolboxBitmap32
H    : wDefaultIcon
H    : fIsDesigner
I    : bDesignerData
""",packed=True)
class tagRegInfo(StructFormatter):
    order = '<'
    def __init__(self,data="",offset=0):
        self.flag_formatter('fObjectType')
        if data:
            self.unpack(data,offset)
#------------------------------------------------------------------------------

@StructDefine("""
c*16 : uuidDesigner
I    : cbStructSize
s*~I : bstrAddinRegKey
s*~I : bstrAddinName
s*~I : bstrAddinDescription
I    : dwLoadBehaviour
s*~I : bstrSatelliteDll
s*~I : bstrAdditionalRegKey
I    : dwCommandLineSafe
""",packed=True)
class DesignerInfo(StructFormatter):
    order = '<'
    def __init__(self,data="",offset=0):
        if data:
            self.unpack(data,offset)

#------------------------------------------------------------------------------


@StructDefine("""
I    : dwVersion
I    : lpObjectTable
I    : dwNull
I    : lpCodeStart
I    : lpCodeEnd
I    : dwDataSize
I    : lpThreadSpace
I    : lpVbaSeh
I    : lpNativeCode
s*528: szPathInformation
I    : lpExternalTable
I    : dwExternalCount
""",packed=True)
class ProjectInfo(StructFormatter):
    order = '<'
    def __init__(self,data="",offset=0):
        self.address_formatter('lpObjectTable')
        self.address_formatter('lpCodeStart','lpCodeEnd')
        self.address_formatter('lpThreadSpace','lpVbaSeh')
        self.address_formatter('lpNativeCode','lpExternalTable')
        if data:
            self.unpack(data,offset)
#------------------------------------------------------------------------------

@StructDefine("""
I    : lpHeapLink
I    : lpObjectTable
I    : dwReserved
I    : dwUnused
I    : lpObjectList
I    : dwUnused2
I    : szProjectDescription
I    : szProjectHelpFile
I    : dwReserved2
I    : dwHelpContextId
""",packed=True)
class ProjectInfo2(StructFormatter):
    order = '<'
    def __init__(self,data="",offset=0):
        self.address_formatter('lpHeapLink','lpObjectTable')
        self.address_formatter('lpObjectList')
        if data:
            self.unpack(data,offset)
#------------------------------------------------------------------------------


@StructDefine("""
I    : lpHeapLink
I    : lpExecProj
I    : lpProjectInfo2
I    : dwReserved
I    : dwNull
I    : lpProjectObject
c*16 : uuidObject
I    : fCompileState
H    : wTotalObjects
H    : wCompiledObjects
H    : wObjectsInUse
I    : lpObjectArray
I    : fIdeFlag
I    : lpIdeData
I    : lpIdeData2
I    : lpszProjectName
I    : dwLcid
I    : dwLcid2
I    : lpIdeData3
I    : dwIdentifier
""",packed=True)
class ObjectTable(StructFormatter):
    order = '<'
    def __init__(self,data="",offset=0):
        self.address_formatter('lpHeapLink','lpExecProj','lpProjectInfo2')
        self.address_formatter('lpProjectObject','lpObjectArray')
        self.address_formatter('lpszProjectName')
        self.flag_formatter('fCompileState','fIdeFlag')
        if data:
            self.unpack(data,offset)
#------------------------------------------------------------------------------

@StructDefine("""
I    : lpHeapLink
I    : lpObjectInfo
I*3  : dwIdeData
I    : lpObjectList
I    : dwIdeData2
I    : lpObjectList2
I*3  : dwIdeData3
I    : dwObjectType
I    : dwIdentifier
""",packed=True)
class PrivateObject(StructFormatter):
    order = '<'
    def __init__(self,data="",offset=0):
        self.address_formatter('lpHeapLink','lpObjectInfo')
        self.address_formatter('lpObjectList','lpObjectList2')
        if data:
            self.unpack(data,offset)
#------------------------------------------------------------------------------

@StructDefine("""
I    : lpObjectInfo
I    : dwReserved
I    : lpPublicBytes
I    : lpStaticBytes
I    : lpModulePublic
I    : lpModuleStatic
I    : lpszObjectName
I    : dwMethodCount
I    : lpMethodNames
I    : bStaticvars
I    : fObjectType
I    : dwNull
""",packed=True)
class PublicObject(StructFormatter):
    order = '<'
    def __init__(self,data="",offset=0):
        self.address_formatter('lpObjectInfo')
        self.address_formatter('lpPublicBytes','lpStaticBytes')
        self.address_formatter('lpModulePublic','lpModuleStatic')
        self.address_formatter('lpszObjectName')
        self.address_formatter('lpMethodNames')
        self.flag_formatter('fObjectType')
        if data:
            self.unpack(data,offset)
#------------------------------------------------------------------------------

@StructDefine("""
H    : wRefCount
H    : wObjectIndex
I    : lpObjectTable
I    : lpIdeData
I    : lpPrivateObject
I    : dwReversed
I    : dwNull
I    : lpObject
I    : lpProjectData
H    : wMethodCount
H    : wMethodCount2
I    : lpMethods
H    : wConstants
H    : wMaxConstants
I    : lpIdeData2
I    : lpIdeData3
I    : lpConstants
""",packed=True)
class ObjectInfo(StructFormatter):
    order = '<'
    def __init__(self,data="",offset=0):
        self.address_formatter('lpObjectTable')
        self.address_formatter('lpIdeData','lpIdeData2', 'lpIdeData3')
        self.address_formatter('lpPrivateObject','lpObject', 'lpProjectData')
        self.address_formatter('lpMethods','lpConstants')
        self.address_formatter('lpMethodNames')
        self.flag_formatter('fObjectType')
        if data:
            self.unpack(data,offset)
#------------------------------------------------------------------------------

@StructDefine("""
I    : dwObjectGuids
I    : lpObjectGuid
I    : dwNull
I    : lpuuidObjectTypes
I    : dwObjectTypeGuids
I    : lpControls2
I    : dwNull2
I    : lpObjectGuid2
I    : dwControlCount
I    : lpControls
H    : wEventCount
H    : wPCodeCount
I    : bWInitializeEvent
I    : bWTerminateEvent
I    : lpEvents
I    : lpBasicClassObject
I    : dwNull3
I    : lpIdeData
""",packed=True)
class OptionalObjectInfo(StructFormatter):
    order = '<'
    def __init__(self,data="",offset=0):
        self.address_formatter('lpObjectGuid')
        self.address_formatter('lpuuidObjectTypes','lpControls2', 'lpObjectGuid2')
        self.address_formatter('lpControls','lpEvents')
        self.address_formatter('lpBasicClassObject')
        self.address_formatter('lpIdeData')
        if data:
            self.unpack(data,offset)
#------------------------------------------------------------------------------

@StructDefine("""
I    : fControlType
H    : wEventCount
I    : bWEventsOffset
I    : lpGuid
I    : dwIndex
I    : dwNull
I    : dwNull2
I    : lpEventTable
I    : lpIdeData
I    : lpszName
I    : dwIndexCopy
""",packed=True)
class ControlInfo(StructFormatter):
    order = '<'
    def __init__(self,data="",offset=0):
        self.address_formatter('lpGuid')
        self.address_formatter('lpEventTable')
        self.address_formatter('lpIdeData')
        self.address_formatter('lpszName')
        self.flag_formatter('fControlType')
        if data:
            self.unpack(data,offset)
#------------------------------------------------------------------------------
