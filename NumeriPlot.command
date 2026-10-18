#!/bin/bash
# Finder launcher for an already installed source checkout.
set -u
cd -- "$(dirname -- "$0")" || exit 1

pause_on_error() {
    if [ -t 0 ]; then
        read -r -p "Kapatmak için Enter / Press Enter to close: " reply
    fi
}

if [ ! -f main.py ]; then
    echo "Başlatıcı NumeriPlot klasöründe kalmalı; masaüstü için Finder takma adı kullanın."
    echo "Keep this launcher in the NumeriPlot folder; use a Finder alias on the desktop."
    pause_on_error
    exit 1
fi

if [ ! -x venv/bin/python ]; then
    echo "İlk kurulum gerekli. / First-time setup is required."
    echo "Kılavuz / Guide: docs/SOURCE_INSTALL_TR.md (English: docs/SOURCE_INSTALL.md)"
    echo "https://github.com/alptekin-yildiz/NumeriPlot/blob/v0.2.0/docs/SOURCE_INSTALL_TR.md"
    echo "https://github.com/alptekin-yildiz/NumeriPlot/blob/v0.2.0/docs/SOURCE_INSTALL.md"
    pause_on_error
    exit 1
fi

echo "NumeriPlot açılıyor. Bu pencere açık kalsın. / Starting NumeriPlot. Keep this window open."
NUMERIPLOT_LAUNCHER=1 ./venv/bin/python main.py
result=$?
if [ "$result" -ne 0 ]; then
    echo "Açılış başarısız. bash setup.sh komutunu yeniden çalıştırın; kılavuz bölüm 6’ya bakın."
    echo "Launch failed. Run bash setup.sh again; see section 6 (Troubleshooting) in the installation guide."
    echo "docs/SOURCE_INSTALL_TR.md / docs/SOURCE_INSTALL.md"
    pause_on_error
fi
exit "$result"
