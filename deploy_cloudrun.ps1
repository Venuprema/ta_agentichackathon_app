# Deploy Wendy's Offer App to Google Cloud Run
# 1. Edit YOUR_PROJECT_ID and YOUR_GEMINI_API_KEY below (or use Secret Manager).
# 2. Run: .\deploy_cloudrun.ps1
# Prerequisites: gcloud installed and logged in (gcloud auth login).

param(
    [string]$ProjectId = "YOUR_PROJECT_ID",
    [string]$GeminiKey = "YOUR_GEMINI_API_KEY",
    [string]$Region = "us-central1",
    [switch]$UseSecretManager
)

$ErrorActionPreference = "Stop"

if ($ProjectId -eq "YOUR_PROJECT_ID") {
    Write-Host "Edit this script: set ProjectId and GeminiKey, or run:" -ForegroundColor Yellow
    Write-Host '  .\deploy_cloudrun.ps1 -ProjectId "my-gcp-project" -GeminiKey "your-key"' -ForegroundColor Cyan
    exit 1
}

Write-Host "Step 1: Setting project to $ProjectId" -ForegroundColor Green
gcloud config set project $ProjectId

Write-Host "Step 2: Enabling Cloud Run and Artifact Registry APIs" -ForegroundColor Green
gcloud services enable run.googleapis.com artifactregistry.googleapis.com

Write-Host "Step 3: Deploying from source (this may take a few minutes)..." -ForegroundColor Green
$appRoot = $PSScriptRoot
Set-Location $appRoot

if ($UseSecretManager) {
    gcloud run deploy wendys-offer-app `
        --source . `
        --region $Region `
        --allow-unauthenticated `
        --set-secrets "GEMINI_API_KEY=gemini-api-key:latest"
} else {
    # Env vars: use your gateway URL/model if needed
    $envVars = "GEMINI_API_KEY=$GeminiKey,REQUIRE_GEMINI_KEY=1"
    # Uncomment and set if using AI gateway:
    # $envVars = "GEMINI_API_KEY=$GeminiKey,GEMINI_BASE_URL=https://api.ai-gateway.tigeranalytics.com,GEMINI_MODEL=gemini-2.0-flash,REQUIRE_GEMINI_KEY=1"

    gcloud run deploy wendys-offer-app `
        --source . `
        --region $Region `
        --allow-unauthenticated `
        --memory 1Gi `
        --set-env-vars $envVars
}

Write-Host "Done. Open the Service URL shown above in your browser." -ForegroundColor Green
