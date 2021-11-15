#!/usr/bin/env bash 
#ACTION="${1:-start}"
#MODULE_DOT_PATH="${2:-pylibs.sidecars.metrics.app}.celery"
#RUN_PATH='./run'
# WORKER_LOG="${RUN_PATH}/${MODULE_DOT_PATH}-worker.log"
# WORKER_PID="${RUN_PATH}/${MODULE_DOT_PATH}-worker.pid"

# . "scripts/colors.sh"

# echo -e "${Green} what? ${Color_Off}"
# defaults
ACTION="status"
MODULE_DOT_PATH="pylibs.sidecars.metrics.app.celery"
RUN_PATH="./run"
DEBUG=0
#LOGLEVEL="INFO"

function usage() {
    printf "usage: %s -r %s -m %s -a %s\n" "$0" "<runPath>" "<modulePath>" "<action>"
}

function info() {
    local run_path="${1}"
    local module_dot_path="${2}"
    local action="${3}"
    local logfile="${4}"
    local pidfile="${5}"
    message=(
        "run_path: ${run_path}"
        "module_dot_path: ${module_dot_path}"
        "action: ${action}"
        "logfile: ${logfile}"
        "pidfile: ${pidfile}"
    )
    printf "%s\n" "${message[@]}"
}


function start_worker() {
    local module="$1"
    local logfile="$2"    
    local pidfile="$3"
    /usr/bin/python3.7 -m celery -A "${module}" worker -l DEBUG  -E -D --logfile "${logfile}" --pidfile "${pidfile}"
}

function stop_worker() {
    local module="$1"
    if [[ $(check_worker "$module" |wc -l)  -gt 0 ]]; then 
        pgrep -f "${module} worker" |xargs kill -9
    fi
}

function check_worker() {
    local module="$1"
    #running_workers="$(pgrep -a -f "${module} worker" | wc -l)"
    #printf "running processes: %s" "${running_workers}"
    pgrep -a -f "${module} worker" 
}

function main() {
    local run_path="${1}"
    local module_dot_path="${2}"
    local action="${3}"
    local logfile="${4}"
    local pidfile="${5}"
    if [[ "$action" == "start" ]]; then 
        echo "starting ${module_dot_path}"
        start_worker "${module_dot_path}"
        #/usr/bin/python3.7 -m celery -A "${MODULE_DOT_PATH}" worker -l DEBUG -E -D
    fi

    if [[ "$action" == "stop" ]]; then 
        echo "stopping ${module_dot_path}"
        stop_worker "${module_dot_path}"
        #pgrep -f "${MODULE_DOT_PATH}" |xargs kill -9
    fi

    if [[ "$action" == "status" ]]; then 
        echo "checking ${module_dot_path}"
        check_worker "${module_dot_path}"
        #pgrep -a -f "${MODULE_DOT_PATH}"
    fi

    if [[ "$action" == "restart" ]]; then 
        echo "restarting ${module_dot_path}"
        if [[ $(check_worker "${module_dot_path}"|wc -l) -gt 0 ]]; then 
            stop_worker "${module_dot_path}"
            sleep 0.5
            start_worker "${module_dot_path}"
        else
            echo "no running workers for ${module_dot_path}"
        fi
    fi
}


#[ $# -eq 0 ] && usage
while getopts ":hdr:m:a:" arg;  do 
    case "$arg" in 
        r)
        RUN_PATH="${OPTARG}"
        ;;
        m)
        MODULE_DOT_PATH="${OPTARG}"
        if [[ ! "$MODULE_DOT_PATH" == *celery ]]; then 
            MODULE_DOT_PATH="${MODULE_DOT_PATH}.celery"
        fi
        ;;
        a)
        ACTION="${OPTARG}"
        ;;
        d)
        DEBUG=1
        #LOGLEVEL="DEBUG"
        ;;
        h|*)
        usage
        ;;
    esac
done

WORKER_LOG="${RUN_PATH}/${MODULE_DOT_PATH}-worker.log"
WORKER_PID="${RUN_PATH}/${MODULE_DOT_PATH}-worker.pid"



if [[ $DEBUG -gt 0 ]]; then 
    info "${RUN_PATH}" "${MODULE_DOT_PATH}" "${ACTION}" "${WORKER_LOG}" "${WORKER_PID}"
fi

main "${RUN_PATH}" "${MODULE_DOT_PATH}" "${ACTION}" "${WORKER_LOG}" "${WORKER_PID}"

# printf "run_path: '%s'\n" "${RUN_PATH}"
# printf "module_dot_path: '%s'\n" "${MODULE_DOT_PATH}"
# printf "action: '%s'\n" "${ACTION}"
# printf "log: '%s' pid: '%s'\n" "${WORKER_LOG}" "${WORKER_PID}"