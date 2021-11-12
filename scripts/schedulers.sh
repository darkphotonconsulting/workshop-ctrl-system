#!/usr/bi/env bash 

ACTION="${1:-start}"
MODULE_DOT_PATH="${2:-pylibs.sidecars.metrics.app}.celery"
RUN_PATH='./run'

function start_scheduler() {
    local module="$1"
    #echo "starting ${module}"
    /usr/bin/python3.7 -m celery -A "${module}" beat --pidfile "${RUN_PATH}/${module}.pid" --loglevel DEBUG --logfile "${RUN_PATH}/${module}-beat.log" --schedule "${RUN_PATH}/${module}-beat.db" >/dev/null 2>&1  & 
    #nohup
    disown %1
}

function stop_scheduler() {
    local module="$1"
    #echo "stopping ${module}"
    if [[ $(check_scheduler "$module" |wc -l)  -gt 0 ]]; then 
        pgrep -f "${module} beat" |xargs kill -9
    else 
        printf "%s\n" "no schedulers running to stop"
    fi
    #pgrep -f "${module}" |xargs kill -9
}

function check_scheduler() {
    local module="$1"
    #echo "checking ${module}"
    pgrep -a -f "${module} beat"
    #pgrep -a -f "${module}" 
}


if [[ "$ACTION" == "start" ]]; then 
    echo "starting ${MODULE_DOT_PATH} schedulers" 
    start_scheduler "${MODULE_DOT_PATH}"
fi

if [[ "$ACTION" == "stop" ]]; then 
    echo "stopping ${MODULE_DOT_PATH} schedulers"
    stop_scheduler "${MODULE_DOT_PATH}"
    #pgrep -f "${MODULE_DOT_PATH} beat" |xargs kill -9
fi

if [[ "$ACTION" == "status" ]]; then 
    echo "checking ${MODULE_DOT_PATH} schedulers"
    check_scheduler "${MODULE_DOT_PATH}"
    #pgrep -a -f "${MODULE_DOT_PATH} beat"
fi

if [[ "$ACTION" == "restart" ]]; then 
    echo "restarting ${MODULE_DOT_PATH}"
    if [[ $(check_scheduler "${MODULE_DOT_PATH}"|wc -l) -gt 0 ]]; then 
        stop_scheduler "${MODULE_DOT_PATH}"
        sleep 0.5
        start_scheduler "${MODULE_DOT_PATH}"
    else
        echo "no running schedulers for ${MODULE_DOT_PATH}"
    fi
    #stop_worker ""
    #start_worker ""

fi