#!/usr/bin/env python3
import sys
import re
import shlex, subprocess
from datetime import datetime
import os

def getStorageJson ( site ):
    import os.path
    from os import path
    import json
    
    storage_json='/cvmfs/cms.cern.ch/SITECONF/'+site+'/storage.json'
    if not path.exists(storage_json) : print ( 'no_storage_json' )
    #print ( "storage_json ",storage_json)
    with open(storage_json) as f: storage = f.read()
    try:
      storage = json.loads(str(storage))
    except:
      return {}
    return storage



def getpfnFromlfn (s,lfn,protocol):
    storage = getStorageJson ( s )
    pfns = []
    for index in range(len(storage)):
        if storage[index]['rse'] is None : continue
        if 'Tape' in storage[index]['rse'] : continue
        if 'Buffer' in storage[index]['rse'] : continue
        for iproto in range(len(storage[index]['protocols'])):
            if not protocol in storage[index]['protocols'][iproto]['protocol'] : continue
            ##print (storage[index]['protocols'][iproto]['protocol'])
            #print (storage[index]['protocols'][iproto].keys())
            if 'rules' in storage[index]['protocols'][iproto].keys() :
                #print ("Site: ", s , " dicts : ",storage[index]['protocols'][iproto].keys())
                for irule in range(len(storage[index]['protocols'][iproto]['rules'])) :
                    #print (storage[index]['protocols'][iproto]['rules'][irule]['lfn'], storage[index]['protocols'][iproto]['rules'][irule]['pfn'])
                    rule = storage[index]['protocols'][iproto]['rules'][irule]['lfn']
                    pfn = storage[index]['protocols'][iproto]['rules'][irule]['pfn']
                    match = re.match(rule, lfn)
                    if match :
                       #print(rule,' did match with the lfn ')
                       for count, s in enumerate(match.groups()):
                            ar='$'+str(count+1)
                            pfn = pfn.replace(ar,s)
                       #print (lfn)
                       #print (pfn)
                       pfns.append(pfn)
                    else :
                       pass
                       #print(rule,' did not match with the lfn ')
            elif 'prefix' in storage[index]['protocols'][iproto].keys() :
                #print ("Site: ", s , " dicts : ",storage[index]['protocols'][iproto].keys())
                pfn = storage[index]['protocols'][iproto]['prefix']+lfn
                #print (lfn)
                #print (pfn)
                pfns.append(pfn)
    return pfns

def getpfnFromlfnChain (s,lfn,protocol):
    storage = getStorageJson ( s )
    pfns = []
    for index in range(len(storage)):
        if storage[index]['rse'] is None : continue
        if 'Tape' in storage[index]['rse'] : continue
        if 'Buffer' in storage[index]['rse'] : continue
        for iproto in range(len(storage[index]['protocols'])):
            if not protocol in storage[index]['protocols'][iproto]['protocol'] : continue
            ##print (storage[index]['protocols'][iproto]['protocol'])
            #print (storage[index]['protocols'][iproto].keys())
            if 'rules' in storage[index]['protocols'][iproto].keys() :
                #print ("Site: ", s , " dicts : ",storage[index]['protocols'][iproto].keys())
                for irule in range(len(storage[index]['protocols'][iproto]['rules'])) :
                        #print (storage[index]['protocols'][iproto]['rules'][irule]['lfn'], storage[index]['protocols'][iproto]['rules'][irule]['pfn'])
                        if 'chain' in storage[index]['protocols'][iproto]['rules'][irule].keys() :
                            rule = storage[index]['protocols'][iproto]['rules'][irule]['lfn']
                            match = re.match(rule, lfn)
                            if not match : continue
                            chain=storage[index]['protocols'][iproto]['rules'][irule]['chain']
                            rules=[]
                            for jproto in range(len(storage[index]['protocols'])):
                                if chain == storage[index]['protocols'][jproto]['protocol'] :
                                   rules = storage[index]['protocols'][jproto]['rules']
                            #print ( rules )
                            lfn_chain = ""
                            for rule in rules :
                                pfn = rule['pfn']
                                match = re.match( rule['lfn'], lfn )
                                if match :
                                   for count, s in enumerate(match.groups()):
                                        ar='$'+str(count+1)
                                        pfn = pfn.replace(ar,s)
                                   #pfns.append(pfn)
                                   lfn_chain = pfn
                                else : continue
                            count = 0
                            ar='$'+str(count+1)
                            pfn = storage[index]['protocols'][iproto]['rules'][irule]['pfn']
                            pfn = pfn.replace(ar,lfn_chain)
                            pfns.append(pfn)
                        else :
                            rule = storage[index]['protocols'][iproto]['rules'][irule]['lfn']
                            pfn = storage[index]['protocols'][iproto]['rules'][irule]['pfn']
                            match = re.match(rule, lfn)
                            if match :
                               #print(rule,' did match with the lfn ')
                               for count, s in enumerate(match.groups()):
                                    ar='$'+str(count+1)
                                    pfn = pfn.replace(ar,s)
                               pfns.append(pfn)
                            else :
                               pass
            elif 'prefix' in storage[index]['protocols'][iproto].keys() :
                #print ("Site: ", s , " dicts : ",storage[index]['protocols'][iproto].keys())
                pfn = storage[index]['protocols'][iproto]['prefix']+lfn
                #print (lfn)
                #print (pfn)
                pfns.append(pfn)
    return pfns

