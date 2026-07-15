@echo off
setlocal EnableExtensions DisableDelayedExpansion

set "VALIDATOR=%~dp0validate_ingest_contract.py"
if not exist "%VALIDATOR%" (
  echo ERROR: bundled validator not found: %VALIDATOR% 1>&2
  exit /b 2
)

set "PYTHON_EXE="
set "PYTHON_PREFIX="
set "PYTHON_SYS="
set "PYTHON_VERSION="

call :probe "python" ""
if defined PYTHON_EXE goto :run
call :probe "py" "-3"
if defined PYTHON_EXE goto :run
call :probe "python3" ""
if defined PYTHON_EXE goto :run

for /f "delims=" %%P in ('where python 2^>nul') do (
  call :probe "%%P" ""
  if defined PYTHON_EXE goto :run
)
for /f "delims=" %%P in ('where python3 2^>nul') do (
  call :probe "%%P" ""
  if defined PYTHON_EXE goto :run
)

if defined LOCALAPPDATA (
  for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%~fD\python.exe" call :probe "%%~fD\python.exe" ""
    if defined PYTHON_EXE goto :run
  )
)
if defined ProgramFiles (
  for /d %%D in ("%ProgramFiles%\Python*") do (
    if exist "%%~fD\python.exe" call :probe "%%~fD\python.exe" ""
    if defined PYTHON_EXE goto :run
  )
)
echo ERROR: no working Python interpreter was found on this computer. Repair the Wiki tool environment before claiming ingest success. 1>&2
exit /b 2

:probe
set "CANDIDATE=%~1"
set "PREFIX=%~2"
set "PROBE_FILE=%TEMP%\llmwiki-python-probe-%RANDOM%-%RANDOM%.txt"
set "PROBE_LINE="
set "PROBE_SYS="
set "PROBE_VERSION="
"%CANDIDATE%" %PREFIX% -c "import sys; print(sys.executable + ';' + '.'.join(map(str, sys.version_info[:3])))" >"%PROBE_FILE%" 2>nul
if errorlevel 1 (
  del /q "%PROBE_FILE%" >nul 2>&1
  exit /b 1
)
set /p "PROBE_LINE="<"%PROBE_FILE%"
del /q "%PROBE_FILE%" >nul 2>&1
if not defined PROBE_LINE exit /b 1
for /f "tokens=1,* delims=;" %%A in ("%PROBE_LINE%") do (
  set "PROBE_SYS=%%A"
  set "PROBE_VERSION=%%B"
)
if not defined PROBE_SYS exit /b 1
if not defined PROBE_VERSION exit /b 1
set "PYTHON_EXE=%CANDIDATE%"
set "PYTHON_PREFIX=%PREFIX%"
set "PYTHON_SYS=%PROBE_SYS%"
set "PYTHON_VERSION=%PROBE_VERSION%"
exit /b 0

:run
echo Validated Python: %PYTHON_SYS% (%PYTHON_VERSION%)
"%PYTHON_EXE%" %PYTHON_PREFIX% "%VALIDATOR%" %*
exit /b %ERRORLEVEL%
