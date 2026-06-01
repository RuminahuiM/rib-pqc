#!/usr/bin/env bash
# setup-node22.sh
# ----------------------------------------------------------------------------
# Bootstrap-Script fuer das Implementing-PQC Projekt:
# Installiert nvm-windows + Node 22 LTS auf einer Windows-Maschine.
#
# WICHTIG: Vor diesem Script muss die alte Node-Installation (Node 18) MANUELL
# deinstalliert werden via:
#   Windows-Einstellungen > Apps > Installierte Apps > "Node.js" > Deinstallieren
#
# Reason: nvm-windows installer kann nicht ueber eine vorhandene Node-Installation
# drueber, weil die PATHs kollidieren.
#
# Verwendung in Git-Bash:
#   cd ~/Documents/Claude/Projects/Implementing\ PQC
#   bash infra/scripts/setup-node22.sh
# ----------------------------------------------------------------------------

set -euo pipefail

NVM_VERSION="1.1.12"
NVM_URL="https://github.com/coreybutler/nvm-windows/releases/download/${NVM_VERSION}/nvm-setup.exe"
NVM_INSTALLER="/tmp/nvm-setup.exe"
NODE_VERSION="22"

echo "=========================================================================="
echo "Implementing-PQC Node 22 Setup Script"
echo "=========================================================================="

# -----------------------------------------------------------------------------
# Pre-Check: Ist alte Node-Installation noch da?
# -----------------------------------------------------------------------------

if command -v node &>/dev/null; then
    CURRENT_NODE=$(node --version 2>&1)
    echo ""
    echo "WARNUNG: Es gibt noch eine bestehende Node-Installation: $CURRENT_NODE"
    echo ""
    echo "Falls das Node 22 (via nvm) ist, ist alles ok und du kannst hier abbrechen (Ctrl+C)."
    echo ""
    echo "Falls das die alte Node 18 Installation ist, MUSST du sie zuerst deinstallieren:"
    echo "  1. Windows-Taste druecken, 'Apps & Features' tippen, Enter."
    echo "  2. Nach 'Node.js' suchen, klicken, 'Deinstallieren' druecken."
    echo "  3. Im Installer durchklicken bis Deinstallation abgeschlossen."
    echo "  4. Dieses Script noch einmal aufrufen."
    echo ""
    read -p "Druecke ENTER wenn du jetzt die alte Node deinstallierst, oder Ctrl+C zum Abbruch: " _
    echo ""
    echo "Bitte deinstalliere jetzt Node und fuehre das Script danach erneut aus."
    exit 0
fi

# -----------------------------------------------------------------------------
# Step 1: nvm-windows Installer runterladen
# -----------------------------------------------------------------------------

echo ""
echo "=== Schritt 1: nvm-windows Installer herunterladen ==="
echo "URL: $NVM_URL"

if [ -f "$NVM_INSTALLER" ]; then
    echo "Installer existiert schon unter $NVM_INSTALLER, wird wiederverwendet."
else
    if command -v curl.exe &>/dev/null; then
        curl.exe -L -o "$NVM_INSTALLER" "$NVM_URL"
    elif command -v wget &>/dev/null; then
        wget -O "$NVM_INSTALLER" "$NVM_URL"
    else
        echo "FEHLER: weder curl.exe noch wget gefunden. Bitte manuell runterladen von:"
        echo "  $NVM_URL"
        echo "Und unter $NVM_INSTALLER ablegen, dann Script neu starten."
        exit 1
    fi
fi

if [ ! -f "$NVM_INSTALLER" ] || [ "$(stat -c%s "$NVM_INSTALLER")" -lt 1000 ]; then
    echo "FEHLER: Installer-Download nicht erfolgreich (Datei fehlt oder zu klein)."
    exit 1
fi

echo "OK: Installer unter $NVM_INSTALLER ($(stat -c%s "$NVM_INSTALLER") bytes)"

# -----------------------------------------------------------------------------
# Step 2: Installer ausfuehren (oeffnet GUI-Installer)
# -----------------------------------------------------------------------------

echo ""
echo "=== Schritt 2: nvm-windows Installer starten ==="
echo "Es oeffnet sich jetzt der Installer (GUI). Bitte:"
echo "  1. Lizenz akzeptieren."
echo "  2. nvm-Installations-Pfad bei Default belassen (C:\\Users\\WATASHII\\AppData\\Roaming\\nvm)."
echo "  3. Node-Symlink-Pfad bei Default belassen (C:\\Program Files\\nodejs)."
echo "  4. Installation abschliessen."
echo ""
read -p "Druecke ENTER um den Installer zu starten..." _

start "" "$NVM_INSTALLER" 2>/dev/null || cmd //c start "$NVM_INSTALLER"

echo ""
echo "Installer gestartet. Bitte abschliessen, dann hier weiter."
read -p "Druecke ENTER wenn der nvm-Installer durch ist..." _

# -----------------------------------------------------------------------------
# Step 3: Hinweis dass User neues Terminal oeffnen muss
# -----------------------------------------------------------------------------

echo ""
echo "=========================================================================="
echo "Schritt 3: WICHTIG - neues Git-Bash Terminal oeffnen!"
echo "=========================================================================="
echo ""
echo "Damit nvm in PATH ist, musst du jetzt:"
echo "  1. Dieses Git-Bash-Fenster SCHLIESSEN."
echo "  2. Ein NEUES Git-Bash-Fenster oeffnen."
echo "  3. Im neuen Fenster ausfuehren:"
echo ""
echo "       nvm --version"
echo "       nvm install ${NODE_VERSION}"
echo "       nvm use ${NODE_VERSION}"
echo "       node --version    # sollte v${NODE_VERSION}.x.x zeigen"
echo "       npm --version"
echo ""
echo "  4. Dann zurueck zum Implementation-Chat und melden dass node 22 aktiv ist."
echo "     Wir machen dann weiter mit create-expo-app fuer PQC-20."
echo ""
echo "=========================================================================="
