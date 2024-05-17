# Define output CSV file paths
$outputCsvFilePath1 = "NAS1_Hashes.csv"
$outputCsvFilePath2 = "NAS2_Hashes.csv"

# Define log file path
$logFilePath = "NASComparisonLog.txt"

# Function to write data to a CSV file
function Write-ToCsvFile($filePath, $data) {
    $data | Export-Csv -Path $filePath -Delimiter "," -NoTypeInformation
}

# Function to write log message to log file
function Write-Log($message) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $message"
    Add-Content -Path $logFilePath -Value $logMessage
}

# Log start of script
Write-Log "Starting NAS hashing script..."

# Function to generate hashes for files in a NAS share
function Generate-HashesForNAS($nasShare) {
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

# Get hashes for files in each NAS share
$nas1FilesAndHashes = Generate-HashesForNAS $nasShare1
$nas2FilesAndHashes = Generate-HashesForNAS $nasShare2

# Log progress
Write-Log "Hashes generated for files in NAS shares."

# Write hashes to CSV for NAS1
Write-ToCsvFile -FilePath $outputCsvFilePath1 -Data $nas1FilesAndHashes
Write-Log "Hashes for NAS1 written to $outputCsvFilePath1."

# Write hashes to CSV for NAS2
Write-ToCsvFile -FilePath $outputCsvFilePath2 -Data $nas2FilesAndHashes
Write-Log "Hashes for NAS2 written to $outputCsvFilePath2."

# Log end of script
Write-Log "Script completed."
