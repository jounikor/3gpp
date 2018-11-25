#
import exceptions


# In units of Radio Frames
tdrx  = (
    32, 64, 128, 256 )

tedrx = (
    512,1024,2048,4096,6144,8192,10240,12288,14336,
    16384,32768,65536,131072,262144,524288,1048576)

# In units of Radio Frames
nbptw = (
    256,512,768,1024,1280,1536,1792,2048,2304,2560,2816,3072,3328,3584,3840,4096)
m1ptw = (
    128,256,384,512,640,768,896,1024,1152,1280,1408,1536,1664,1792,1920,2048)

#
#
#

class NAS(object):
    def __init__(self,rel=13):
        self.rel = rel
        pass




#
class extendedDRXparametersIE(NAS):
    def __init__(self,ptw,edrx,nbiot=True,rel=13):
        if (nbiot):
            if (edrx < 0b0010):
                # 24.008 subclause 10.5.5.32 for NB-IoT eDRX periods
                # start from 2048 sf i.e., 20.48 sec
                raise ValueError("Invalid UE specific NB-IOT eDRX period")
            if (edrx == 0b0100 or (edrx >= 0b0110 and edrx < 0b1001)):
                # 24.008 subclause 10.5.5.32 for NB-IoT eDRX periods
                # 61.44, 102.4, 122.88, 143.36 sec are treated as 20.48 sec
                edrx = 0b0010
            self.PTW = nbptw[ptw]
        else:
            if (edrx > 0b1101):
                # 24.008 subclause 10.5.5.32 for WB-S1 mode 5242.88 and
                # 10485.76 sec are treated as 2621.44 sec
                edrx = 0b1101
            self.PTW = m1ptw[ptw]

        self.TeDRX = tedrx[edrx]

        super(extendedDRXparametersIE,self).__init__(rel)


#
class DRXparametersIE(NAS):
    def __init__(self,drx,nbiot=True,rel=13):
        if (drx >= 0b0110 and drx <= 0b1001):
            self.DRX = tdrx[drx-0b0110]

        super(DRXparametersIE,self).__init__(rel)