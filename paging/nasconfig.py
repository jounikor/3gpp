#
#import exceptions


# In units of Radio Frames

tdrx = {
    "32":32,    "0110":32,
    "64":64,    "0111":64,
    "128":128,  "1000":128,
    "256":256,  "1001":256
}

# In units of Radio Frames
tedrx_nb = {
    "512":0, "0000":0,        # 24.008 10.5.5.32 Note 4
    "1024":0, "0001":0,       # 24.008 10.5.5.32 Note 4
    "2048":2048, "0010":2048,
    "4096":4096, "0011":4096,
    "6144":2048, "0100":2048,
    "8192":8192, "0101":8192,
    "10240":2048, "0110":2048,   # 24.008 10.5.5.32 Note 5
    "12288":2048, "0111":2048,   # 24.008 10.5.5.32 Note 5
    "14336":2048, "1000":2048,   # 24.008 10.5.5.32 Note 5
    "16384":16384, "1001":16384,
    "32768":32768, "1010":32768,
    "65536":65536, "1011":65536,
    "131072":131072, "1100":131072,
    "262144":262144, "1101":262144,
    "524288":524288, "1110":524288,
    "1048576":1048576,"1111":1048576
}

# In units of Radio Frames
tedrx_m1 = {
    "512":512,         "0000":512,
    "1024":1024,       "0001":1024,
    "2048":2048,       "0010":2048,
    "4096":4096,       "0011":4096,
    "6144":6144,       "0100":6144,
    "8192":8192,       "0101":8192,
    "10240":10240,     "0110":10240,
    "12288":12280,     "0111":12280,
    "14336":14336,     "1000":14336,
    "16384":16384,     "1001":16384,
    "32768":32768,     "1010":32768,
    "65536":65536,     "1011":65536,
    "131072":131072,   "1100":131072,
    "262144":262144,   "1101":262144,
    "524288":262144,   "1110":262144,    # 24.008 10.5.5.32 Note 6
    "1048576":262144,  "1111":262144    # 24.008 10.5.5.32 Note 6
}

# In units of Radio Frames
ptw_nb = {
    "256":256, "0000":256,
    "512":512, "0001":512,
    "768":768, "0010":768,
    "1024":1024, "0011":1024,
    "1280":1280, "0100":1280,
    "1536":1536, "0101":1536,
    "1792":1792, "0110":1792,
    "2048":2048, "0111":2048,
    "2304":2304, "1000":2304,
    "2560":2560, "1001":2560,
    "2816":2816, "1010":2816,
    "3072":3072, "1011":3072,
    "3328":3328, "1100":3328,
    "3584":3584, "1101":3584,
    "3840":3840, "1110":3840,
    "4096":4096,"1111":4096
}

ptw_m1 = {
    "128":128, "0000":128,
    "256":256, "0001":256,
    "384":384, "0010":384,
    "512":512, "0011":512,
    "640":640, "0100":640,
    "768":768, "0101":768,
    "896":896, "0110":896,
    "1024":1024, "0111":1024,
    "1152":1152, "1000":1152,
    "1280":1280, "1001":1280,
    "1408":1408, "1010":1408,
    "1536":1536, "1011":1536,
    "1664":1664, "1100":1664,
    "1792":1792, "1101":1792,
    "1920":1920, "1110":1920,
    "2048":2048,"1111":2048
}

#
#
#

class NAS(object):
    def __init__(self,rel,debug=False):
        self.rel = rel
        self.debug = debug

        if (rel < 13 or rel > 14):
            raise NotImplementedError(f"3GPP Release-{rel} paging supported")




#
class extendedDRXparametersIE(NAS):
    def __init__(self,ptw,edrx,nbiot=False,rel=13,debug=False):
        self.PTW = 0
        self.TeDRX = 0
        
        if (nbiot):
            local_ptw = ptw_nb
            local_drx = tedrx_nb
        else:
            local_ptw = ptw_m1
            local_drx = tedrx_m1

        if (ptw in local_ptw):
            self.PTW = local_ptw[ptw]

        if (edrx and edrx in local_drx):
            self.TeDRX=local_drx[edrx]
        else:
            raise ValueError(f"Invalid extended DRX value '{edrx}'")
            

        super(extendedDRXparametersIE,self).__init__(rel,debug)


#
class DRXparametersIE(NAS):
    def __init__(self,drx,rel=13,debug=False):
        if (drx and drx in tdrx):
            self.DRX = tdrx[drx]
        else:
            raise ValueError(f"Invalid DRX value '{drx}'")
       
        super(DRXparametersIE,self).__init__(rel,debug)
