# transferBenchmarkTests
To run gfal-copy and xrdcp command to check the download rate from CMS US T1/T2 and CMS T1/T2 sites
to /dev/null
This uses /cvmfs/cms.cern.ch/SITECONF/local/storage.json to create the source of the download for sites

## Instruction to whoever participates in running the shell script
<pre>
1 Change # === #== section as needed, for example, X509_USER_PROXY should be set to a proper path
2 Change notifytowhom as needed, but keep copytowhom as is if possible.
3 Run it from a machine with the best network capability if possible, e.g., an xrootd server machine
</pre>
