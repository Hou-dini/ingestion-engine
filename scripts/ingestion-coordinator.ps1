# PowerShell wrapper to run the CLI module
param(
    [switch]$SkipPersist
)
$flags = @()
if ($SkipPersist) { $flags += '--skip-persist' }
python -m src.cli.coordinator @flags
