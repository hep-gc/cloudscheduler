#!/bin/bash
previous_time=`date +%s`
for i in `seq 1 5`; do
        echo "################################################################################################"
        echo "#"
        echo "#" $i `/bin/date` `/bin/hostname`
        echo "#"
        echo "################################################################################################"
        echo 

        echo "---> id"
        id
        echo 

        echo "---> condor_status -version"
        condor_status -version
        echo 

        echo "---> ls -l /cvmfs/atlas.cern.ch/repo"
        ls -l /cvmfs/atlas.cern.ch/repo
        echo 

        echo "---> mount"
        mount 
        echo " "

        echo "---> ifconfig"
        ifconfig
        echo " "

        echo "---> ping -c 100 -i 5 -R condor.heprc.uvic.ca"
        ping -c 25 condor.heprc.uvic.ca
        echo " "

        echo "---> tracepath lxplus.cern.ch"
        tracepath lxplus.cern.ch
        echo " "

        stats=(`cat /proc/uptime`)
        cpu_count=`grep processor /proc/cpuinfo | wc -l`
        pc_quotient=`echo "${stats[1]} * 10000 / ${cpu_count} / ${stats[0]} / 100" | bc`
        pc_remainder=`echo "${stats[1]} * 10000 / ${cpu_count} / ${stats[0]} % 100" | bc`
        current_time=`date +%s`
        elapse_time=$(($current_time - $previous_time))
        previous_time=$current_time
        echo '>>>>' $i'.' `/bin/hostname`', idle='$pc_quotient'.'$pc_remainder'%, elapse='$elapse_time 'seconds.'
        echo " "
done
exit 0

