@echo off
setlocal enabledelayedexpansion

set "VSDEVCMD=%TAURI_VSDEVCMD%"
if "%VSDEVCMD%"=="" set "VSDEVCMD=C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\Common7\Tools\VsDevCmd.bat"

if not exist "%VSDEVCMD%" (
  echo VsDevCmd.bat not found at "%VSDEVCMD%".
  echo Set the TAURI_VSDEVCMD environment variable to the correct path.
  exit /b 1
)

call "%VSDEVCMD%" -arch=x64 || exit /b %errorlevel%

set "WINSDK_ROOT=%TAURI_WINSDK_ROOT%"
if "%WINSDK_ROOT%"=="" set "WINSDK_ROOT=C:\Program Files (x86)\Windows Kits\10"

set "WINSDK_VERSION=%TAURI_WINSDK_VERSION%"
if "%WINSDK_VERSION%"=="" set "WINSDK_VERSION=10.0.26100.0"

set "INCLUDE=%INCLUDE%;%WINSDK_ROOT%\Include\%WINSDK_VERSION%\ucrt;%WINSDK_ROOT%\Include\%WINSDK_VERSION%\shared;%WINSDK_ROOT%\Include\%WINSDK_VERSION%\um;%WINSDK_ROOT%\Include\%WINSDK_VERSION%\winrt;%WINSDK_ROOT%\Include\%WINSDK_VERSION%\cppwinrt"
set "LIB=%LIB%;%WINSDK_ROOT%\Lib\%WINSDK_VERSION%\ucrt\x64;%WINSDK_ROOT%\Lib\%WINSDK_VERSION%\um\x64"

node scripts\sync-assets.cjs || exit /b %errorlevel%

npx tauri %*
