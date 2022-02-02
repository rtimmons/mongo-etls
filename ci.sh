#!/usr/bin/env bash

set -eou pipefail


_pip() {
    # see TIG-2862
    CRYPTOGRAPHY_DONT_BUILD_RUST=1 /usr/bin/env python3 -m pip "$@" --isolated -q -q
}

_etls_venv="etls_venv"

pushd "$(dirname "$0")" >/dev/null
    ETLS_REPO_ROOT="$(pwd -P)"
popd >/dev/null


if [[ $# -lt 1 ]]; then
    echo -e "Usage: \\n\\t$0 setup\\n\\t$0 command" >/dev/stderr
    exit 5
fi

if [ -d "/opt/mongodbtoolchain/v3/bin" ]; then
    export PATH="/opt/mongodbtoolchain/v3/bin:$PATH"
fi

_HAVE_PRINTED_DIAGNOSTICS=
_print_diagnostics() {
    if [ -n "$_HAVE_PRINTED_DIAGNOSTICS" ]; then
        return
    fi
    echo >&2 "If you're stuck, please ask for help and include the following output:"
    echo >&2 ""
    echo >&2 "  git rev-parse HEAD: $(git rev-parse HEAD)"
    echo >&2 "  uname -a:           $(uname -a)"
    echo >&2 "  whoami:             $(whoami)"
    echo >&2 "  command -v python3: $(command -v python3)"
    echo >&2 "  pwd:                $(pwd)"
    echo >&2 "  PATH:               $PATH"
    echo >&2 ""
    _HAVE_PRINTED_DIAGNOSTICS=1
}


if ! python3 -c 'import sys; sys.exit(1 if sys.version_info < (3, 7) else 0)' >/dev/null 2>&1; then
    actual_version=$(python3 -c 'import sys; print(sys.version)')
    echo >&2 "You must have python3.7+ installed."
    echo >&2 "Detected version $actual_version."
    echo >&2 ""
    echo >&2 "On macOS you can run:"
    echo >&2 ""
    echo >&2 "    brew install python3"
    echo >&2 ""
    _print_diagnostics
    exit 1
fi

if [ -n "${VIRTUAL_ENV:-}" ] && [ "${VIRTUAL_ENV}" != "${ETLS_REPO_ROOT}/etls_venv" ]; then
    echo >&2 "You are already inside a virtual environment $VIRTUAL_ENV."
    echo >&2 "This can be problematic. Will try to proceed, but setup may fail."
    echo >&2 "If it does, please deactivate your existing virtualenv first:"
    echo >&2 ""
    echo >&2 "    deactivate"
    echo >&2 ""
    _print_diagnostics
    echo >&2 ""
fi

if which pyenv >/dev/null 2>&1; then
    if pyenv version | grep system >/dev/null 2>&1; then
        echo >&2 "You have system python setup through pyenv."
        echo >&2 "pyenv version: $(pyenv version)"
        echo >&2 ""
        echo >&2 "This can be problematic. Will try to proceed, but setup may fail."
        echo >&2 "If it does, please change your python version by doing something like this:"
        echo >&2 ""
        echo >&2 "    echo '3.7.0' > ~/.python-version"
        echo >&2 "    pyenv install"
        echo >&2 ""
        _print_diagnostics
    fi
fi

if ! python3 -c 'import sys; sys.exit(1 if "Python3.framework" in sys.prefix else 0)' >/dev/null 2>&1; then
    actual_prefix=$(python3 -c 'import sys; print(sys.prefix)')
    echo >&2 "The python built into macOS Catalania is known to be problematic."
    echo >&2 "It complains with 'architecture not supported' during setup."
    echo >&2 "Detected system prefix: $actual_prefix"
    echo >&2 ""
    echo >&2 "On macOS you can run:"
    echo >&2 ""
    echo >&2 "    brew install python3"
    echo >&2 ""
    _print_diagnostics
    exit 1
fi

if ! _pip --version >/dev/null 2>&1; then
    echo >&2 "Your installation of python does not contain pip."
    echo >&2 "On macOS you can run:"
    echo >&2 ""
    echo >&2 "    brew install python3"
    echo >&2 ""
    echo >&2 "If this error persists, check that your PATH points to the correct python location."
    _print_diagnostics
    exit 1
fi


# Check for etls-setup-done-v4 which we create at the end of setup.
# This prevents half-setup environments.
if [[ ! -d "${ETLS_REPO_ROOT}/${_etls_venv}" || ! -e "${ETLS_REPO_ROOT}/${_etls_venv}/etls-setup-done-v4" ]]; then
    rm -rf "${ETLS_REPO_ROOT:?}/${_etls_venv}"

    python3 -m venv "${ETLS_REPO_ROOT}/${_etls_venv}"

    export VIRTUAL_ENV_DISABLE_PROMPT=1  # prevent undefined $PS1 variable
    # shellcheck source=/dev/null
    source "${ETLS_REPO_ROOT}/${_etls_venv}/bin/activate"

    # Upgrade pip itself
    _pip install --upgrade pip setuptools wheel

    # Install etls requirements
    _pip install -r "${ETLS_REPO_ROOT}/requirements-dev.txt"
    _pip install -r "${ETLS_REPO_ROOT}/requirements-external.txt"
    _pip install -r "${ETLS_REPO_ROOT}/requirements-mars.txt"

    # _pip freeze > "pip-requirements.txt" 2>/dev/null

    # Record that we've done setup at the current git sha.
    # (Don't use the sha for now but might in the future to determine
    # if we need to run pip install again or something.)
    pushd "${ETLS_REPO_ROOT}" >/dev/null
        git rev-parse HEAD > "${ETLS_REPO_ROOT}/${_etls_venv}/etls-setup-done-v4"
    popd >/dev/null
fi

declare -a COMMAND
COMMAND=("$@")


if [[ "${COMMAND[0]}" == "setup" ]]; then
    echo "Setup successfully into ${ETLS_REPO_ROOT}/${_etls_venv}."
    exit 0
fi


export VIRTUAL_ENV_DISABLE_PROMPT=1  # prevent undefined $PS1 variable
# shellcheck source=/dev/null
source "${ETLS_REPO_ROOT}/${_etls_venv}/bin/activate"


# Else we ./run-etls X invoked with X being a file.

PYTHONPATH="${ETLS_REPO_ROOT}/src:${PYTHONPATH:-}" /usr/bin/env "${COMMAND[@]}"

