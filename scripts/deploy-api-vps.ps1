param(
    [Parameter(Mandatory = $true)]
    [string]$DeployHost,

    [string]$DeployUser = "ubuntu",
    [string]$DeployPath = "/opt/relojeria",
    [ValidateSet("production", "staging")]
    [string]$DeployEnv = "production",
    [string]$EnvFile = ""
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($EnvFile)) {
    if ($DeployEnv -eq "production") {
        $EnvFile = ".env.production"
    } else {
        $EnvFile = ".env.staging"
    }
}

if ($DeployPath.Contains("'")) {
    throw "DeployPath cannot contain single quotes."
}

if (-not (Test-Path -LiteralPath $EnvFile)) {
    throw "Missing required file: $EnvFile"
}

$composeProjectName = if ($DeployEnv -eq "production") { "relojeria-prod" } else { "relojeria-staging" }
$verifyUrl = if ($DeployEnv -eq "production") { "https://api.tutallerrelojero.com/health" } else { "https://api-staging.tutallerrelojero.com/health" }

$backendHostPort = Select-String -Path $EnvFile -Pattern '^BACKEND_HOST_PORT=' |
    Select-Object -First 1 |
    ForEach-Object { ($_.Line -split '=', 2)[1].Trim() }

if ([string]::IsNullOrWhiteSpace($backendHostPort)) {
    throw "BACKEND_HOST_PORT is required in $EnvFile."
}

$requiredFiles = @(
    "docker-compose.vps.yml",
    "infra/nginx/relojeria-vps.conf",
    "scripts/backup-postgres.sh",
    $EnvFile
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $file)) {
        throw "Missing required file: $file"
    }
}

$target = "$DeployUser@$DeployHost"

Write-Host "Creating remote directories on $target`:$DeployPath"
ssh $target "mkdir -p '$DeployPath/infra/nginx' '$DeployPath/scripts'"

Write-Host "Copying deployment files"
scp "docker-compose.vps.yml" "$target`:$DeployPath/docker-compose.vps.yml"
scp "infra/nginx/relojeria-vps.conf" "$target`:$DeployPath/infra/nginx/relojeria-vps.conf"
scp "scripts/backup-postgres.sh" "$target`:$DeployPath/scripts/backup-postgres.sh"
scp $EnvFile "$target`:$DeployPath/.env"

Write-Host "Starting API stack"
$remoteDeploy = "cd '$DeployPath' && chmod +x scripts/backup-postgres.sh && docker compose --env-file .env -p '$composeProjectName' -f docker-compose.vps.yml pull && docker compose --env-file .env -p '$composeProjectName' -f docker-compose.vps.yml up -d && docker compose --env-file .env -p '$composeProjectName' -f docker-compose.vps.yml ps"
ssh $target $remoteDeploy

Write-Host "Checking local API health on VPS"
ssh $target "curl -fsS http://127.0.0.1:$backendHostPort/health"

Write-Host "Deployment finished. Now verify: $verifyUrl"
Write-Host "If Nginx is not configured yet, run scripts/install-vps-nginx-router.ps1."
