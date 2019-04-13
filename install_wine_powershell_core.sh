#!/bin/bash
function include_dependencies {
    local my_dir="$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )"  # this gives the full path, even for sourced scripts
    chmod +x "${my_dir}/lib_bash/*.sh"
    source "${my_dir}/lib_bash/lib_color.sh"
    source "${my_dir}/lib_bash/lib_retry.sh"
    source "${my_dir}/lib_bash/lib_wine_install.sh"
}

include_dependencies  # me need to do that via a function to have local scope of my_dir

## set wine prefix to ${HOME}/.wine if not given by environment variable
if [[ -z ${WINEPREFIX} ]]
    then
        echo "WARNING - no WINEPREFIX in environment - set now to ${HOME}/.wine"
        WINEPREFIX=${HOME}/.wine
    fi

wine_drive_c_dir=${WINEPREFIX}/drive_c
powershell_install_dir=${wine_drive_c_dir}/windows/system32/powershell
mkdir -p ${powershell_install_dir}

cd ${powershell_install_dir}

if [[ "${WINEARCH}" == "win32" ]]
    then
        echo "Download Powershell 32 Bit"
        wget --no-check-certificate -O powershell.zip https://github.com/PowerShell/PowerShell/releases/download/v6.2.0/PowerShell-6.2.0-win-x86.zip
    else
        echo "Download Powershell 64 Bit"
        wget --no-check-certificate -O powershell.zip https://github.com/PowerShell/PowerShell/releases/download/v6.2.0/PowerShell-6.2.0-win-x64.zip
    fi

unzip -qq ./powershell.zip -d ${powershell_install_dir}
rm ./powershell.zip
wine ${powershell_install_dir}/pwsh -ExecutionPolicy unrestricted -Command "get-executionpolicy"

