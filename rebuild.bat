@echo off
echo Starting rebuild at %TIME% > rebuild_full.log
python apps/api/rebuild.py ac2e93f6-b5d0-47b6-840b-6e0571518ac2 >> rebuild_full.log 2>&1
echo Finished rebuild at %TIME% >> rebuild_full.log
