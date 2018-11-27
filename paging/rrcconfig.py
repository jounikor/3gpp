#
#
#
#
#
#
#

maxNPRACH_Resources_NB_r13 = 3
maxNonAnchorCarriers_NB_r14 = 16
maxAvailNarrowBands_r14 = 16

#
# in units of radio frames
ENUM_NB_defaultPagingCycle_r13 = (128, 256, 512, 1024)
ENUM_LTEM_defaultPagingCycle = (32, 64, 128, 256)

#
ENUM_nB_r13 = (
    4.0, 2.0, 1.0, 1.0/2, 1.0/4, 1.0/8, 1.0/16, 1.0/32, 1.0/64, 1.0/128,
    1.0/256, 1.0/512, 1.0/1024, 0, 0, 0)
ENUM_npdcch_NumRepetitionPaging_r13 = (
    1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 0, 0, 0, 0)
ENUM_npdcch_NumRepetitionPaging_r14 = (
    1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 0, 0, 0, 0)
ENUM_PagingWeight_NB_r14 = (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)   #
ENUM_mpdcch_NumRepetition_Paging_r13 = (
    1, 2, 4, 8, 16, 32, 64, 128, 256)
nrep = (
    "r1", "r2", "r4", "r8", "r16", "r32", "r64", "r128", "r256")

ENUM_npdcch_NumRepetitionPaging_str =  (
    "r1", "r2", "r4", "r8", "r16", "r32", "r64", "r128",
    "r256", "r512", "r1024", "r2048")
ENUM_mpdcch_NumRepetition_Paging_str =  (
    "r1", "r2", "r4", "r8", "r16", "r32", "r64", "r128", "r256")

# Helper functions

def numrepetition_paging_to_index(s,NBIOT=True):
    if (s is None):
        return None
    if (NBIOT):
        tab = ENUM_npdcch_NumRepetitionPaging_str
    else:
        tab = ENUM_mpdcch_NumRepetition_Paging_str

    if (s in tab):
        return tab.index(s)
    else:
        return None


def pagingWeight_r14_to_index(s):
    w = ("w1", "w2", "w3", "w4", "w5", "w6", "w7", "w8",
         "w9", "w10", "w11", "w12", "w13", "w14", "w15", "w16")

    if (s is None):
        return None

    if (s in w):
        return w.index(s)
    else:
        return None


def NB_defaultPagingCycle_r13_to_index(s):
    cyc = ("rf128", "rf256", "rf512", "rf1024")

    if (s is None):
        return None

    if (s in cyc):
        return cyc.index(s)
    else:
        return None

def nB_r13_to_index(s):
    nb = (  "fourT", "twoT", "oneT", "halfT", "quarterT", "one8thT",
            "one16thT", "one32ndT", "one64thT",
            "one128thT", "one256thT", "one512thT", "one1024thT") 
    
    if (s is None):
        return None

    if (s in nb):
        return nb.index(s)
    else:
        return None






# R13
class PCCH_Config_NB_r13(object):
    def __init__(self, T, nB, rep ):
        if (type(T) == str):
            T = NB_defaultPagingCycle_r13_to_index(T)
        if (type(nB) == str):
            nB = nB_r13_to_index(nB)
        if (type(rep) == str):
            rep = numrepetition_paging_to_index(rep)
        
        self.defaultPagingCycle_r13 = ENUM_NB_defaultPagingCycle_r13[T]
        self.nB_r13 = int(self.defaultPagingCycle_r13 * ENUM_nB_r13[nB])
        self.npdcch_NumRepetitionPaging_r13 = ENUM_npdcch_NumRepetitionPaging_r13[rep]


class RadioResourceConfigCommonSIB_NB_r13(object):
    def __init__(self,pcch_config_nb_r13):
        self.pcch_Config_r13 = pcch_config_nb_r13


class SystemInformationBlockType2_NB_r13(object):
    def __init__(self, radioresourceconfigcommonsib_nb_r13):
        self.radioResourceConfigCommon_r13 = radioresourceconfigcommonsib_nb_r13


class PCCH_Config_v1310(object):
    def __init__(self,narrowbands,mpdcch_numreppag,nB):
        self.paging_narrowBands_r13 = narrowbands


class SystemInformationBlockType1_BR_r13(object):
    def __init__(self,narrowbands,mpdcch_numreppag,nB,rel=13):
        pass


# R14
# 36.331 14.2.2 page 599 

#PCCH-ConfigList_NB_r14 ::= SEQUENCE (SIZE (1.. maxNonAnchorCarriers-NB-r14)) OF
# PCCH-Config-NB-r14

class PCCH_Config_NB_r14(object):
    def __init__(self, npdcch_numrepetitionpaging_r14=None, pagingweight_nb_r14=None):
        if (pagingweight_nb_r14 is None):
            pagingweight_nb_r14 = 0
        if (type(npdcch_numrepetitionpaging_r14) == str):
            npdcch_numrepetitionpaging_r14 = numrepetition_paging_to_index(npdcch_numrepetitionpaging_r14)
        if (type(pagingweight_nb_r14) == str):
            pagingweight_nb_r14 = pagingWeight_r14_to_index(pagingweight_nb_r14)
       
        if (npdcch_numrepetitionpaging_r14):
            self.npdcch_NumRepetitionPaging_r14 = ENUM_npdcch_NumRepetitionPaging_r14[npdcch_numrepetitionpaging_r14]
        self.pagingWeight_r14 = ENUM_PagingWeight_NB_r14[pagingweight_nb_r14]

class PCCH_MultiCarrierConfig_NB_r14(object):
    def __init__(self,pcch_configlist_nb_r14,pagingweightanchor_r14=None):
        self.pcch_ConfigList_r14 = pcch_configlist_nb_r14
            
        if (type(pagingweightanchor_r14) == str):
            pagingweightanchor_r14 = pagingWeight_r14_to_index(pagingweightanchor_r14)
            
        if (pagingweightanchor_r14 is not None):
            self.pagingWeightAnchor_r14 = ENUM_PagingWeight_NB_r14[pagingweightanchor_r14]

class SystemInformationBlockType22_NB_r14(object):
    def __init__(self,pcch_multicarrierconfig_nb_r14=None):
        if (pcch_multicarrierconfig_nb_r14):
            self.pcch_MultiCarrierConfig_r14 = pcch_multicarrierconfig_nb_r14

# R15 (add WUS)
#
