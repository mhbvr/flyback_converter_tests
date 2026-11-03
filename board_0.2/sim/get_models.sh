#!/bin/bash
# Downloads the vendor SPICE models used by the simulations and makes them ngspice-ready.
#  - TI NexFET PSpice models: CSD18533KCS (on board 0.2), CSD18534KCS, CSD18543Q3A (candidates)
#    patched by patch_ti.py (inline subckt .PARAMs, unique helper-subckt names)
#  - Vishay BYG20J diode model (Thomatronik SPICE3 .model, used as-is)
# Vendor model files are not committed (vendor copyright); run this script instead.
set -e
cd "$(dirname "$0")"
tmp=$(mktemp -d)
for pair in SLPM047:CSD18533KCS SLPM046:CSD18534KCS SLPM286:CSD18543Q3A; do
  zip=${pair%%:*}; part=${pair#*:}
  curl -sSL "https://www.ti.com/lit/zip/$zip" -o "$tmp/$zip.zip"
  unzip -o -q "$tmp/$zip.zip" -d "$tmp/$zip"
  src=$(find "$tmp/$zip" -iname "$part.lib" | head -1)
  python3 patch_ti.py "$src" "$part.lib"
done
curl -sSL https://www.vishay.com/docs/89876/byg20j.txt -o byg20j.lib
rm -rf "$tmp"
echo "models ready"
