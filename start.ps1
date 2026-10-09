$ErrorActionPreference = "Stop"

Write-Host "Starting PostgreSQL and API..."
docker compose up --build -d
if ($LASTEXITCODE -ne 0) {
    throw "Docker Compose could not start PostgreSQL and the API."
}

try {
    Write-Host "Starting frontend..."
    Set-Location "$PSScriptRoot\web"
    npm run dev
}
finally {
    Set-Location $PSScriptRoot
    Write-Host "Stopping PostgreSQL and API..."
    docker compose down
}
