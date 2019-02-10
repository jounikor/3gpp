#
# Version 0.1 (c) 2018 Jouni Korhonen
#
#

import exceptions
import rrcconfig as rrc
import nasconfig as nas

# See 36.304 subclause 7.2
#    i_s=0  i_s=1   i_s=2   i_s=3
sf_pattern_npdcch_or_mpdcch_gt_3MHz_fdd = (
    (9,     None,   None,   None),  # Ns = 1
    (4,     9,      None,   None),  # Ns = 2
    (0,     4,      5,      9)      # Ns = 4
)

# See 36.304 subclause 7.2
#    i_s=0  i_s=1   i_s=2   i_s=3
sf_pattern_mpdcch_14_or_3MHz_fdd = (
    (5,     None,   None,   None),  # Ns = 1
    (5,     5,      None,   None),  # Ns = 2
    (5,     5,      5,      5)      # Ns = 4
)

#

class paging(object):
    SYSTEM_BW_1_3 = 0
    SYSTEM_BW_3   = 1
    SYSTEM_BW_5   = 2
    SYSTEM_BW_10  = 3
    SYSTEM_BW_15  = 4
    SYSTEM_BW_20  = 5

    def __init__(self,rel=13):
        self.rel = rel

    def setparameters(self,T,TeDRX,nB,sf_pattern,modulo,shift=0,L=0):
        self.T  = T
        self.TeDRX = TeDRX
        self.nB = nB

        # This code does not take into account the "fractional N" cases. This is
        # discussed in rel-15 how it should be handled properly.
        # "Fractional N" means the case when nB < 0.
        self.N  = min(T,nB)

        #
        self.Ns = int(max(1,nB/T))
        self.sf_pattern = sf_pattern
        self.modulo = modulo
        self.shift = shift
        self.L = L

    def N(self):
        return self.N

    def Ns(self):
        return self.Ns

    # The algorithm is described in more detail in 36.304 Annex B
    def mod2div_(self,N,D):
        D <<= 31
        for i in xrange(32):
            if ((N & D) & 0x8000000000000000):
                N ^= D
            N <<= 1

        return N >> 32

    def get_UE_ID(self,imsi):
        if (type(imsi) == str):
            imsi = int(imsi)

        return imsi % self.modulo

        # 36.304 subclause 7.1
        #if (self._rat == paging.LTEM or (self._rat == paging.NBIOT and self.maxPagingCarriers > 0)):
        #    self._UE_ID = imsi % 16384
        #else:
        #    self._UE_ID = imsi % 4096
        #return self.UE_ID


    # See 36.304 subclause 7.2 and Annex B
    def get_UE_ID_H(self,s_tmsi):
        if (type(s_tmsi) == str):
            s_tmsi = int(s_tmsi)

        Y1 = 0xC704DD7B
        D =  0x104C11DB7
        s_tmsi <<= 32       # k=32
        Y2 = self.mod2div_(s_tmsi,D)

        return ((Y1 ^ Y2) ^ 0xffffffff)

    def gotpaged_DRX(self,imsi,SFN):
        UE_ID = self.get_UE_ID(imsi)
        # 
        i_s = (UE_ID / self.N) % self.Ns
        PO  = self.sf_pattern[self.Ns>>1][i_s]
        PF  = (self.T / self.N) * (UE_ID % self.N)
        #print "UE_ID {}, PF {}, PO {}, (self.T / self.N) {}, (UE_ID % self.N) {}".format(UE_ID,PF,PO,self.T/self.N,UE_ID%self.N)
        return ((SFN % self.T) == PF),PF,PO

    def gotpaged_eDRX(self,s_tmsi,HSFN):
        #
        if (type(s_tmsi) == str):
            s_tmsi = int(s_tmsi)

        #TeDRXH = self.TeDRX / 1024
        TeDRXH = self.TeDRX >> 10

        # 36.304 subclause 7.3
        # UE_ID_H is 12 most significant bits, if P-RNTI is monitored on NPDCCH -> shift 20
        # UE_ID_H is 10 most significant bits, if P-RNTI is monitored on (M=PDCCH -> shift 22
        #
        UE_ID_H = self.get_UE_ID_H(s_tmsi) >> self.shift

        ieDRX = (UE_ID_H / TeDRXH) % 4
        PTW_start = 256 * ieDRX
        PTW_end = (PTW_start + self.L - 1) % 1024

        #print "** UE_ID_H {}, ieDRX {}, (HSFN % self.T) {}, (UE_ID_H % self.T) {}".format(UE_ID_H,ieDRX, (HSFN % T), (UE_ID_H % T))

        return ((HSFN % TeDRXH) == (UE_ID_H % TeDRXH)),PTW_start,PTW_end,(HSFN % TeDRXH),(UE_ID_H % TeDRXH)

    def get_timeout(self):
        pass

