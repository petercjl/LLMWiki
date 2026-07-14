[CmdletBinding()]
param(
    [switch]$Install,
    [switch]$KeepInstaller,
    [string]$DownloadDirectory = (Join-Path $env:TEMP "llm-wiki-bootstrap")
)

$ErrorActionPreference = "Stop"

function Write-ResultAndExit {
    param(
        [System.Collections.IDictionary]$Result,
        [int]$ExitCode
    )
    $Result | ConvertTo-Json -Depth 6
    exit $ExitCode
}

$result = [ordered]@{
    platform = "windows"
    source = "https://obsidian.bijitongbu.site/"
    resolver = "https://obsidian-dl.notebooksyncer.com/sign?os=win"
    downloaded = $false
    signature_valid = $false
    installed = $false
    installer_path = ""
    sha256 = ""
    signer = ""
    version = ""
    error = ""
}
$lockStream = $null
$lockPath = ""

try {
    if (-not $IsWindows -and $env:OS -ne "Windows_NT") {
        throw "This helper can run only on Windows."
    }
    $curl = (Get-Command curl.exe -CommandType Application -ErrorAction Stop).Source
    New-Item -ItemType Directory -Path $DownloadDirectory -Force | Out-Null
    $lockPath = Join-Path $DownloadDirectory ".obsidian-download.lock"
    try {
        $lockStream = [System.IO.File]::Open(
            $lockPath,
            [System.IO.FileMode]::OpenOrCreate,
            [System.IO.FileAccess]::ReadWrite,
            [System.IO.FileShare]::None
        )
    }
    catch {
        throw "Another Obsidian download or installation task is already active for this Skill. Wait for it to finish instead of starting a second downloader."
    }

    $headers = @(
        "-H", "Origin: https://obsidian.bijitongbu.site",
        "-H", "Referer: https://obsidian.bijitongbu.site/"
    )
    $resolverText = & $curl --fail --silent --show-error @headers $result.resolver
    if ($LASTEXITCODE -ne 0) {
        throw "The Obsidian mirror resolver failed with exit code $LASTEXITCODE."
    }
    $resolved = $resolverText | ConvertFrom-Json
    if (-not $resolved.url) {
        throw "The Obsidian mirror resolver did not return a download URL."
    }
    $uri = [System.Uri]$resolved.url
    if ($uri.Scheme -ne "https" -or $uri.Host -ne "obsidian-dl.notebooksyncer.com" -or -not $uri.AbsolutePath.EndsWith(".exe")) {
        throw "The resolved artifact is not the expected HTTPS Windows installer."
    }

    $name = [System.IO.Path]::GetFileName($uri.AbsolutePath)
    $installer = Join-Path $DownloadDirectory $name
    $partial = "$installer.partial"
    Remove-Item -LiteralPath $partial -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $installer -Force -ErrorAction SilentlyContinue

    # This synchronous call is the only download process. Do not wrap it in a
    # background job or start another downloader while it is running.
    & $curl --fail --location --show-error --output $partial $resolved.url
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $partial)) {
        throw "The Obsidian installer download failed with exit code $LASTEXITCODE."
    }
    Move-Item -LiteralPath $partial -Destination $installer -Force
    $result.downloaded = $true
    $result.installer_path = $installer

    $signature = Get-AuthenticodeSignature -FilePath $installer
    $result.signer = if ($signature.SignerCertificate) { $signature.SignerCertificate.Subject } else { "" }
    if ($signature.Status -ne [System.Management.Automation.SignatureStatus]::Valid) {
        throw "Installer signature is not valid: $($signature.Status) $($signature.StatusMessage)"
    }
    $result.signature_valid = $true
    $result.sha256 = (Get-FileHash -Algorithm SHA256 -Path $installer).Hash.ToLowerInvariant()
    $versionInfo = (Get-Item -LiteralPath $installer).VersionInfo
    $result.version = $versionInfo.ProductVersion

    if ($Install) {
        $process = Start-Process -FilePath $installer -ArgumentList "/S" -Wait -PassThru
        if ($process.ExitCode -ne 0) {
            throw "Obsidian installer exited with code $($process.ExitCode)."
        }
        $result.installed = $true
        if (-not $KeepInstaller) {
            Remove-Item -LiteralPath $installer -Force
            $result.installer_path = "removed-after-successful-install"
        }
    }

    $lockStream.Dispose()
    $lockStream = $null
    Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
    Write-ResultAndExit -Result $result -ExitCode 0
}
catch {
    if ($lockStream) {
        $lockStream.Dispose()
        $lockStream = $null
    }
    if ($lockPath) {
        Remove-Item -LiteralPath $lockPath -Force -ErrorAction SilentlyContinue
    }
    $result.error = $_.Exception.Message
    Write-ResultAndExit -Result $result -ExitCode 1
}
