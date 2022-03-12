#
# (c) 2021-2022 Jouni korhonen
#
import argparse
import paging
import rrcconfig as rrc
import nasconfig as nas

#
prs = argparse.ArgumentParser()
prs.add_argument("--nb-iot",dest="rat_nbiot",action="store_true",default=False,
    help="Set NB-IOT mode. Defaults to LTE-M.")
prs.add_argument("--rel",dest="rel",action="store",default=13,type=int,
    help="Set 3GPP Release. Defaults to Rel-13.")
prs.add_argument("--debug",dest="debug",action="store_true",default=False,
    help="Enable debug information.")
prs.add_argument("--verbose",dest="verbose",action="store_true",default=False,
    help="Enable verbose output.")
prs.add_argument("--numrep",dest="numrep",action="store",default="r1",type=str,
    help="Set MPDDCH or NPDCCH NumRepetitionPaging. Defaults to 'r1'.")

prs.add_argument("--drx",dest="drx",action="store",type=str,default="rf256",
    help="Set UE specific I-DRX cycle in binary or SFNs. Defaults to 'rf256'")

grp_edrx = prs.add_argument_group("Extended DRX","Extended DRX required configurations")

grp_edrx.add_argument("--edrx",dest="edrx",action="store",type=str,default=None,
    help="Set UE specific I-eDRX cycle in binary or SFNs. Default no I-eDRX.")

grp_edrx.add_argument("--ptw",dest="ptw",action="store",type=str,default="256",
    help="Set PTW in binary or SFNs. Defaults to '256'.")

grp_edrx.add_argument("--s-tmsi",dest="s_tmsi",type=int,default=0x12341234,
    help="Set S-TMSI for the UE. Required in case of I-eDRX. Defaults to 0x12341234.")
grp_edrx.add_argument("--num-hsfn",dest="num_hsfn",default=1,action="store",type=int,
    help="Number of H-SFNs to run simulation. Defaults to 1.")

# UE specific DRX cycles
prs.add_argument("--ue-drx",dest="uedrx",type=str,default=None,
    help="Set UE specific DRX cycle in binary or SFNs. Valid for LTE-M.")

prs.add_argument("--imsi",dest="imsi",type=int,action="store",default=123456789012345,
    help="Set UE IMSI. Defaults to 123456789012345.")
#
prs.add_argument("--nB",dest="nB",action="store",type=str,default="oneT",
    help="nB value, see 36.331 PCCH-Config. Defaults to 'oneT'.")
prs.add_argument("--nB-v1310",dest="nB_v1310",action="store",type=str,default=None,
    help="nB value, see 36.331 PCCH-Config-v1310. Defaults to None.")
prs.add_argument("--pnb",dest="PNB",action="store",type=int,default=1,
    help="Number of LTE-M paging narrow bands. Defaults to 1.")

prs.add_argument("--system-bw",dest="system_bw",default=10,action="store",type=float,
    help="LTE-M system bandwidth in MHz (1.4, 3, 5, 10, 15 or 20). Defaults to 10.")

# to be NB-IOT R14 non-anchor paging
prs.add_argument("--non-anchor",type=str,default=None,dest="non_anchor",nargs='+',
    help="List of non-anchor paging carrier weights.")

prs.add_argument("--paging-weight-anchor",type=str,default=None,dest="paging_weight_anchor",
    help="Weight of the anchor carrier.")


# Handle fractional nB cases
prs.add_argument("--fractional-nB",dest="fractional_nb",action="store_true",
    help="Allow paging calculation in nB < 1 cases so that 0 < N < 1 is possible.")


args = prs.parse_args()

