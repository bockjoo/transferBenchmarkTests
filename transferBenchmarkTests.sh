#!/bin/bash
# Change the configuration between # === and # ===
# ========================================================
notifytowhom=b__empty__oc__empty__kjoo__AT__gmail__dot__com
workdir=$HOME/transferBenchmarkTests
DST_DIR=$workdir
export X509_USER_PROXY=_your_voms_proxy_file_

#export PATH=/home/bockjoo/bin:/home/bockjoo/opt/cmsio2/gfal2/bin:/home/bockjoo/opt/cmsio2/anaconda3/bin:/home/bockjoo/opt/cmsio2/anaconda3/condabin:/apps/ufrc/bin:/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/opt/puppetlabs/bin:/opt/dell/srvadmin/bin:/home/bockjoo/services/external/webisoget-2.8.4/bin
#export LD_LIBRARY_PATH=/home/bockjoo/opt/cmsio2/gfal2/lib64:/home/bockjoo/services/external/webisoget-2.8.4/lib:/usr/lib/x86_64-linux-gnu

# ========================================================
echo INFO checking voms proxy
which voms-proxy-info 2>/dev/null 1>/dev/null || source /cvmfs/oasis.opensciencegrid.org/osg-software/osg-wn-client/current/el$(source /cvmfs/cms.cern.ch/cmsset_default.sh ; cmsos| cut -d_ -f1 | sed 's#[a-z]\|[A-Z]##g')-x86_64/setup.sh
if [ $(voms-proxy-info -timeleft 2>/dev/null) -lt 3600 ] ; then
   echo ERROR voms-proxy-info -timeleft is less than an hour
   exit 1
fi
copytowhom=b__empty__oc__empty__kjoo__AT__gmail__dot__com
regions="US T1 T2"
ipvs="4 6"
regions="US"
#regions="T1"
#regions="T2"
#regions="US T1 T2"
ipvs="6"
htmls=""
#protocols="WebDAV"
updown="Download"
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
[ -d $workdir ] || mkdir -p $workdir
cd $workdir
which wget 2>/dev/null 1>/dev/null || source /cvmfs/oasis.opensciencegrid.org/osg-software/osg-wn-client/current/el$(source /cvmfs/cms.cern.ch/cmsset_default.sh ; cmsos| cut -d_ -f1 | sed 's#[a-z]\|[A-Z]##g')-x86_64/setup.sh
[ -f transferBenchmarkTests.py ] || wget -q -O transferBenchmarkTests.py https://raw.githubusercontent.com/bockjoo/transferBenchmarkTests/main/transferBenchmarkTests.py
for r in $regions ; do
   for ipv in $ipvs ; do
    #for protocol in $protocols ; do
     for updw in $updown ; do
       echo python3 transferBenchmarkTests.py $r $ipv $updw >  transferBenchmarkTests_${r}_${ipv}_${updw}.log
       python3 transferBenchmarkTests.py $r $ipv $updw >>  transferBenchmarkTests_${r}_${ipv}_${updw}.log
       html=$(cat transferBenchmarkTests_${r}_${ipv}_${updw}.log | grep html | tail -1)
       date_now=$(date +%Y%m%d%H%M%S)
       dst_html=${DST_DIR}/$(basename $html | sed "s#\.html#${date_now}.html#")
       echo INFO copying $html to $dst_html
       /bin/cp $html $dst_html
       htmls="$htmls $dst_html"
     done
    #done
   done
done
(
     echo "To: "$(echo $notifytowhom | sed "s#__AT__#@#" | sed "s#__dot__#\.#g" | sed "s#__empty__##g")
     echo "Cc: "$(echo $notifytowhom | sed "s#__AT__#@#" | sed "s#__dot__#\.#g" | sed "s#__empty__##g")
     echo "Subject: transferBenchmarkTests on $(/bin/hostname -s)"
     echo "Content-Type: text/html"
     echo
     for html in $htmls ; do
	 cat $html
     done
     echo
) | /usr/sbin/sendmail -t
cd -
exit 0
