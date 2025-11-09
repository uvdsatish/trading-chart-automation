# PowerShell script to create a desktop shortcut for the VS Code Admin Launcher

# Get the desktop path
$DesktopPath = [Environment]::GetFolderPath("Desktop")

# Define paths
$ShortcutPath = "$DesktopPath\VS Code Admin - Browser Automation.lnk"
$TargetPath = "$PSScriptRoot\launch_vscode_admin.bat"
$IconPath = "$env:LocalAppData\Programs\Microsoft VS Code\Code.exe"

# Create the shortcut
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "Launch VS Code as Administrator for Browser Automation Project"

# Try to set VS Code icon if it exists
if (Test-Path $IconPath) {
    $Shortcut.IconLocation = "$IconPath,0"
} else {
    # Fallback to cmd icon if VS Code not found
    $Shortcut.IconLocation = "%SystemRoot%\System32\cmd.exe,0"
}

# Save the shortcut
$Shortcut.Save()

Write-Host "Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "Location: $ShortcutPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now:" -ForegroundColor Yellow
Write-Host "1. Double-click the desktop shortcut to launch VS Code as admin"
Write-Host "2. Right-click and pin to taskbar for quick access"
Write-Host "3. The UAC prompt will appear when you use it"