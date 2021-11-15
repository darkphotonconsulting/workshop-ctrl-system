#!/usr/bi/env bash 

ACTION="${1:-start}"
MODULE_DOT_PATH="${2:-pylibs.sidecars.metrics.app}.celery"
RUN_PATH='./run'

function start_worker() {
    local module="$1"
    
    /usr/bin/python3.7 -m celery -A "${module}" worker  -l DEBUG  -E -D --logfile "${RUN_PATH}/${module}-worker.log" --pidfile "${RUN_PATH}/${module}-worker.pid"
}

# function stop_worker() {
#     local module="$1"

#     pgrep -f "${module} worker" |xargs kill -9
# }

function stop_worker() {
    local module="$1"
    #echo "stopping ${module}"
    if [[ $(check_worker "$module" |wc -l)  -gt 0 ]]; then 
        pgrep -f "${module} worker" |xargs kill -9
    else 
        printf "%s\n" "no workers running to stop"
    fi
    #pgrep -f "${module}" |xargs kill -9
}

function check_worker() {
    local module="$1"

    pgrep -a -f "${module} worker" 

}

if [[ "$ACTION" == "start" ]]; then 
    echo "starting ${MODULE_DOT_PATH}"
    start_worker "${MODULE_DOT_PATH}"
    #/usr/bin/python3.7 -m celery -A "${MODULE_DOT_PATH}" worker -l DEBUG -E -D
fi

if [[ "$ACTION" == "stop" ]]; then 
    echo "stopping ${MODULE_DOT_PATH}"
    stop_worker "${MODULE_DOT_PATH}"
    #pgrep -f "${MODULE_DOT_PATH}" |xargs kill -9
fi

if [[ "$ACTION" == "status" ]]; then 
    echo "checking ${MODULE_DOT_PATH}"
    check_worker "${MODULE_DOT_PATH}"
    #pgrep -a -f "${MODULE_DOT_PATH}"
fi

if [[ "$ACTION" == "restart" ]]; then 
    echo "restarting ${MODULE_DOT_PATH}"
    if [[ $(check_worker "${MODULE_DOT_PATH}"|wc -l) -gt 0 ]]; then 
        stop_worker "${MODULE_DOT_PATH}"
        sleep 0.5
        start_worker "${MODULE_DOT_PATH}"
    else
        echo "no running workers for ${MODULE_DOT_PATH}"
    fi
fi
