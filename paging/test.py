
import paging
import rrcconfig as rrc
import nasconfig as nas
#import exceptions



if (__name__ == "__main__"):
    nonanchors = rrc.DL_ConfigCommonList_NB_r14([
        rrc.DL_ConfigCommon_NB_r14(None,pcch_Config_r14=rrc.PCCH_Config_NB_r14("w1","r32")),
        rrc.DL_ConfigCommon_NB_r14(None,pcch_Config_r14=rrc.PCCH_Config_NB_r14("w2","r64")),
        rrc.DL_ConfigCommon_NB_r14(None,pcch_Config_r14=rrc.PCCH_Config_NB_r14("w1","r128")),
        rrc.DL_ConfigCommon_NB_r14(None,pcch_Config_r14=rrc.PCCH_Config_NB_r14("w3","r1024")),
        rrc.DL_ConfigCommon_NB_r14(None,pcch_Config_r14=rrc.PCCH_Config_NB_r14("w4"))
    ])
    sib22 = rrc.SystemInformationBlockType22_NB_r14(dl_ConfigList_r14=nonanchors,
                                                    pagingWeightAnchor_r14="w2")

    print("** sib22 **")
    print(sib22.pagingWeightAnchor_r14)
    print(sib22.dl_ConfigList_r14[0].pcch_Config_r14.npdcch_NumRepetitionPaging_r14)
    print(sib22.dl_ConfigList_r14[0].pcch_Config_r14.pagingWeight_r14)
    print(sib22.dl_ConfigList_r14[2].pcch_Config_r14.npdcch_NumRepetitionPaging_r14)
    print(sib22.dl_ConfigList_r14[2].pcch_Config_r14.pagingWeight_r14)
    print(sib22.dl_ConfigList_r14[4].pcch_Config_r14.pagingWeight_r14)

    pcchcfg = rrc.PCCH_Config_NB_r13("rf512","halfT","r32")
    radcfg = rrc.RadioResourceConfigCommonSIB_NB_r13(pcchcfg)
    sib2 = rrc.SystemInformationBlockType2_NB_r13(radcfg)
    print("Broadcasted DRX values:")
    print("\tdefault: ",sib2.radioResourceConfigCommon_r13.pcch_Config_r13.defaultPagingCycle_r13)
    print("\tnB: ",sib2.radioResourceConfigCommon_r13.pcch_Config_r13.nB_r13)
    print("\tnumrep: ",sib2.radioResourceConfigCommon_r13.pcch_Config_r13.npdcch_NumRepetitionPaging_r13)

    #edrx = nas.extendedDRXparametersIE(0b0001,0b0011)
    #print "eDRAX values: ",edrx.TeDRX,edrx.PTW

    nb = paging.pagingNB(14)
    #edrx = nb.configure(sib2,sib22,edrx)
    edrx = nb.configure(sib2,sib22,None)
    #edrx = nb.configure(sib2,None,edrx)

    if (edrx):
        print("UE specific I-eDRX enabled..")
    else:
        print("Cell specific I-eDRX enabled")


    #
    # Check for paging..
    #

    s_tmsi = 0x68cd5509e6 
    imsi   = 244125009125283
    hsfn = 0
    sfn = 0

    #
    # If non-anchor carriers are present & configured check on which
    # carrier paging takes place
    #

    paging_carrier = nb.paging_carrier(imsi)

    if (paging_carrier == 0):
        print("Paging on anchor carrier")
    else:
        print("Paging on non-anchor carrier {}".format(paging_carrier))

    #
    inPH = False
    PTWstart = sfn
    PTWend = sfn

    for n in range(1024):
    #for n in range(1024*1024):
    #for n in range(nb.TeDRX):

        if (edrx is True):
            if (not inPH):
                ph,s,e,phmod,uemod = nb.gotpaged_eDRX(s_tmsi,hsfn)

                if (ph is True):
                    inPH = True
                    PTWstart = s
                    PTWend = e
                    print("PH positive: H-SFN {}, SFN {}, PTW_start {}, PTW_end {}".format(hsfn,sfn,s,e))
                    print("\tPH modulo would be {} and UE_ID_H is {}".format(phmod,uemod))
        else:
            PTWstart = sfn
            PTWend = sfn

        # Since PTWstart and PTWend are modulo 1024 there are cases where PTWend is less
        # than PTWstart.. this has to be taken into account when comparing if the SFN is
        # between PTWstart and PTWend

        if (inPH is True or (not edrx)):
            p = False

            if (PTWstart > PTWend):
                if (sfn >= PTWstart and sfn >= PTWend):
                    p, pf, po = nb.gotpaged_DRX(imsi, sfn)
            else:
                if (sfn >= PTWstart and sfn <= PTWend):
                    p, pf, po = nb.gotpaged_DRX(imsi, sfn)

            if (p):
                print("Paging positive: H-SFN {}, SFN {}, PF {}, PO {}".format(hsfn,sfn,pf,po))
                inPH = False
                # Fast forward SFN when we found SF & PO for this example purposes.. 36.304 subclause 7.2 states:
                # "Otherwise, a UE configured with eDRX monitors POs as defined in 7.1 (i.e, based on the upper
                # layer configured DRX value and a default DRX value determined in 7.1), during a periodic Paging
                # Time Window (PTW) configured for the UE or until a paging message including the UE's NAS identity
                # is received for the UE during the PTW, whichever is earlier."
                sfn = 1023

        sfn += 1

        if (sfn >= 1024):
            inPH = False
            hsfn += 1
            sfn &= 1023
            hsfn &= 1023



