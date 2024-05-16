# Install ImportExcel module if not already installed
if (-not (Get-Module -Name ImportExcel -ListAvailable)) {
    Install-Module ImportExcel -Scope CurrentUser -Force
}

# Define NAS share paths
$nasShare1 = "\\NAS1\Share1"
$nasShare2 = "\\NAS2\Share2"

# Function to calculate MD5 hash of a file
function Get-FileHashMD5($filePath) {
    $md5 = New-Object -TypeName System.Security.Cryptography.MD5CryptoServiceProvider
    $fileStream = [System.IO.File]::OpenRead($filePath)
    $hash = [System.BitConverter]::ToString($md5.ComputeHash($fileStream))
    $fileStream.Close()
    $hash
}

# Function to get files and their MD5 hashes from a NAS share
function Get-FilesAndHashesFromNAS($nasShare) {
    $filesAndHashes = @()
    $files = Get-ChildItem -Path $nasShare -Recurse -File

    foreach ($file in $files) {
        $fileHash = Get-FileHashMD5 $file.FullName
        $fileObject = [PSCustomObject]@{
            "File" = $file.FullName
            "MD5 Hash" = $fileHash
        }
        $filesAndHashes += $fileObject
    }

    return $filesAndHashes
}

# Get files and their MD5 hashes from each NAS share
$nas1FilesAndHashes = Get-FilesAndHashesFromNAS $nasShare1
$nas2FilesAndHashes = Get-FilesAndHashesFromNAS $nasShare2

# Create Excel report
$reportData = @()

foreach ($file in $nas1FilesAndHashes) {
    $nas2File = $nas2FilesAndHashes | Where-Object { $_.File -eq $file.File }
    if ($nas2File) {
        $reportData += [PSCustomObject]@{
            "File" = $file.File
            "NAS1 MD5 Hash" = $file."MD5 Hash"
            "NAS2 MD5 Hash" = $nas2File."MD5 Hash"
        }
    } else {
        $reportData += [PSCustomObject]@{
            "File" = $file.File
            "NAS1 MD5 Hash" = $file."MD5 Hash"
            "NAS2 MD5 Hash" = "File not found in NAS2"
        }
    }
}

foreach ($file in $nas2FilesAndHashes) {
    $nas1File = $nas1FilesAndHashes | Where-Object { $_.File -eq $file.File }
    if (-not $nas1File) {
        $reportData += [PSCustomObject]@{
            "File" = $file.File
            "NAS1 MD5 Hash" = "File not found in NAS1"
            "NAS2 MD5 Hash" = $file."MD5 Hash"
        }
    }
}

# Export report data to Excel
$reportData | Export-Excel -Path "NASComparisonReport.xlsx" -AutoSize -Show
