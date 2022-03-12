#
# Version 0.1 (c) 2018 Jouni Korhonen
#
#

#import exceptions
import rrcconfig as rrc
import nasconfig as nas
import math as m

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
    SYSTEM_BW_1_4 = 1.4
    SYSTEM_BW_3   = 3
    SYSTEM_BW_5   = 5
    SYSTEM_BW_10  = 10
    SYSTEM_BW_15  = 15
    SYSTEM_BW_20  = 20

    #
    def init_PTW(self,edrx):
        self.inside_PTW = edrx
        self.ph = False

    #
    def configure_PTW(self,PTW_sta=None,PTW_end=None,PTW_len=None):
        self.PTW_sta = PTW_sta
        self.PTW_end = PTW_end
        self.PTW_len = PTW_len
        self.inside_PTW = True if PTW_sta is None else False
        self.ph = True

    #
    def inside_PTW_test(self,sfn):
        # Check if we need are inside the PTW
        if (self.ph and not self.inside_PTW):
            # Case 1: PTW_sta < PTW_end
            if (self.PTW_sta < self.PTW_end):
                if (sfn >= self.PTW_sta and sfn <= self.PTW_end):
                    self.inside_PTW = True
    
            # Case 2: PTW_sta > PTW_end i.e. PTW wrapped hyper frame boundary
            if (self.PTW_sta > self.PTW_end):
                if (sfn >= self.PTW_end and sfn <= self.PTW_sta):
                    self.inside_PTW = True
        #
        inside_PTW = self.inside_PTW
        
        #
        if (self.inside_PTW and self.ph):
            self.PTW_len -= 1
                
            if (self.PTW_len == 0):
                self.inside_PTW = False
                self.ph = False

        #
        return inside_PTW

    #
    def __init__(self,rel=13,fractional_nB=False,debug=False):
        self.rel = rel
        self.debug = debug
        self.fractional_nB = fractional_nB

        if (rel < 13 or rel > 14):
            raise NotImplementedError(f"3GPP Release-{rel} paging supportied")

    # modulo is for calculating the UE_ID
    # 36.304 subclause 7.1:
    #   IMSI mod 4096, if P-RNTI is monitored on NPDCCH.
    #   IMSI mod 16384, if P-RNTI is monitored on MPDCCH or if P-RNTI is monitored on NPDCCH
    #   and the UE supports paging on a non-anchor carrier, and if paging configuration for
    #   non-anchor carrier is provided in system information. 
    # This class is RAT agnostic thus the caller has to be RAT aware.
    #
    def setparameters(self,T,TeDRX,nB,sf_pattern,modulo,shift=0,L=0):
        self.T  = T
        self.TeDRX = TeDRX
        self.nB = nB

        # Sanity check with eDRX parameters
        if (L > TeDRX):
            raise ValueError(f"Extended DRX cycle less or equal than PTW.") 

        # This code takes into account the "fractional nB" case, which
        # was discussed in RAN2#105 and 106 meetings with an outcome:
        # "RAN2 understands that nB value can be fractional".
        # Here we have two implementation where 0 < N < 1 is possible or
        # N=1 when nB < 1
        self.N  = min(T,nB)

        if (self.fractional_nB is False and self.N < 1):
            self.N = 1

        self.Ns = int(max(1,nB/T))
        self.sf_pattern = sf_pattern
        self.modulo = modulo
        self.shift = shift
        self.L = L

        if (self.debug):
            print(f"In setparameters() -> Ns: {self.Ns}, modulo: {self.modulo}, shift: {self.shift}, L: {self.L}")

    # The algorithm is described in more detail in 36.304 Annex B
    def mod2div_(self,N,D):
        D <<= 31
        for i in range(32):
            if ((N & D) & 0x8000000000000000):
                N ^= D
            N <<= 1

        return N >> 32

    #
    def get_UE_ID(self,imsi):
        if (type(imsi) == str):
            imsi = int(imsi)

        return imsi % self.modulo

    # See 36.304 subclause 7.2 and Annex B
    def get_UE_ID_H(self,s_tmsi):
        if (type(s_tmsi) == str):
            s_tmsi = int(s_tmsi)

        Y1 = 0xC704DD7B
        D =  0x104C11DB7
        s_tmsi <<= 32       # k=32
        Y2 = self.mod2div_(s_tmsi,D)

        return ((Y1 ^ Y2) ^ 0xffffffff)

    # Check if there is a PO in this SFN. If yes return both PO and PF.
    def gotpaged_DRX(self,imsi,SFN):
        UE_ID = self.get_UE_ID(imsi)
        # 
        i_s = m.floor((UE_ID / self.N)) % self.Ns
        PO  = int(self.sf_pattern[self.Ns>>1][i_s])
        PF  = int((self.T / self.N) * (UE_ID % self.N))

        if (self.debug):
            print(f"SFN: {SFN}, UE_ID: {UE_ID:#06x}, PF: {PF}, i_s: {i_s}, PO: {PO}, "
                f"(T div N): {int(self.T/self.N)}, (UE_ID mod N): {UE_ID % self.N}") 
        
        return ((SFN % self.T) == PF),PF,PO

    #
    # Check if the s_tmsi has a potential PO within this HSFN. 
    #
    # Input:
    #  s_tmsi - s_tmsi for the UE
    #  HSFN   - 10 bit hyper frame counter
    #
    # Returns:
    #  pagehit, PTW_start, PTW_end, (HSFN % TeDRXH),(UE_ID_H % TeDRXH)
    #
    #  pagehit   - boolean if there is a potential PO in this HSFN
    #  PTW_start - start SFN for the PTW
    #  PTW_end   - end SFN % 1000 for the PTW
    #  L         - lenght of the PTW in SFNs
    #
    def gotpaged_eDRX(self,s_tmsi,HSFN):
        # extended DRX not in use
        if (self.TeDRX == 0):
            return False,0,0,0

        #
        if (type(s_tmsi) == str):
            s_tmsi = int(s_tmsi)

        TeDRXH = self.TeDRX >> 10

        # 36.304 subclause 7.3:
        #   UE_ID_H is 12 most significant bits, if P-RNTI is monitored on NPDCCH -> shift 20
        #   UE_ID_H is 10 most significant bits, if P-RNTI is monitored on (M=PDCCH -> shift 22
        #
        UE_ID_H_noshift = self.get_UE_ID_H(s_tmsi)
        UE_ID_H = UE_ID_H_noshift >> self.shift

        ieDRX = m.floor((UE_ID_H / TeDRXH)) % 4
        PTW_start = 256 * ieDRX
        # L is already *100
        PTW_end = (PTW_start + self.L - 1) % 1024
        
        if (self.debug):
            print(  f"In paging.gotpaged_eDRX()")
            print(  f"  HSFN = {HSFN} s_tmsi = {s_tmsi:#010x}")
            print(  f"  UE_ID_H_noshift = {UE_ID_H_noshift:#010x}, UE_ID_H = {UE_ID_H:#04x}")
            print(  f"  TeDRX>>10 (TeDRXH) = {TeDRXH}, ieDRX = {ieDRX}")
            print(  f"  PTW_start = {PTW_start}, PTW_end = {PTW_end}, L (PTW*100) = {self.L}")
            print(  f"  (HSFN % TeDRXH) = {HSFN % TeDRXH}, (UE_ID_H % TeDRXH) = {UE_ID_H % TeDRXH}")

        # PH is H-SFN when H-SFN mod TeDRX,H= (UE_ID_H mod TeDRX,H) 
        return ((HSFN % TeDRXH) == (UE_ID_H % TeDRXH)),PTW_start,PTW_end,self.L

    def get_timeout(self):
        pass

