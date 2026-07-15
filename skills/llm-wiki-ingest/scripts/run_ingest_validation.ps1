[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$WikiRoot,

    [Parameter(Mandatory = $true)]
    [string]$NotesDir,

    [string[]]$RawPath = @(),

    [Parameter(Mandatory = $true)]
    [string[]]$FormalPath,

    [int]$MinBodyBytes = 500
)

$ErrorActionPreference = 'Stop'

function Test-PythonCandidate {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Executable,
        [string[]]$PrefixArgs = @()
    )

    try {
        $probe = & $Executable @PrefixArgs -c "import json, sys; print(json.dumps({'executable': sys.executable, 'version': list(sys.version_info[:3])}))" 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $probe) {
            return $null
        }
        $info = ($probe | Select-Object -Last 1) | ConvertFrom-Json
        if (-not $info.executable -or -not $info.version) {
            return $null
        }
        return [pscustomobject]@{
            Executable = $Executable
            PrefixArgs = @($PrefixArgs)
            SysExecutable = [string]$info.executable
            Version = (($info.version | ForEach-Object { [string]$_ }) -join '.')
        }
    }
    catch {
        return $null
    }
}

function Add-Candidate {
    param(
        [System.Collections.Generic.List[object]]$List,
        [System.Collections.Generic.HashSet[string]]$Seen,
        [string]$Executable,
        [string[]]$PrefixArgs = @()
    )
    if (-not $Executable) {
        return
    }
    $key = $Executable + "`0" + ($PrefixArgs -join "`0")
    if ($Seen.Add($key)) {
        [void]$List.Add([pscustomobject]@{ Executable = $Executable; PrefixArgs = @($PrefixArgs) })
    }
}

$candidates = [System.Collections.Generic.List[object]]::new()
$seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

foreach ($spec in @(
    @{ Name = 'python'; Prefix = @() },
    @{ Name = 'py'; Prefix = @('-3') },
    @{ Name = 'python3'; Prefix = @() }
)) {
    $commands = @(Get-Command $spec.Name -All -ErrorAction SilentlyContinue)
    foreach ($command in $commands) {
        $resolved = if ($command.Source) { $command.Source } else { $command.Name }
        Add-Candidate -List $candidates -Seen $seen -Executable $resolved -PrefixArgs $spec.Prefix
    }
}

$pyCommand = Get-Command py -ErrorAction SilentlyContinue
if ($pyCommand) {
    try {
        $registered = & $pyCommand.Source -0p 2>$null
        foreach ($line in @($registered)) {
            if ($line -match '([A-Za-z]:\\.*?python(?:\.exe)?)\s*$') {
                Add-Candidate -List $candidates -Seen $seen -Executable $Matches[1]
            }
        }
    }
    catch {
        # Continue with environment-derived discovery.
    }
}

foreach ($entry in @($env:PATH -split [IO.Path]::PathSeparator)) {
    if (-not $entry -or -not (Test-Path -LiteralPath $entry -PathType Container)) {
        continue
    }
    foreach ($file in @(Get-ChildItem -LiteralPath $entry -Filter 'python*.exe' -File -ErrorAction SilentlyContinue)) {
        Add-Candidate -List $candidates -Seen $seen -Executable $file.FullName
    }
}

$searchPatterns = @()
if ($env:LOCALAPPDATA) {
    $searchPatterns += (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python*\python.exe')
}
if ($env:ProgramFiles) {
    $searchPatterns += (Join-Path $env:ProgramFiles 'Python*\python.exe')
}
$programFilesX86 = [Environment]::GetEnvironmentVariable('ProgramFiles(x86)')
if ($programFilesX86) {
    $searchPatterns += (Join-Path $programFilesX86 'Python*\python.exe')
}
foreach ($pattern in $searchPatterns) {
    foreach ($file in @(Get-Item -Path $pattern -ErrorAction SilentlyContinue)) {
        Add-Candidate -List $candidates -Seen $seen -Executable $file.FullName
    }
}

$python = $null
foreach ($candidate in $candidates) {
    $python = Test-PythonCandidate -Executable $candidate.Executable -PrefixArgs $candidate.PrefixArgs
    if ($python) {
        break
    }
}

if (-not $python) {
    Write-Error 'No working Python interpreter was found on this computer. Command aliases that fail the runtime probe were rejected. Repair the Wiki tool environment before claiming ingest success.'
    exit 2
}

$validator = Join-Path $PSScriptRoot 'validate_ingest_contract.py'
if (-not (Test-Path -LiteralPath $validator -PathType Leaf)) {
    Write-Error "Bundled validator not found: $validator"
    exit 2
}

Write-Host "Validated Python: $($python.SysExecutable) ($($python.Version))"
$validatorArgs = @(
    $validator,
    '--wiki-root', $WikiRoot,
    '--notes-dir', $NotesDir,
    '--min-body-bytes', [string]$MinBodyBytes
)
foreach ($path in $RawPath) {
    $validatorArgs += @('--raw', $path)
}
foreach ($path in $FormalPath) {
    $validatorArgs += @('--formal', $path)
}

& $python.Executable @($python.PrefixArgs) @validatorArgs
exit $LASTEXITCODE
