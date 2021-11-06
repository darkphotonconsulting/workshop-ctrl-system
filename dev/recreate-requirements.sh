#!/usr/bin/env bash 

# dont error when escaping an '=' to create a literal '='
# shellcheck disable=SC1001


REQUIREMENTS_IN="${1:-requirements.txt}"
REQUIREMENTS_OUT="${2:-requirements.txt}"
OVERWRITE=0
printf "present working dir: %s\n" "$(pwd)"
printf "scanning input: %s\n" "$REQUIREMENTS_IN"

printf "writing output: %s\n" "$REQUIREMENTS_OUT"
#printf "using output: %s\n" "$REQUIREMENTS_OUT"

if [ "${REQUIREMENTS_IN}" == "${REQUIREMENTS_OUT}" ]; then 
    #printf "requesting a file overwrite...\n"
    OVERWRITE=1
    REQUIREMENTS_OUT=$(mktemp)
    #printf "updated requirements file to be: %s\n" "${REQUIREMENTS_OUT}"    
    cat < "${REQUIREMENTS_IN}" | while IFS= read  -r line; do
        if [[ "$line" == \#* ]]; then 
            #printf "skipping commented line: %s\n" "$line"
            continue;
        fi

        if [[ "$line" == *\=\=* ]]; then 
            #printf "already pinned: %s\n" "$line"
            continue
        fi
        installed_pkg="$line"
        installed_version="$(
            pip3 show "$installed_pkg"|grep -E '^Version' | cut -d ':' -f2 |xargs
        )"
        #printf "adding entry -> [pkg: %s] [version: %s]<- \n" "${installed_pkg}" "${installed_version}"
        printf "%s==%s\n" "${installed_pkg}" "${installed_version}" |tee -a "$REQUIREMENTS_OUT"

        #echo "data file line: $pkg"
    done 
fi



if [ $OVERWRITE -eq 1 ]; then 
    cat < "${REQUIREMENTS_OUT}" | tee  "${REQUIREMENTS_IN}"
fi

