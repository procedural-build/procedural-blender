@echo off
set "defaultaddonpath=C:\Program Files\Blender Foundation\Blender 3.2\3.2\scripts\addons"
set /p useraddonpath="Enter path to addon folder [%defaultaddonpath%]:"

set addonpath=%defaultaddonpath%
if NOT [%useraddonpath%] == [] (
    set addonpath=%useraddonpath%
)

set "linkfolder=%addonpath%\procedural_compute"

echo Linking procedurl_compute folder to %linkfolder% for development

if exist %linkfolder% (
    echo Removing existing folder %linkfolder%
    rmdir "%linkfolder%"
)

mklink /D "%linkfolder%" %cd%\procedural_compute