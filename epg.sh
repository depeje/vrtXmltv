#!/usr/bin/sh

# This script downloads the EPG data from vrt NU and imports it into MythTV
# Note: this scrip will create a temporary XMLTV xml file in the current working directory

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if $DIR/vrtXmltv.py > vrt_epg.xml; then
    echo "Downloaded successfully. Updating MythTV"
    /usr/bin/mythfilldatabase --only-update-guide --sourceid 1 --file --xmlfile vrt_epg.xml
else
    echo "Error downloading vrt data. Not updating MythTV"
fi