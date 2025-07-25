# Check if venv folder exists
& Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
if (-Not (Test-Path "venv")) {
    py -m venv venv
    Write-Host "Virtual environment created."
} else {
    Write-Host "Virtual environment already exists."
}

# Activate the virtual environment
& ".\venv\Scripts\Activate.ps1"

# Install requirements
pip install -r requirements.txt
Write-Host "Requirements installed."

# powershell -ExecutionPolicy Bypass -File .\setup_venv.ps1
