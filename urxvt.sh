#!/usr/bin/env bash

# urxvt.sh - simplify urxvt commandline execution.

SIZE=14
FIXED_SIZE=16
ICON_PATH="${HOME}/GNUstep/Library/Icons"
ICON="tilda.png"
FONT_BOOK="style=Book"
FONT_REGULAR="style=Regular"
FONT_MEDIUM="style=Medium"
FONT_BOLD="style=Bold"

# FIXED_NORMAL="-Misc-Fixed-Medium-R-Normal-*-15-*-*-*-C-*-ISO10646-1"
# FIXED_ITALIC="-Misc-Fixed-Medium-O-Normal-*-15-*-*-*-C-*-ISO10646-1"
# FIXED_BOLD="-Misc-Fixed-Bold-R-Normal-*-15-*-*-*-C-*-ISO10646-1"

# Regular fonts.
DEJAVU="xft:DejaVuSansMono Nerd Font Mono:_FONT_STYLE_:pixelsize=_SIZE_"
FIXED="xft:Misc Fixed:_FONT_STYLE_:pixelsize=_FIXEDSIZE_:antialias=false"
# Fonts, that provides with symbols, icons, emoji (besides those in Nerd Font)
SYMBOLA="xft:Symbola:_FONT_STYLE_:pixelsize=_SIZE_"
UNIFONT="xft:Unifont Upper:_FONT_STYLE_:pixelsize=_SIZE_"
DEJAVUSANS="xft:DejaVu Sans:style=_FONT_STYLE_:pixelsize=_SIZE_"

XFT=true
EXEC=''
PERLEXT="url-select,keyboard-select,font-size,color-themes"

# TODO: do we need italic/bolditalic?

function rxvt {
    urxvtc "$@"
    if [ $? -eq 2 ]; then
        urxvtd -q -o -f
        urxvtc "$@"
    fi
}

function join_by {
    local IFS="$1"; shift; echo "$*";
}

function usage {
    echo "Usage: $(basename "${0}") [options]"
    echo
    echo Options:
    echo
    echo "  -i icon          select icon file from ${ICON_PATH},"
    echo "                   default tilda.png"
    echo "  -t               activate tabbedalt extension"
    echo "  -s size          set font size, default 14"
    echo "  -f               use fixed misc font as a main font instead of"
    echo "                   DejaVu"
    echo "  -e               pass exec to the urxvt"
    echo "  -n               no perl extensions"
    echo "  -h               this help"
}

while getopts ":i:hfs:te:n" option; do
    case $option in
        h)
            usage
            exit 0
            ;;
        t)
            PERLEXT="tabbedalt,${PERLEXT}"
            ;;
        i)
            ICON=${OPTARG}
            ;;
        s)
            SIZE=${OPTARG}
            FIXED_SIZE=${OPTARG}
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

if ${XFT}; then
    FONTS="${DEJAVU/_FONT_STYLE_/style=Book}"
    FONTS="${FONTS/_SIZE_/$SIZE}"
    FONTS="${FONTS},${SYMBOLA/_FONT_STYLE_/style=Regular}"
    FONTS="${FONTS/_SIZE_/$SIZE}"
    FONTS="${FONTS},${UNIFONT/_FONT_STYLE_/style=Medium}"
    FONTS="${FONTS/_SIZE_/$SIZE},${FIXED/_FONT_STYLE_/style=Regular}"
    FONTS="${FONTS},${DEJAVUSANS/_FONT_STYLE_/style=Book}"
    FONTS="${FONTS/_SIZE_/$SIZE}"

    FONTSB="${DEJAVU/_FONT_STYLE_/style=Bold}"
    FONTSB="${FONTSB/_SIZE_/$SIZE}"
    FONTSB="${FONTSB},${SYMBOLA/_FONT_STYLE_/style=Bold}"
    FONTSB="${FONTSB/_SIZE_/$SIZE}"
    FONTSB="${FONTSB},${UNIFONT/_FONT_STYLE_/style=Bold}"
    FONTSB="${FONTSB/_SIZE_/$SIZE},${FIXED/_FONT_STYLE_/style=Bold}"
    FONTSB="${FONTSB},${DEJAVUSANS/_FONT_STYLE_/style=Bold}"
    FONTSB="${FONTSB/_SIZE_/$SIZE}"
else
    FONTS="${FIXED/_FONT_STYLE_/style=Regular}"
    FONTS="${FONTS/_FIXEDSIZE_/$FIXED_SIZE}"
    FONTS="${FONTS},${DEJAVU/_FONT_STYLE_/style=Book}"
    FONTS="${FONTS/_SIZE_/$SIZE}"
    FONTS="${FONTS},${SYMBOLA/_FONT_STYLE_/style=Regular}"
    FONTS="${FONTS/_SIZE_/$SIZE}"
    FONTS="${FONTS},${UNIFONT/_FONT_STYLE_/style=Medium}"
    FONTS="${FONTS/_SIZE_/$SIZE}"
    FONTS="${FONTS},${DEJAVUSANS/_FONT_STYLE_/style=Book}"
    FONTS="${FONTS/_SIZE_/$SIZE}"

    FONTSB="${FIXED/_FONT_STYLE_/style=Bold}"
    FONTSB="${FONTSB/_FIXEDSIZE_/$FIXED_SIZE}"
    FONTSB="${FONTSB},${DEJAVU/_FONT_STYLE_/style=Bold}"
    FONTSB="${FONTSB/_SIZE_/$SIZE}"
    FONTSB="${FONTSB},${SYMBOLA/_FONT_STYLE_/style=Bold}"
    FONTSB="${FONTSB/_SIZE_/$SIZE}"
    FONTSB="${FONTSB},${UNIFONT/_FONT_STYLE_/style=Bold}"
    FONTSB="${FONTSB/_SIZE_/$SIZE}"
    FONTSB="${FONTSB},${DEJAVUSANS/_FONT_STYLE_/style=Bold}"
    FONTSB="${FONTSB/_SIZE_/$SIZE}"
fi

args=("-pe" "${PERLEXT}" "-icon" "${ICON_PATH}/${ICON}")
args+=("-fn" "${FONTS}" "-fb" "${FONTSB}" )

if [ -n "${EXEC}" ]; then
    args+=("-e" "${EXEC}")
fi

rxvt "${args[@]}"
