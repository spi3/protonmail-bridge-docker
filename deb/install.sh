#!/bin/bash
set -ex

version="${1:?version argument required}"

# Repack deb (remove unnecessary dependencies)
mkdir deb
package_url="$(
    wget -qO- "https://api.github.com/repos/ProtonMail/proton-bridge/releases/tags/${version}" \
        | jq -r '.assets[] | select(.name | endswith("_amd64.deb")) | .browser_download_url' \
        | head -n 1
)"

if [[ -z "${package_url}" || "${package_url}" == "null" ]]; then
    echo "No amd64 Debian package found for Proton Bridge ${version}" >&2
    exit 1
fi

wget "${package_url}" -O /deb/protonmail.deb
cd deb
ar x -v protonmail.deb
mkdir control
tar zxvf control.tar.gz -C control
sed -i "s/^Depends: .*$/Depends: libgl1, libc6, libsecret-1-0, libfido2-1, libstdc++6, libgcc1/" control/control
cd control
tar zcvf ../control.tar.gz .
cd ../

ar rcs -v /protonmail.deb debian-binary control.tar.gz data.tar.gz
