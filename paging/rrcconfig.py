#
#
#
#

maxNPRACH_Resources_NB_r13 =    3
maxNonAnchorCarriers_NB_r14 =   16
maxAvailNarrowBands_r14 =       16

#
# in units of radio frames
ENUM_NB_defaultPagingCycle_r13 =    (128, 256, 512, 1024)
ENUM_LTEM_defaultPagingCycle =      (32, 64, 128, 256)

#
ENUM_nB_r13 = (
    4.0, 2.0, 1.0, 1.0/2, 1.0/4, 1.0/8, 1.0/16, 1.0/32, 1.0/64, 1.0/128,
    1.0/256, 1.0/512, 1.0/1024, 0, 0, None)
ENUM_npdcch_NumRepetitionPaging_r13 = (
    1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 0, 0, 0, 0)
ENUM_npdcch_NumRepetitionPaging_r14 = (
    1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 0, 0, 0, 0)
#ENUM_PagingWeight_NB_r14 = (
#    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)   #
ENUM_mpdcch_NumRepetitionPaging_r13 = (
    1, 2, 4, 8, 16, 32, 64, 128, 256)
nrep = (
    "r1", "r2", "r4", "r8", "r16", "r32", "r64", "r128", "r256")

ENUM_npdcch_NumRepetitionPaging_str =  (
    "r1", "r2", "r4", "r8", "r16", "r32", "r64", "r128",
    "r256", "r512", "r1024", "r2048")
ENUM_mpdcch_NumRepetition_Paging_str =  (
    "r1", "r2", "r4", "r8", "r16", "r32", "r64", "r128", "r256")

# Helper functions

def numrepetition_paging_to_index(s,LTEM=True):
    if (s is None):
        return None
    if (not LTEM):
        tab = ENUM_npdcch_NumRepetitionPaging_str
    else:
        tab = ENUM_mpdcch_NumRepetition_Paging_str

    if (s in tab):
        return tab.index(s)
    else:
        return None

#
# Returns:
#  Paging weight -1.. If the weight string is None then -1 is returned
#  to mean weight of w0. 
#
def pagingWeight_r14_to_index(s):
    w = ("w1", "w2", "w3", "w4", "w5", "w6", "w7", "w8",
         "w9", "w10", "w11", "w12", "w13", "w14", "w15", "w16")

    if (s in w):
        return w.index(s)
    if (s is None):
        return -1
    else:
        raise ValueError(f"Invalid paging weight '{s}'")


def NB_defaultPagingCycle_r13_to_index(s):
    cyc = ("rf128", "rf256", "rf512", "rf1024")

    if (s and s in cyc):
        return cyc.index(s)
    else:
        raise ValueError(f"Invalid default paging cycle '{s}'")

def defaultPagingCycle_r13_to_index(s):
    cyc = ("rf32", "r64", "rf128", "rf256")

    if (s and s in cyc):
        return cyc.index(s)
    else:
        return ValueError(f"Invalid nB value '{s}'")

def NB_nB_r13_to_index(s):
    nb = (  "fourT", "twoT", "oneT", "halfT", "quarterT", "one8thT", "one16thT", "one32ndT",
            "one64thT", "one128thT", "one256thT", "one512thT", "one1024thT") 
    
    if (s and s in nb):
        return nb.index(s)
    else:
        raise ValueError(f"Invalid nB value '{s}'")

def nB_r13_to_index(s,v1310=False):
    nb =        ("fourT", "twoT", "oneT", "halfT", "quarterT", "one8thT", "one16thT", "one32ndT")
    nb_v1310 =  ("one64thT", "one128thT", "one256thT")
    
    if (s is None):
        if (v1310):
            return -1
        else:
            raise ValueError("No nB value defined.")

    if (v1310):
        if (s in nb_v1310):
            return nb_v1310.index(s)+nb.__len__()
        else:
            raise ValueError(f"Invalid nB-v1310 value '{s}'")
    else:
        if (s in nb):
            return nb.index(s)
        else:
            raise ValueError(f"Invalid nB value '{s}'")


# R13
class PCCH_Config_NB_r13(object):
    def __init__(self, T, nB, rep ):
        T = NB_defaultPagingCycle_r13_to_index(T)
        nB = NB_nB_r13_to_index(nB)
        rep = numrepetition_paging_to_index(rep)
        
        self.defaultPagingCycle_r13 = ENUM_NB_defaultPagingCycle_r13[T]
        self.nB_r13 = ENUM_nB_r13[nB]
        self.npdcch_NumRepetitionPaging_r13 = ENUM_npdcch_NumRepetitionPaging_r13[rep]


