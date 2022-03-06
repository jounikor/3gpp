#
# (c) 2021-2022 Jouni korhonen
#
import argparse
import paging
import rrcconfig as rrc
import nasconfig as nas

#
prs = argparse.ArgumentParser()
prs.add_argument("--nb-iot","-n",dest="rat_nbiot",action="store_true",default=False,
    help="Set NB-IOT mode. Defaults to LTE-M.")
prs.add_argument("--rel","-R",dest="rel",action="store",default=13,type=int,
    help="Set 3GPP Release. Defaults to Rel-13.")
prs.add_argument("--debug","-d",dest="debug",action="store_true",default=False,
    help="Enable debug information.")
prs.add_argument("--numrep","-r",dest="numrep",action="store",default="r1",type=str,
    help="Set MPDDCH or NPDCCH NumRepetitionPaging. Defaults to 'r1'.")

prs.add_argument("--drx","-D",dest="drx",action="store",type=str,default="rf256",
    help="Set UE specific I-DRX cycle in binary or SFNs. Defaults to 'rf256'")

grp_edrx = prs.add_argument_group("Extended DRX","Extended DRX required configurations")

grp_edrx.add_argument("--edrx","-E",dest="edrx",action="store",type=str,default=None,
    help="Set UE specific I-eDRX cycle in binary or SFNs. Default no I-eDRX.")

grp_edrx.add_argument("--ptw","-p",dest="PTW",action="store",type=str,default="256",
    help="Set PTW in binary or SFNs. Defaults to '256'.")

grp_edrx.add_argument("--s-tmsi","-s",dest="s_tmsi",type=int,default=None,
    help="Set S-TMSI for the UE. Required in case of I-eDRX.")

# UE specific DRX cycles
prs.add_argument("--ue-drx","-u",dest="uedrx",type=str,default=None,
    help="Set UE specific DRX cycle in binary or SFNs. Valid for LTE-M.")

prs.add_argument("--imsi","-i",dest="imsi",type=int,action="store",
    required=True,help="Set UE IMSI.")
#
prs.add_argument("--nB","-b",dest="nB",action="store",type=str,default="oneT",
    help="nB value, see 36.331 PCCH-Config. Defaults to 'oneT'.")
prs.add_argument("--nB-v1310",dest="nB_v1310",action="store",type=str,default=None,
    help="nB value, see 36.331 PCCH-Config-v1310. Defaults to None.")
prs.add_argument("--PNB","-P",dest="PNB",action="store",type=int,default=1,
    help="Number of LTE-M paging narrow bands. Defaults to 1.")
# to be NB-IOT R14 non-anchor paging
#prs.add_argument("--non_anchor","-n","")

args = prs.parse_args()

#
if (__name__ == "__main__"):
    
    # if debug dump command line parameters.. including default values
    if (args.debug):
        print("Current configuration:")
        print(f"  3GPP Release-{args.rel} {'NB-IOT' if args.rat_nbiot else 'LTE-M'}")
        print(f"  UE IMSI:                       {args.imsi}")

        if (args.s_tmsi):
            print(f"  UE S-TMSI:                     {args.s_tmsi}")

        if (not args.rat_nbiot):
            print(f"  Number of paging narrowbands:  {args.PNB}")
 
        print(f"  Default paging cycle:          {args.drx}")
        
        if (args.edrx):
            print(f"  Default extended paging cycle: {args.edrx[0]}")
            print(f"  Default paging time window:    {args.edrx[1]}")

        print(f"  nB:                            {args.nB}")

        if (args.nB_v1310 is not None):
            print(f"  nB-v1310:                      {args.nB_v1310}");

        if (not args.rat_nbiot):
            # For NB-IOT UE specific DRX cycles come after R14
            if (args.uedrx is not None):
                print(f"  UE specific DRX cycles:          {args.uedrx}")

        print(f"  Number of paging repetitions:  {args.numrep}")

    # Build configurations.. and check for NB-IOT
    if (args.rat_nbiot):
        sib22 = None

        # Check for non-anchor paging carriers and configurations
        if (args.rel > 13):
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


        pcchcfg = rrc.PCCH_Config_NB_r13(args.drx,args.nB,args.numrep)
        radcfg = rrc.RadioResourceConfigCommonSIB_NB_r13(pcchcfg)
        sib2 = rrc.SystemInformationBlockType2_NB_r13(radcfg)

    # LTE-M configurations
    else:
        # Here's a bit of an issue.. the PCCH_Config nB value 
        pcchcfg = rrc.PCCH_Config(args.drx,args.nB)
        pcchcfg_v1310 = rrc.PCCH_Config_v1310(args.PNB,args.numrep,args.nB_v1310)
        radcfg = rrc.RadioResourceConfigCommonSIB(pcchcfg,pcchcfg_v1310)
        sib2 = rrc.SystemInformationBlockType2(radcfg)

    # Common configurations: NAS and WUS
    # NB-IOT UE specific DRX not supported yet
    if (args.uedrx and not args.rat_nbiot):
       drx_ie = nas.DRXparametersIE(args.uedrx,args.rel,args.debug)
    else:
        drx_ie = None

    if (args.edrx):
        edrx_ie = nas.extendedDRXparametersIE(args.edrx[1],args.edrx[0],args.rat_nbiot,args.rel,args.debug) 
    else:
        edrx_ie = None


    # Create paging objects
    if (args.rat_nbiot):
        pass
    else:
        pass

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


