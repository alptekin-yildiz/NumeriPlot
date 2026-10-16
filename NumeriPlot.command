#!/bin/bash
# Finder launcher for an already installed source checkout.
set -u
cd -- "$(dirname -- "$0")" || exit 1

pause_on_error() {
    if [ -t 0 ]; then
        read -r -p "Kapatmak için Enter / Press Enter to close: " reply
    fi
}

if [ ! -x venv/bin/python ] || [ ! -f main.py ]; then
    echo "İlk kurulum gerekli. / First-time setup is required."
    echo "Kılavuz / Guide: docs/SOURCE_INSTALL_TR.md (English: docs/SOURCE_INSTALL.md)"
    echo "https://github.com/alptekin-yildiz/NumeriPlot/blob/main/docs/SOURCE_INSTALL_TR.md"
    echo "https://github.com/alptekin-yildiz/NumeriPlot/blob/main/docs/SOURCE_INSTALL.md"
    pause_on_error
    exit 1
fi

echo "NumeriPlot açılıyor. Bu pencere açık kalsın. / Starting NumeriPlot. Keep this window open."
./venv/bin/python main.py
result=$?
if [ "$result" -ne 0 ]; then
    echo "Açılış başarısız. Kılavuzun sorun giderme bölümüne bakın."
    echo "Launch failed. See the troubleshooting section in the installation guide."
    echo "docs/SOURCE_INSTALL_TR.md / docs/SOURCE_INSTALL.md"
    pause_on_error
fi
exit "$result"