class RadioResourceConfigCommonSIB_NB_r13(object):
    #
    # Params:
    #
    # kwargs params:
    #   wus_Config_r15 type of WUS-ConfigPerCarrier-NB-r15
    #
    #
    #
    #
    def __init__(self,pcch_config_nb_r13,**kwargs):
        self.pcch_Config_r13 = pcch_config_nb_r13

        #
        # [[  nprach-Config-v1530   NPRACH-ConfigSIB-NB-v1530   OPTIONAL
        #     dl-Gap-v1530          DL-GapConfig-NB-v1530       OPTIONAL
        #     wus-Config-r15        WUS-Config-NB-r15           OPTIONAL -- Need OE
        # ]]
        #

        if ("wus_Config_r15" in kwargs):
            self.wus_Config_r15 = kwargs["wus_Config_r15"]



class SystemInformationBlockType2_NB_r13(object):
    def __init__(self, radioresourceconfigcommonsib_nb_r13,**kwargs):
        self.radioResourceConfigCommon_r13 = radioresourceconfigcommonsib_nb_r13


class PCCH_Config(object):
    def __init__(self, T, nB):
        self.defaultPagingCycle = ENUM_LTEM_defaultPagingCycle[defaultPagingCycle_r13_to_index(T)]
        self.nB = ENUM_nB_r13[nB_r13_to_index(nB)] 

class PCCH_Config_v1310(object):
    def __init__(self,narrowbands,mpdcch_numreppag,nB=None):
        rep = numrepetition_paging_to_index(mpdcch_numreppag)
        self.mpdcch_NumRepetitionPaging_r13 = ENUM_mpdcch_NumRepetitionPaging_r13[rep]
        self.paging_narrowBands_r13 = narrowbands
        self.nB_v1310 = ENUM_nB_r13[nB_r13_to_index(nB,True)]


class RadioResourceConfigCommonSIB(object):
    def __init__(self,pcch,pcch_v1310,**kwargs):
        self.pcch_Config = pcch
        self.pcch_Config_v1310 = pcch_v1310


class SystemInformationBlockType2(object):
    def __init__(self,radioresourceconfigcommonsib,**kwargs):
        self.radioResourceConfigCommon = radioresourceconfigcommonsib



# R14
# 36.331 14.2.2 page 599 

#PCCH-ConfigList_NB_r14 ::= SEQUENCE (SIZE (1.. maxNonAnchorCarriers-NB-r14)) OF
# PCCH-Config-NB-r14

class PCCH_Config_NB_r14(object):
    def __init__(self, pagingWeight_NB_r14, **kwargs):
        if ("npdcch_NumRepetitionRaging_r14" in kwargs):
            npdcch_NumRepetitionPaging_r14 = numrepetition_paging_to_index(npdcch_NumRepetitionPaging_r14)+1
            self.npdcch_NumRepetitionPaging_r14 = ENUM_npdcch_NumRepetitionPaging_r14[npdcch_NumRepetitionPaging_r14]
        else:
            self.npdcch_NumRepetitionPaging_r14 = None

        # defaults to w1
        self.pagingWeight_r14 = pagingWeight_r14_to_index(pagingWeight_NB_r14) + 1

class DL_CarrierConfigCommon_NB_r14(object):
    def __init__(self,**kwargs):
        pass

class DL_ConfigCommon_NB_r14(object):
    def __init__(self,dl_CarrierConfig_r14,**kwargs):
        #  dl-CarrierConfig-r14     DL-CarrierConfigCommon-NB-r14,
        #  pcch-Config-r14          PCCH-Config-NB-r14              OPTIONAL -- Need OR
        #  ...,
        #  [[  wus-Config-r15       WUS-ConfigPerCarrier-NB-r15     OPTIONAL -- Cond WUS
        #  ]]

        # This IE is not really used..
        self.dl_CarrierConfig_r14 = dl_CarrierConfig_r14

        if ("pcch_Config_r14" in kwargs):
            self.pcch_Config_r14 = kwargs["pcch_Config_r14"]
        else:
            self.pcch_Config_r14 = None

        if ("wus_Config_r15" in kwargs):
            self.wus_Config_r15 = kwargs["wus_Config_r15"]
        else:
            self.wus_Config_r15 = None


class DL_ConfigCommonList_NB_r14(object):
    def __init__(self,dl_configcommonlist_nb_r14):
        #
        # DL-ConfigCommonList-NB-r14 ::= SEQUENCE (SIZE (1.. maxNonAnchorCarriers-NB-r14)) OF
        #                                        DL-ConfigCommon-NB-r14

        if (dl_configcommonlist_nb_r14):
            if (dl_configcommonlist_nb_r14.__len__() > maxNonAnchorCarriers_NB_r14):
                raise IndexError(f"DL_ConfigCommonList_NB_r14 too big")
        
            # This must be a list or tuple
            if (type(dl_configcommonlist_nb_r14) != list and
                type(dl_configcommonlist_nb_r14) != tuple):
                raise TypeError("dl_configcommonlist_nb_r14 not list or tuple")

        self.DL_ConfigCommonList_NB_r14 = dl_configcommonlist_nb_r14


