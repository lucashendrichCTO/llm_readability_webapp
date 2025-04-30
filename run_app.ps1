# PowerShell script to run the LLM Readability Web App
# Created: April 30, 2025

# Navigate to the application directory
$appDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $appDir

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Found $pythonVersion"
} catch {
    Write-Host "Python is not installed or not in PATH. Please install Python 3.x and try again."
    exit 1
}

# Install dependencies if needed
Write-Host "Checking and installing dependencies..."
python -m pip install -r requirements.txt

# Start the application
Write-Host "Starting LLM Readability Web App..."
Write-Host "The application will be available at http://127.0.0.1:8000"
Write-Host "Press Ctrl+C to stop the server when done."

# Run the application
python -m uvicorn main:app --host 127.0.0.1 --port 8000

# Note: The script will hang here while the application is running
# which is expected behavior
