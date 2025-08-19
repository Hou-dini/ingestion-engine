<#
Load secrets from a SecretManagement vault into session environment variables
and optionally run the coordinator script.

Usage examples:
# Load secrets into the current PowerShell session only (no run):
.
\scripts\load_secrets_and_run.ps1

# Load secrets and run the coordinator (in this process):
.
\scripts\load_secrets_and_run.ps1 -Run

# Use a non-default vault name:
.
\scripts\load_secrets_and_run.ps1 -VaultName MyVault -Run

Security notes:
- This script only sets environment variables in the current PowerShell process.
- It converts SecureString to plaintext in-memory to set $env: variables; values are not written to disk.
- Avoid printing secrets to logs; this script will print only redacted values.
#>

param(
    [string]$VaultName = 'LocalStore',
    [string]$CoordinatorScript = '.\scripts\run_coordinator_no_persist.py',
    [switch]$Run,
    [switch]$UnsetAfterRun
)

function Get-SecretPlain {
    param(
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$true)][string]$Vault
    )

    try {
        $s = Get-Secret -Name $Name -Vault $Vault -ErrorAction Stop
        if ($s -is [System.Security.SecureString]) {
            $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($s)
            try {
                $plain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
            } finally {
                [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
            }
            return $plain
        }
        return $s
    } catch {
        Write-Host "Secret '$Name' not found in vault '$Vault'" -ForegroundColor Yellow
        return $null
    }
}

function Redact {
    param([string]$v)
    if (-not $v) { return '' }
    if ($v.Length -le 8) { return 'REDACTED' }
    return $v.Substring(0,4) + '...' + $v.Substring($v.Length-4)
}

Write-Host "Using SecretManagement vault: $VaultName"

# Read secrets (best-effort)
$rid = Get-SecretPlain -Name 'REDDIT_CLIENT_ID' -Vault $VaultName
$rsecret = Get-SecretPlain -Name 'REDDIT_CLIENT_SECRET' -Vault $VaultName
$rua = Get-SecretPlain -Name 'REDDIT_USER_AGENT' -Vault $VaultName
$gcs = Get-SecretPlain -Name 'GCS_CREDENTIALS_JSON' -Vault $VaultName
$gcs_bucket = Get-SecretPlain -Name 'GCS_BUCKET_NAME' -Vault $VaultName

# Set session environment variables only if found
if ($rid) { $env:REDDIT_CLIENT_ID = $rid }
if ($rsecret) { $env:REDDIT_CLIENT_SECRET = $rsecret }
if ($rua) { $env:REDDIT_USER_AGENT = $rua }
if ($gcs) { $env:GCS_CREDENTIALS_JSON = $gcs }
if ($gcs_bucket) { $env:GCS_BUCKET_NAME = $gcs_bucket }

# Print redacted diagnostics
Write-Host "Loaded settings (redacted):"
Write-Host "  REDDIT_CLIENT_ID = $(Redact $env:REDDIT_CLIENT_ID)"
Write-Host "  REDDIT_CLIENT_SECRET = $(Redact $env:REDDIT_CLIENT_SECRET)"
Write-Host "  REDDIT_USER_AGENT = $($env:REDDIT_USER_AGENT)"
Write-Host "  GCS_CREDENTIALS_JSON = $(Redact $env:GCS_CREDENTIALS_JSON)"
Write-Host "  GCS_BUCKET_NAME = $env:GCS_BUCKET_NAME"

if ($Run) {
    Write-Host "Running coordinator script: $CoordinatorScript"
    # Run in the same process so env vars are visible
    & python $CoordinatorScript
}

# Optionally unset the environment variables we set in this session.
if ($UnsetAfterRun) {
    Write-Host "Unsetting loaded environment variables from this session"
    if ($rid) { Remove-Item Env:\REDDIT_CLIENT_ID -ErrorAction SilentlyContinue }
    if ($rsecret) { Remove-Item Env:\REDDIT_CLIENT_SECRET -ErrorAction SilentlyContinue }
    if ($rua) { Remove-Item Env:\REDDIT_USER_AGENT -ErrorAction SilentlyContinue }
    if ($gcs) { Remove-Item Env:\GCS_CREDENTIALS_JSON -ErrorAction SilentlyContinue }
    if ($gcs_bucket) { Remove-Item Env:\GCS_BUCKET_NAME -ErrorAction SilentlyContinue }
    Write-Host "Environment variables removed from session."
}
