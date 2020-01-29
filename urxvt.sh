#!/usr/bin/env bash

SIZE=14
ICON_PATH="${HOME}/GNUstep/Library/Icons"
ICON="tilda.png"
FONT_NAME="DejaVuSansMono Nerd Font Mono"
FONT_NORMAL="style=Book"
FONT_BOLD="style=Bold"
FONT_ITALIC="style=Oblique"
FONT_BOLDITALIC="style=Bold Oblique"
FIXED_NORMAL="-Misc-Fixed-Medium-R-Normal-*-15-*-*-*-C-*-ISO10646-1"
FIXED_ITALIC="-Misc-Fixed-Medium-O-Normal-*-15-*-*-*-C-*-ISO10646-1"
FIXED_BOLD="-Misc-Fixed-Bold-R-Normal-*-15-*-*-*-C-*-ISO10646-1"
XFT=true
EXEC=''
PERLEXT="url-select,keyboard-select,font-size,color-themes"



function usage {
    echo "Usage: $(basename "${0}") [options]"
    echo
    echo Options:
    echo
    echo "  -i icon          select icon file from ${ICON_PATH},"
    echo "                   default tilda.png"
    echo "  -t               activate tabbed extension"
    echo "  -s size          set font size, default 14"
    echo "  -f               use fixed misc font instead of DejaVu"
    echo "  -e               pass exec to the urxvt"
    echo "  -n               no perl extensions"
    echo "  -h               this help"
}

while getopts ":i:hfs:te:n" option
do
    case $option in
        h)
            usage
            exit 0
            ;;
        t)
            PERLEXT="tabbed,${PERLEXT}"
            ;;
        i)
            ICON=${OPTARG}
            ;;
        s)
            SIZE=${OPTARG}
            ;;
        f)
            XFT=false
            ;;
        e)
            EXEC="${OPTARG}"
            ;;
        n)
            PERLEXT=''
            ;;
        *)
            echo "Bad option"
            exit 1
            ;;
    esac
done

if ${XFT}
then
    if [ -n "${EXEC}" ]; then
        urxvt -pe "${PERLEXT}" \
            -fn "xft:${FONT_NAME}:${FONT_NORMAL}:pixelsize=${SIZE}" \
            -fb "xft:${FONT_NAME}:${FONT_BOLD}:pixelsize=${SIZE}" \
            -fbi "xft:${FONT_NAME}:${FONT_BOLDITALIC}:pixelsize=${SIZE}" \
            -fi "xft:${FONT_NAME}:${FONT_ITALIC}:pixelsize=${SIZE}" \
            -icon "${ICON_PATH}/${ICON}" -e ${EXEC}
    else
        urxvt -pe "${PERLEXT}" \
            -fn "xft:${FONT_NAME}:${FONT_NORMAL}:pixelsize=${SIZE}" \
            -fb "xft:${FONT_NAME}:${FONT_BOLD}:pixelsize=${SIZE}" \
            -fbi "xft:${FONT_NAME}:${FONT_BOLDITALIC}:pixelsize=${SIZE}" \
            -fi "xft:${FONT_NAME}:${FONT_ITALIC}:pixelsize=${SIZE}" \
            -icon "${ICON_PATH}/${ICON}"
    fi
else
    if [ -n "${EXEC}" ]; then
        urxvt -pe "${PERLEXT}" \
            -fn "${FIXED_NORMAL}" \
            -fb "${FIXED_BOLD}" \
            -fi "${FIXED_ITALIC}" \
            -icon "${ICON_PATH}/${ICON}" -e ${EXEC}
    else
        urxvt -pe "${PERLEXT}" \
            -fn "${FIXED_NORMAL}" \
            -fb "${FIXED_BOLD}" \
            -fi "${FIXED_ITALIC}" \
            -icon "${ICON_PATH}/${ICON}"
    fi
fi
