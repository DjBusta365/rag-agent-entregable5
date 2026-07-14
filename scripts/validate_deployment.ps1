param(
    [Parameter(Mandatory=$true)]
    [string]$BaseUrl
)

Write-Host "Validando API en $BaseUrl"
Invoke-RestMethod -Uri "$BaseUrl/health"
Invoke-RestMethod -Uri "$BaseUrl/knowledge"

$body = @{ question = "Que papel cumple Azure Container Apps en esta practica?" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$BaseUrl/ask" -ContentType "application/json" -Body $body