# LTE-M
class pagingLTEM(paging):
    def __init__(self,sysbw=paging.SYSTEM_BW_5,rel=13,frac=False,debug=False):
        # This mimics SIB1-BR eDRX-Allowed-r13 flag
        #
        # See 36.304 subclause 7.2 for system bw and RAT based
        # table selections.
        #
        super (pagingLTEM,self).__init__(rel,frac,debug)

        if (sysbw > paging.SYSTEM_BW_3):
            self.sf_pattern = sf_pattern_npdcch_or_mpdcch_gt_3MHz_fdd
        else:
            self.sf_pattern = sf_pattern_mpdcch_14_or_3MHz_fdd

        if (debug):
            print(  f"In pagingLTEM.__init__()\n"
                    f"  Release = {rel}\n"
                    f"  sysbw   = {sysbw}")

    #
    #
    def configure(self,sib2,drxie=None,edrxie=None):
        # get default paging cycle from SIB2
        T  = sib2.radioResourceConfigCommon.pcch_Config.defaultPagingCycle
        TeDRX = 0
        sf_pattern = self.sf_pattern
        modulo = 16384
        L = 0

        # If upper layer provided eDRX parameters configure based on those
        if (edrxie and hasattr(edrxie,"TeDRX")):
            # If upper layer provided eDRX cycle is 512 then monitor PO according
            # 36.304 subclause 7.1 algorithm using T = 512
            # Otherwise use subclause 7.3 algorithm to find the start of the
            # paging window and then use subclause 7.1 algorithm to find the PO
            if (edrxie.TeDRX < 1024):
                T = edrxie.TeDRX
                TeDRX = 0
            else:
                TeDRX = edrxie.TeDRX
                L = edrxie.PTW

        # If upper layer provided UE specific DRX parameter configuration..
        if (drxie and hasattr(edrxie,"DRX")):
            T = drxie.DRX
            TeDRX = 0

        # Precalculate nB
        if (sib2.radioResourceConfigCommon.pcch_Config_v1310.nB_v1310 is not None):
            nB = T * sib2.radioResourceConfigCommon.pcch_Config_v1310.nB_v1310
        else:
            nB = T * sib2.radioResourceConfigCommon.pcch_Config.nB

        # Paging narrow bands.
        self.Nn = sib2.radioResourceConfigCommon.pcch_Config_v1310.paging_narrowBands_r13

        if (self.debug):
            print(  f"In pagingLTEM.configure()\n"
                    f"  T = {T}, Nb = {nB}, Nn = {self.Nn}\n"
                    f"  TeDRX = {TeDRX}, L (PTW*100) = {L}\n"
                    f"  modulo = {modulo}, shift = {22}\n")

        # setup common parameters
        super(pagingLTEM,self).setparameters(T,TeDRX,nB,sf_pattern,modulo,22,L)

    #

    def paging_carrier(self,imsi):
        UE_ID = self.get_UE_ID(imsi)
        return int(1+m.floor((UE_ID / (self.N * self.Ns))) % self.Nn)


