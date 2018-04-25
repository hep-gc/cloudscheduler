node {
    checkout scm
    docker.image('mariadb').withRun('-e "MYSQL_ROOT_PASSWORD=pass-test"') {c ->
        docker.image('mariadb').inside("--link ${c.id}:db") {
            /* Wait for the db to setup */
            sh 'while ! mysqladmin ping -hdb --silent; do sleep 1; done'

            sh 'mysql -uroot --password=pass-test -hdb -e "CREATE DATABASE csv2;"'
            def table = readFile "schema/table_order"
            def tables = table.split()
            for (int i = 0; i < tables.size(); ++i){
                sh "mysql -uroot --password=pass-test -hdb -D csv2< schema/backup/${tables[i]}"
            }
            /*Insert needed data into db*/
            def condor_jobs = readFile "test-data/condor_jobs"
            def condor_machines = readFile "test-data/condor_machines"
            def os_general = readFile "test-data/os_general"
            def yaml = readFile "default.yaml.j2"
            sh """
               mysql -uroot -ppass-test -hdb -D csv2 -e "INSERT INTO csv2_config (config_name, yaml) VALUES ('condor_jobs', '${condor_jobs}')";
               mysql -uroot -ppass-test -hdb -D csv2 -e "INSERT INTO csv2_config (config_name, yaml) VALUES ('condor_machines', '${condor_machines}')";
               mysql -uroot -ppass-test -hdb -D csv2 -e "INSERT INTO csv2_config (config_name, yaml) VALUES ('os_general', '${os_general}')";
               """
        }
        docker.image('csv2:python3').inside("--link ${c.id}:db") {
            sh '''
               HOSTIP=`ip -4 addr show eth0 | grep 'inet ' | awk '{print $2}' | awk -F '/' '{print $1}'`
               sed -i "s/SETHOST/${HOSTIP}/g" /etc/condor/condor_config.local
               mysql -uroot -ppass-test -hdb -D csv2 -e "INSERT INTO csv2_groups (group_name, condor_central_manager) VALUES ('local-test', '${HOSTIP}')";
               systemctl start libvirtd
               systemctl start condor
               systemctl start virtlogd
               '''
            sleep 10
            sh '''
               cp -r /var/jenkins_home/workspace/cloudscheduler /opt/cloudscheduler
               mkdir /etc/cloudscheduler
               cp cloudscheduler.yaml /etc/cloudscheduler/

               cp data_collectors/cspollers.logrotate /etc/logrotate.d/cspollers.logrotate
               cp data_collectors/condor/cscollector.service /etc/systemd/system/cscollector.service
               cp data_collectors/condor/csjobs.service /etc/systemd/system/csjobs.service
               cp data_collectors/localhost/csmetadata.service /etc/systemd/system/csmetadata.service

               adduser cloudscheduler -s /sbin/nologin

               mkdir /var/log/cloudscheduler
               touch /var/log/cloudscheduler/csjobs.log
               touch /var/log/cloudscheduler/cscollector.log
               touch /var/log/cloudscheduler/localhostpoller.log
               chown cloudscheduler:cloudscheduler /var/log/cloudscheduler
               chown cloudscheduler:cloudscheduler /var/log/cloudscheduler/csjobs.log
               chown cloudscheduler:cloudscheduler /var/log/cloudscheduler/cscollector.log
               chown cloudscheduler:cloudscheduler /var/log/cloudscheduler/localhostpoller.log

               python3 setup.py install
               python setup.py install

               '''
            try{
                sh '''
                   systemctl daemon-reload
                   systemctl start csjobs
                   systemctl start cscollector
                   systemctl start csmetadata
                   '''
            }
            catch(exe){
                sh '''
                   cp /var/log/cloudscheduler/csjobs.log .
                   cp /var/log/cloudscheduler/cscollector.log .
                   cp /var/log/cloudscheduler/localhostpoller.log .
                   '''
                def jobs = readFile "csjobs.log"
                def collector = readFile "cscollector.log"
                def poller = readFile "localhostpoller.log"
                echo jobs
                echo collector
                echo poller
            }
            
            condor_nojob = sh(script: 'condor_q | grep jobs', returnStdout: true).trim()
            virsh_base = sh(script: 'virsh list --all', returnStdout: true).trim()

            try{
                sh '''
                   cp /jobs/try.job .
                   cp /jobs/try.sh .
                   sudo -u hep condor_submit try.job
                   '''
                sleep 15
                sh '''
                   python3 csmain-local
                   condor_q
                   '''
            }
            catch(exc){
                error('Job submission failed...')
            }
        }
    }
}
