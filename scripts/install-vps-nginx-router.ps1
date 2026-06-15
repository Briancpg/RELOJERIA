param(
    [Parameter(Mandatory = $true)]
    [string]$DeployHost,

    [string]$DeployUser = "ubuntu",
    [string]$DeployPath = "/opt/relojeria"
)

$ErrorActionPreference = "Stop"

if ($DeployPath.Contains("'")) {
    throw "DeployPath cannot contain single quotes."
}

if (-not (Test-Path -LiteralPath "infra/nginx/relojeria-vps.conf")) {
    throw "Missing required file: infra/nginx/relojeria-vps.conf"
}

$target = "$DeployUser@$DeployHost"

Write-Host "Copying Nginx router config to $target`:$DeployPath"
ssh $target "mkdir -p '$DeployPath/infra/nginx'"
scp "infra/nginx/relojeria-vps.conf" "$target`:$DeployPath/infra/nginx/relojeria-vps.conf"

Write-Host "Installing Nginx router config"
$remoteInstall = "sudo cp '$DeployPath/infra/nginx/relojeria-vps.conf' /etc/nginx/sites-available/relojeria-vps.conf && sudo ln -sf /etc/nginx/sites-available/relojeria-vps.conf /etc/nginx/sites-enabled/relojeria-vps.conf && sudo rm -f /etc/nginx/sites-enabled/default && sudo nginx -t && sudo systemctl reload nginx"
ssh $target $remoteInstall

Write-Host "Nginx router installed. Verify:"
Write-Host "  http://api.tutallerrelojero.com/health"
Write-Host "  http://api-staging.tutallerrelojero.com/health"