def run_xrd_commands(cmd,args,timelimit):
    import subprocess
    import time
    dev_null = open('/dev/null', 'r')
    errtxt = ''
    elapsed = -1.0
    out = ''
    err = ''
    if 'xrdcp' in cmd :
       xrd_args = [ 'perl','-e',"alarm "+str(timelimit)+" ; exec @ARGV", cmd,   # one-line wrapper that *actually* kills the command
                    "-DIConnectTimeout","30",
                    "-DITransactionTimeout","60",
                    "-DIRequestTimeout","60" ] + args
       #xrd_args = [ cmd ] + args
    elif 'gfal-copy' in cmd :
       #xrd_args = [ "source /cvmfs/oasis.opensciencegrid.org/osg-software/osg-wn-client/current/el8-x86_64/setup.sh && " + cmd ] + args
       xrd_args = [ "source /cvmfs/oasis.opensciencegrid.org/osg-software/osg-wn-client/current/el$(source /cvmfs/cms.cern.ch/cmsset_default.sh ; cmsos| cut -d_ -f1 | sed 's#[a-z]\|[A-Z]##g')-x86_64/setup.sh && " + cmd ] + args
       #xrd_args = [ cmd ] + args
    else :
       xrd_args = [ 'perl','-e',"alarm "+str(timelimit)+" ; exec @ARGV", cmd ] + args    

    #print ( "xrd_args ",xrd_args)
    #if 'xrdmapc' in cmd :
    #    xrd_args = [ cmd, ] + args    
    try:
        start = time.time()
        if 'gfal-copy' in cmd :
          proc = subprocess.Popen(xrd_args,
                                stdin=dev_null,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, shell=True)
        else :
          proc = subprocess.Popen(xrd_args,
                                stdin=dev_null,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (out, err) = proc.communicate()
        ret = proc.returncode
        elapsed = (time.time() - start)
        #print ( ' out ',out )
        #if 'xrdmapc' in cmd : return ('',out,err,elapsed)
        err_redir_index = err.rfind(b'Received redirection to')
        err_index3010 = err.rfind(b'(error code: 3010')  # (permission denied) may be sort-of-OK - we are talking to final storage already - UK
        err_index3005 = err.rfind(b'(error code: 3005')  # (no user mapping) - INFN
        if err_redir_index >= 0 and (err_index3010 >= 0 or err_index3005 >= 0):
            #print ("errtxt will be empty because ",err)
            errtxt = ''
        else:    
            #print ("errtxt will not be empty because ret ",ret," err ",err)
            if(ret > 0):
               errtxt = "client-side error - exit code "+str(ret)+"\n"
            err_index = err.rfind(b'Last server error')
            if err_index >= 0:
               err_end_index=err.find(b"\n",err_index)
               errtxt = errtxt + err[err_index:err_end_index]
            #print ("errtxt will not be empty because ret ",ret," err_index ", err_index, " err ",err)
    except Exception as e :
        errtext = errtxt + "Exception: "+str(e)
        out = 'Try did not work :O'
        print(out)
    dev_null.close()
    
    return (errtxt,out,err,elapsed, ret)

''' Main '''
#os.environ['X509_USER_PROXY'] = '/home/bockjoo/.cmsuser.proxy'
size = 739040.0
lfn='/store/mc/SAM/GenericTTbar/AODSIM/CMSSW_9_2_6_91X_mcRun1_realistic_v2-v1/00000/AE237916-5D76-E711-A48C-FA163EEEBFED.root'
sites_dict={"US":['T1_US_FNAL','T2_US_Caltech','T2_US_MIT','T2_US_Florida','T2_US_Nebraska','T2_US_Purdue','T2_US_UCSD','T2_US_Wisconsin','T2_US_Vanderbilt','T2_BR_SPRACE','T2_BR_UERJ'],"T1":['T1_DE_KIT','T1_ES_PIC','T1_FR_CCIN2P3','T1_IT_CNAF','T1_RU_JINR','T1_UK_RAL'], "T2":['T2_AT_Vienna','T2_BE_IIHE','T2_BE_UCL','T2_CH_CERN','T2_CH_CSCS','T2_CN_Beijing','T2_DE_DESY','T2_DE_RWTH','T2_EE_Estonia','T2_ES_CIEMAT','T2_ES_IFCA','T2_FI_HIP','T2_FR_GRIF','T2_FR_GRIF_IRFU','T2_FR_GRIF_LLR','T2_FR_IPHC','T2_GR_Ioannina','T2_HU_Budapest','T2_IN_TIFR','T2_IT_Bari','T2_IT_Legnaro','T2_IT_Pisa','T2_IT_Rome','T2_KR_KISTI','T2_PK_NCP','T2_PL_Cyfronet','T2_PL_Swierk','T2_PT_NCG_Lisbon','T2_RU_IHEP','T2_RU_INR','T2_RU_ITEP','T2_RU_JINR','T2_TR_METU','T2_TW_NCHC','T2_UA_KIPT','T2_UK_London_Brunel','T2_UK_London_IC','T2_UK_SGrid_Bristol','T2_UK_SGrid_RALPP']}
#protocol = 'WebDAV'
timeout=1800
ipv="4"
what="Download"
if len(sys.argv) > 3 :
    region = sys.argv[1]
    ipv = sys.argv[2] #lfn = sys.argv[2]
    #protocol = sys.argv[3]
    what = sys.argv[3]
else :
    print ("ERROR_NOT_ENOUGH_PARAMETERS")
    sys.exit(1)

sites=sites_dict[region]
if (len(sites) < 1 ) :
    print ("ERROR region=",region," is incorrect")
    sys.exit(1)
if not "4" in ipv and not "6" in ipv :
    print ("ERROR IPv=",ipv," is incorrect")
    sys.exit(1)
#if not "WebDAV" in protocol :
#    print ("ERROR protocol=",protocol," is incorrect")
#    sys.exit(1)
if not "Download" in what and not "Upload" in what :
    print ("ERROR UP- or Download=",what," is incorrect")
    sys.exit(1)
    
    
print ( "Region: ",region)
print ( "Sites : ",sites)
print ( "IPv : ",ipv)
#print ( "Protocol : ",protocol)
print ( "Download or Upload",what)

#sys.exit(0)

time_now = datetime.now().strftime("%b %d, %Y at %H:%M:%S").strip()

transfer_rate_html="transfer_rate_"+region+"_ipv"+ipv+"_"+what+".html"
file = open(transfer_rate_html,'w')
file.write( "<html>\n" )
file.write( "<b><FONT color='green' size=+2>"+region+" Tranfer "+what+" Rate "+" with ipv"+str(ipv)+" ("+str(time_now)+") </FONT></b><br/>\n" )
file.write( "<table>\n" )
file.write( "<tr bgcolor='yellow'><td>Site</td><td colspan=2 align='right'>gfal-copy Rate</td><td colspan=2 align='right'>xrdcp Rate</td><td>pfn</td></tr>\n" )
#file.close()
for s in sites:
   upfns=set()
   pfns_webdav = getpfnFromlfnChain (s,lfn,'WebDAV')
   for pfn_webdav in pfns_webdav :
       host=pfn_webdav.replace(":"," ").replace("/"," ").split()[1]
       pfns_xrootd = getpfnFromlfnChain (s,lfn,'XRootD')
       for pfn_xrootd in pfns_xrootd :
           #match = re.match('(.*)'+host+'(.*)',pfn_xrootd)
           #if match :
           upfns.add(pfn_webdav+"|"+pfn_xrootd)
           #else :
           #   upfns.add('None|'+pfn_xrootd)
              
   pfns_xrootd = getpfnFromlfnChain (s,lfn,'XRootD')
   for pfn_xrootd in pfns_xrootd :
       host=pfn_xrootd.replace(":"," ").replace("/"," ").split()[1]
       pfns_webdav = getpfnFromlfnChain (s,lfn,'WebDav')
       for pfn_webdav in pfns_webdav :
           #match = re.match('(.*)'+host+'(.*)',pfn_webdav)
           #if match :
           upfns.add(pfn_webdav+"|"+pfn_xrootd)
           #else :
           #   upfns.add(pfn_webdav+'|None')
              
   for pfnp in upfns:
       pfn_webdav=pfnp.replace("|"," ").split()[0]
       pfn_xrootd=pfnp.replace("|"," ").split()[1]
       if 'davs:' in pfn_webdav or 'https:' in pfn_webdav :
          (errtext,out,err,elapsed,ret_davs) = run_xrd_commands("gfal-copy -f -"+ipv+" -t "+str(timeout)+" "+pfn_webdav+" /dev/null",[], timeout)
          rate_gfal_copy = "{:.2f}".format( size / 1000.0 / elapsed )
          print ( "WebDAV errtext ",errtext," out ",out," err ",err, " elapsed ",elapsed, " ret ",ret_davs)
       else :
          rate_gfal_copy = 'N/A'
       if 'root:' in pfn_xrootd :
          (errtext,out,err,elapsed,ret_root) = run_xrd_commands("xrdcp",
                                                 ["-d","1",
                                                  "-f",
                                                  "-DSNetworkStack","IPv"+str(ipv),
                                                  "-DIReadCacheSize","0",
                                                  "-DIRedirCntTimeout","180",
                                                  pfn_xrootd,
                                                  '/dev/null'],180)
          rate_xrdcp = "{:.2f}".format( size / 1000.0 / elapsed )
          print ( "XRootD errtext ",errtext," out ",out," err ",err, " elapsed ",elapsed, " ret ",ret_davs)
       else :
          rate_xrdcp = 'N/A'
          
       #print (s, " Rate : ", rate, " MB/s " , " pfn = ",pfn)
       file.write( "<tr bgcolor='yellow'><td>"+s+"</td><td align='right'>"+str(rate_gfal_copy)+"<br/>"+str(ret_davs)+"</td><td>MB/s</td>"+"<td align='right'>"+str(rate_xrdcp)+"<br/>"+str(ret_root)+"</td><td>MB/s</td><td>"+pfn_webdav+"<br/>"+pfn_xrootd+"</td></tr>\n" )
   #break
file.write( "</table>\n" )
time_now = datetime.now().strftime("%b %d, %Y at %H:%M:%S").strip()
file.write( "<b><FONT color='green' size=+2>"+region+" Tranfer "+what+" Rate "+" with ipv"+str(ipv)+" ("+str(time_now)+") </FONT></b><br/>\n" )
file.write( "</html>\n" )
file.close()
#print ("http://cmsio2.rc.ufl.edu:2811/view/T2/ops/Work/Rucio/"+gfal_copy_rate_html)
print (os.getcwd()+"/"+transfer_rate_html)