class pagingNB(paging):
    def __init__(self,rel,frac,debug):
        super (pagingNB,self).__init__(rel,frac,debug)
        self.rel = rel
        self.debug = debug
        self.sf_pattern = sf_pattern_npdcch_or_mpdcch_gt_3MHz_fdd
        #
        # See 36.304 subclause 7.2 for system bw and RAT based
        # table selections.
        #


    def configure(self,sib2,sib22=None,edrxie=None):
        sf_pattern = self.sf_pattern
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

            print(f"*** self.Nn = {self.Nn}, self.Wall = {self.Wall}")

            # If P-RNTI is monitored on NPDCCH and UE supports paging on a non-anchor
            # carrier then UE_ID = IMSI mod 16384
            modulo = 16384

        # get default paging cycle from SIB2-NB
        T  = sib2.radioResourceConfigCommon_r13.pcch_Config_r13.defaultPagingCycle_r13

        # If upper layer provided eDRX parameters configure based on those
        if (edrxie and hasattr(edrxie,"TeDRX")):
            # If upper layer provided eDRX cycle is 512 then monitor PO according
            # 36.304 subclause 7.1 algorithm using T = 512
            # Otherwise use subclause 7.3 algorithm to find the start of the
            # paging window and then use subclause 7.1 algorithm to find the PO
            if (edrxie.TeDRX > 1024):
                TeDRX = edrxie.TeDRX
                L = edrxie.PTW

        nB = T * sib2.radioResourceConfigCommon_r13.pcch_Config_r13.nB_r13
        
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
        wmod = m.floor((UE_ID / (self.N*self.Ns))) % self.Wall

        while (n <= self.Nn-1 and wmod >= self.W[n]):
            n += 1

        return m.floor(n)

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