# LTE-M is TBD
class pagingLTEM(paging):
    def __init__(self,sysbw=paging.SYSTEM_BW_5,rel=13):
        # This mimics SIB1-BR eDRX-Allowed-r13 flag
        #
        # See 36.304 subclause 7.2 for system bw and RAT based
        # table selections.
        #
        super (pagingLTEM,self).__init__(rel)

        if (sysbw > paging.SYSTEM_BW_3):
            sf_pattern = sf_pattern_npdcch_or_mpdcch_gt_3MHz_fdd
        else:
            sf_pattern = sf_pattern_mpdcch_14_or_3MHz_fdd

    def configure(self,sib1,sib2,drxie=None,edrxie=None):
        # get default paging cycle from SIB2
        T  = sib2.radioResourceConfigCommon_r13.pcch_Config_r13.defaultPagingCycle_r13
        nB = sib2.radioResourceConfigCommon_r13.pcch_Config_r13.nB_r13
        TeDRX = 0

        # If upper layer provided eDRX parameters configure based on those
        if (edrxie and hasattr(edrxie,"TeDRX")):
            # If upper layer provided eDRX cycle is 512 then monitor PO according
            # 36.304 subclause 7.1 algorithm using T = 512
            # Otherwise use subclause 7.3 algorithm to find the start of the
            # paging window and then use subclause 7.1 algorithm to find the PO
            if (edrxie.TeDRX < 1024):
                T = edrxie.TeDRX
            else:
                TeDRX = edrxie.TeDRX
                L = edrxie.PTW

        super(pagingNB,self).setparameters(T,TeDRX,nB,sf_pattern,modulo,L)

    #
    #
    #
    #
    #
    #
    #
    #
    #




    def paging_PNB(self,UE_ID,imsi):
        return (UE_ID / (self.N * self.Ns)) % self.Nn


class pagingNB(paging):
    def __init__(self,rel=13):
        super (pagingNB,self).__init__(rel)
        self.rel = rel
        #
        # See 36.304 subclause 7.2 for system bw and RAT based
        # table selections.
        #


    def configure(self,sib2,sib22=None,edrxie=None):
        sf_pattern = sf_pattern_npdcch_or_mpdcch_gt_3MHz_fdd
        modulo = 4096
        self.TeDRX = 0
        L = 0
        TeDRX = 0


        #
        # 34.304 subclause 7.1 for Rel-14 and greater

        # Index 0 is the anchor carrier.. and contains the weight of the carrier
        # Default to w0
        self.W    = [0]
        self.Nn   = 1
        self.Wall = 0

        # Also, the anchor carrier may have a weight
        if (sib22 and hasattr(sib22, "pagingWeightAnchor_r14")):
            # Anchor carrier weight is the index 0 of the pagingCarriersWeight
            # If pagingWeightAnchor is absent, then 36.331 sublause 6.7.3.1 for 
            # SystemInformationBlock22-NB states that w0 (=0 weight) for anchor carrier
            # is used, which means no paging takes place on anchor carrier.
            # 36.304 subclause 7.1 for paging carrier will always skip W[0] as its
            # weight is 0.
            
            self.W[0]  = sib22.pagingWeightAnchor_r14
            self.Wall += sib22.pagingWeightAnchor_r14

        # If non-anchor carriers exist..
        if (sib22 and hasattr(sib22, "dl_ConfigList_r14")):
            n = sib22.dl_ConfigList_r14.__len__()
            i = 0

            # SIB22-NB contained configuration for non-anchor carrier paging.
            # Calculate cumulativer total weight of all non-anchor carriers.
            while (i < n):
                self.Wall += sib22.dl_ConfigList_r14[i].pcch_Config_r14.pagingWeight_r14
                self.W.append(self.Wall)
                i += 1

            self.Nn += n

            # If P-RNTI is monitored on NPDCCH and UE supports paging on a non-anchor
            # carrier then UE_ID = IMSI mod 16384
            modulo = 16384

        # get default paging cycle from SIB2-NB
        T  = sib2.radioResourceConfigCommon_r13.pcch_Config_r13.defaultPagingCycle_r13
        nB = sib2.radioResourceConfigCommon_r13.pcch_Config_r13.nB_r13

        # If upper layer provided eDRX parameters configure based on those
        if (edrxie and hasattr(edrxie,"TeDRX")):
            # If upper layer provided eDRX cycle is 512 then monitor PO according
            # 36.304 subclause 7.1 algorithm using T = 512
            # Otherwise use subclause 7.3 algorithm to find the start of the
            # paging window and then use subclause 7.1 algorithm to find the PO
            if (edrxie.TeDRX < 1024):
                T = edrxie.TeDRX
            else:
                TeDRX = edrxie.TeDRX
                L = edrxie.PTW

        #print "Modulo {}, L {}".format(modulo,L)

        print "-->",TeDRX

        super(pagingNB,self).setparameters(T,TeDRX,nB,sf_pattern,modulo,20,L)
        return self.TeDRX > 0

    def paging_carrier(self,imsi):
        # Non-anchor paging supported only for Rel-14 or above, and
        # when non-anchor configuration has been provided in SIB22-NB.
        #
        # Returns:
        #  carrier number (0 is the anchor)
        #
        if (self.rel < 14 or self.Nn == 1):
            return 0

        n = 0
        UE_ID = self.get_UE_ID(imsi)

        # wmod = floor(UE_ID/(self.N*self.Ns)) mod W
        wmod = (UE_ID / (self.N*self.Ns)) % self.Wall
        
        while (n <= self.Nn-1 and wmod >= self.W[n]):
            n += 1

        return n




#def bdiv(N,D):
#
#    Q,R = 0,0
#    i = 1 << 64
#
#    while (i > 0):
#        R <<= 1
#        R |= (1 if (N & i) else 0)
#        if (R >= D):
#            R -= D
#            Q |= i
#        i >>= 1
#    
#    return Q,R