#
if (__name__ == "__main__"):
    
    # if debug dump command line parameters.. including default values
    if (args.verbose):
        print("Current configuration:")
        print(f"  3GPP Release-{args.rel} {'NB-IOT' if args.rat_nbiot else 'LTE-M'}")

        if (not args.rat_nbiot):
            print(f"  System bandwidth:              {args.system_bw}MHz")

        print(f"  UE IMSI:                       {args.imsi}")
        print(f"  UE S-TMSI:                     {args.s_tmsi:#x}")

        if (not args.rat_nbiot):
            print(f"  Number of paging narrowbands:  {args.PNB}")
 
        print(f"  Default paging cycle:          {args.drx}")
        
        if (args.edrx):
            print(f"  Default extended paging cycle: {args.edrx} rf")
            print(f"  Default paging time window:    {args.ptw} rf")

        print(f"  nB:                            {args.nB}")

        if (not args.rat_nbiot and args.nB_v1310 is not None):
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
            nonanchors = None
            
            if (args.non_anchor):
                dl_configcommonlist_nb_r14 = [rrc.DL_ConfigCommon_NB_r14(
                    None,pcch_Config_r14=rrc.PCCH_Config_NB_r14(w)) for w in args.non_anchor]
                nonanchors = rrc.DL_ConfigCommonList_NB_r14(dl_configcommonlist_nb_r14)
            
            sib22 = rrc.SystemInformationBlockType22_NB_r14(dl_ConfigList_r14=nonanchors,
                                                    pagingWeightAnchor_r14=args.paging_weight_anchor)

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
        edrx_ie = nas.extendedDRXparametersIE(args.ptw,args.edrx,args.rat_nbiot,args.rel,args.debug) 
    else:
        edrx_ie = None

    # Create paging objects
    if (args.rat_nbiot):
        pg = paging.pagingNB(args.rel,args.fractional_nb,args.debug)
        pg.configure(sib2,sib22,edrx_ie)
    else:
        # Some sanity checks
        if (args.system_bw not in (1.4,3,5,10,15,20)):
            raise ValueError(f"Invalid system bandwidth {args.system_bw}MHz")

        pg = paging.pagingLTEM(args.system_bw,args.rel,args.fractional_nb,args.debug)
        pg.configure(sib2,drx_ie,edrx_ie)

    #
    # If non-anchor carriers are present & configured check on which
    # carrier paging takes place
    #

    paging_carrier = pg.paging_carrier(args.imsi)
    hsfn = 0
    sfn = 0
    sfn_count = 0

    # calculate simulation length
    if (pg.TeDRX > 0):
        sfn_max = 1024 * args.num_hsfn
        pg.init_PTW(False)
    else:
        sfn_max = max(256,pg.T)
        # If eDRX is not used we are always within the "PTW"..
        pg.init_PTW(True)

    # Simulation loop
    while (sfn_count < sfn_max):
        hsfn = (sfn_count >> 10) % 1024
        sfn  = sfn_count % 1024

        # Check if we are inside the Paging Hyperframe
        if (sfn % 1024 == 0):
            ph,PTW_sta,PTW_end,PTW_len = pg.gotpaged_eDRX(args.s_tmsi,hsfn)
        
            if (args.verbose):
                print( "START-OF-HYPER-FRAME-------------------------------")

            if (ph):
                pg.configure_PTW(PTW_sta,PTW_end,PTW_len)

        inside_ptw = pg.inside_PTW_test(sfn)
        got_paged = False

        if (inside_ptw):
            got_paged,pf,po = pg.gotpaged_DRX(args.imsi,sfn)

        # Do the print out..
        if (sfn % 256 == 0 and args.verbose):
            print(f"H-SFN   SFN     PH      PTW     PO      SF      PNB")

        if (got_paged):
            print(  f"*{hsfn:4d}  {sfn:4d}     {'Y' if ph else 'N'}       {'Y' if inside_ptw else 'N'}     "
                    f"{po:3d}     {pf:3d}       {paging_carrier} ")
        else:
            if (args.verbose):
                print(  f"{hsfn:5d}  {sfn:4d}     {'Y' if ph else 'N'}       {'Y' if inside_ptw else 'N'}       "
                        f"-       -       -")
        
        sfn_count += 1 



