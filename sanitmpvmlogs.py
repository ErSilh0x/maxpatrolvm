#!/usr/bin/python3

import os
import re
import argparse

#python3 sanitmpvmlogs.py --logs ./troubleshoot_dir

#Arguments
parser = argparse.ArgumentParser(description='Удаление паролей в логах диагностики Maxpatrol VM. Распакуйте архив'
                                             ' с логами, полученными от утилиты сбора логов в каталог'
                                             ' и задайте каталог скрипту.\n'
                                             'Delete passwords in Maxpatrol VM diagnostic logs.')
parser.add_argument('-l', '--logs', required=True, help='Enter directory with logs')
args = parser.parse_args()
catalog = args.logs

pass_patterns = [r'(PgPassword=)\S*',
                r'(PostgrePassword=)\S*'
                r'(ConsulSecret=)\S*',
                r'(EventStorageAuthPassword=)\S*',
                r'(MetricsPassword=)\S*',
                r'(RMQAgentPassword=)\S*',
                r'(RMQPassword=)\S*',
                r'(RMQSiemPassword=)\S*',
                r'(RMQAdminPassword=)\S*',
                r'(RMQSiemPassword=)\S*',
                r'(SmtpPassword=)\S*',
                r'(ClickHouseUserPassword=)\S*',
                r'(GrafanaAdminPassword=)\S*',
                r'(TelemetryInstanceAccessToken=)\S*',
                r'(ProxyPassword=)\S*',
                r'(--httpAuth.password=)\S*',
                r'(METRICS_PASSWORD=)\S*',
                r'(GF_SECURITY_ADMIN_PASSWORD=)\S*',
                r'(LogManager_ClickhousePassword=)\S*',
                r'(VictoriaMetrics_Password=)\S*',
                r'(VictoriaMetricsSettings_BasicAuthPassword=)\S*',
                r'(Database_VictoriaMetricsPassword=)\S*',
                r'(FRONTEND__LOGSPACE__SECURITY__PASSWORD=)\S*',
                r'(FRONTEND__CLICKHOUSE__SECURITY__PASSWORD=)\S*',
                r'(FRONTEND__ELASTICSEARCH__SECURITY__PASSWORD=)\S*',
                r'(RABBITMQ_ADMIN_PASS=)\S*',
                r'(RABBITMQ_SIEM_PASS=)\S*',
                r'(COLLECTOR_METRICS_PASSWORD=)\S*',
                r'(RABBITMQ_AGENT_PASS=)\S*',
                r'(PGADMIN_DEFAULT_PASSWORD=)\S*',
                r'(COLLECTOR_POSTGRESQL_PASSWORD=)\S*',
                r'(POSTGRES_PASSWORD=)\S*',
                r'(CONTENT_POSTGRES_PASSWORD=)\S*',
                r'(CONSUL_SECRET=)\S*',
                r'(HMRabbitSettings_Password=)\S*',
                r'(CONTENT_HM_RMQ_AUTH_PLAIN_PASSWORD=)\S*',
                r'(RabbitMq_Password=)\S*',
                r'(CSPF_HM_RMQ_AUTH_PLAIN_PASSWORD=)\S*',
                r'(RABBITMQ_CORE_PASS=)\S*'
                r'(FlusProxy_ProxyPassword=)\S*',
                r'(Password=)\S*',
                r'(Password:) \S*',
                r'(Password\":) \S*'
                ]

replace = ''
stats = {}

#Count statistics
def count_stat(p):
    if p in stats:
        stats[p] += 1
    else:
        stats[p] = 1

def clean_log(f):
    with open(f, 'r', encoding='utf-8', errors='ignore') as fr:
        lines = fr.readlines()

    with open(f, 'w', encoding='utf-8', newline='\n') as fw:
        for line in lines:
            for pattern in pass_patterns:

                #Search
                if re.search(pattern, line):
                    replace = re.search(pattern, line)
                    line = re.sub(pattern, replace.group(1), line, flags=re.IGNORECASE)
                    count_stat(replace.group(1).rstrip('='))
                    print(line)
                    #print(replace)

            fw.write(line)


for current_dir, subdirs, files in os.walk(catalog):
    #Current Iteration Directory
    #print('Current Directory: ', current_dir)

    #Directories
    '''for dirname in subdirs:
        print('\tSub Directory: ' + dirname)'''

    #Files
    for filename in files:
        fullpath = os.path.join(current_dir, filename)
        print('Parsing: ', fullpath)
        clean_log(fullpath)

#Statistics
for i in stats:
    print('Strings found: ', i, stats[i])