class WUS_MaxDurationFactor_NB_r15(object):
    def __init__(self,duration):
        # WUS-MaxDurationFactor-NB-r15 ::= ENUMERATED {one128th, one64th, one32th, one16th,
        #                                              oneEighth, oneQuarter, oneHalf}
        n = ["one128th", "one64th", "one32th", "one16th", "oneEighth", "oneQuarter", "oneHalf"].index(duration)
        self.maxDurationFactor_r15 = 1.0 / (128 >> n)


class WUS_ConfigPerCarrier_NB_r15(object):
    def __init__(self,wus_MaxDurationFactor_r15):
        self.maxDurationFactor_r15 = wus_MaxDurationFactor_r15.maxDurationFactor_r15

class WUS_Config_NB_r15(object):
    def __init__(self, maxDurationFactor_r15, numPOs_r15, numDRX_CyclesRelaxed_r15,
        timeOffsetDRX_r15, timeOffset_eDRX_Short_r15, **kwargs):

        numPOs_r15 = 1 << ["n1","n2","n4"].index(numPOs_r15)
        numDRX_CyclesRelaxed_r15 = 1 << ["n1","n2","n4","n8"].index(numDRX_CyclesRelaxed_r15)
        timeOffsetDRX_r15         = {"ms40":40,"ms80":80,"ms160":160,"ms240":240}.get(timeOffsetDRX_r15)
        timeOffset_eDRX_Short_r15 = {"ms40":40,"ms80":80,"ms160":160,"ms240":240}.get(timeOffset_eDRX_Short_r15)

        self.maxDurationFactor_r15 = maxDurationFactor_r15.maxDurationFactor_r15
        self.numPOs_r15 = numPOs_r15
        self.numDRX_CyclesRelaxed_r15 = numDRX_CyclesRelaxed_r15
        self.timeOffsetDRX_r15 = timeOffsetDRX_r15
        self.timeOffset_eDRX_Short_r15 = timeOffset_eDRX_Short_r15

        if ("timeOffset_eDRX_Long_r15" in kwargs):
            timeOffset_eDRX_Long_r15 = kwargs["timeOffset_eDRX_Long_r15"]
            self.timeOffset_eDRX_Long_r15 = {"ms1000":1000,"ms2000":2000}.get(timeOffset_eDRX_Long_r15)

class SystemInformationBlockType22_NB_r14(object):
    def __init__(self,**kwargs):
        if ("dl_ConfigList_r14" in kwargs):
            dl_ConfigList_r14 = kwargs["dl_ConfigList_r14"]

            if (dl_ConfigList_r14):
                self.dl_ConfigList_r14 = dl_ConfigList_r14.DL_ConfigCommonList_NB_r14

        if ("pagingWeightAnchor_r14" in kwargs):
            self.pagingWeightAnchor_r14 = pagingWeight_r14_to_index(kwargs["pagingWeightAnchor_r14"])+1
        else:
            self.pagingWeightAnchor_r14 = 0
            
            if (hasattr(self, "dl_ConfigList_r14") == False):
                raise (RuntimeError("SystemInformationBlockType22_NB_r14.dl_ConfigList_r14 missing"))

# R12 - The IE UE-RadioPagingInfo-NB contains UE NB-IoT capability information needed for paging.
class UE_RadioPagingInfo_NB_r13(object):
    def __init__(self,**kwargs):
        self.ue_Category_NB_r13 = 0             # == "nb1"

        if ("mixedOperationMode_r15" in kwargs):
            self.mixedOperationMode_r15 = 0     # == "supported"
        if ("multiCarrierPaging_r14" in kwargs):
            self.multiCarrierPaging_r14 = True
        if ("wakeUpSignal_r15" in kwargs):
            self.wakeUpSignal_r15 = True
        if ("wakeUpSignalMinGap_eDRX_r15" in kwargs):
            n = kwargs["wakeUpSignalMinGap_eDRX_r15"]
            self.wakeUpSignalMinGap_eDRX_r15 = {"ms40":40,"ms240":240,"ms1000":1000,"ms2000":2000}.get(n)

#
#   if (wakeUpSignalMinGap_eDRX_r15 does not exist):
#        wakeUpSignalMinGap_eDRX_r15 = "40ms"
#
#
#
#
#
#
