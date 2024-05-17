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

# Function to generate hashes for files in a NAS share (running in a separate runspace)
function Generate-HashesForNAS($nasShare, $outputFilePath) {
    $filesAndHashes = @()
    $files = Get-ChildItem -Path $nasShare -Recurse -File
    $totalFiles = $files.Count
    $processedFiles = 0

    foreach ($file in $files) {
        $fileHash = Get-FileHashMD5 $file.FullName
        $fileObject = [PSCustomObject]@{
            "File" = $file.FullName
            "MD5 Hash" = $fileHash
        }
        $filesAndHashes += $fileObject

        # Update progress
        $processedFiles++
        $progressPercentage = [Math]::Round(($processedFiles / $totalFiles) * 100, 2)
        Write-Log "Progress: $progressPercentage% completed for $nasShare."
    }

    # Write hashes to CSV
    Write-ToCsvFile -FilePath $outputFilePath -Data $filesAndHashes
    Write-Log "Hashes for $nasShare written to $outputFilePath."
}

# Log start of script
Write-Log "Starting NAS hashing script..."

# Run hashing for each NAS share in parallel
$runspacePool = [runspacefactory]::CreateRunspacePool(1, [Environment]::ProcessorCount)
$runspacePool.Open()

$nas1Runspace = [powershell]::Create().AddScript({
    param($nasShare, $outputFilePath)
    Generate-HashesForNAS $nasShare $outputFilePath
}).AddArgument($nasShare1).AddArgument($outputCsvFilePath1)
$nas1Runspace.RunspacePool = $runspacePool
$nas1Handle = $nas1Runspace.BeginInvoke()

$nas2Runspace = [powershell]::Create().AddScript({
    param($nasShare, $outputFilePath)
    Generate-HashesForNAS $nasShare $outputFilePath
}).AddArgument($nasShare2).AddArgument($outputCsvFilePath2)
$nas2Runspace.RunspacePool = $runspacePool
$nas2Handle = $nas2Runspace.BeginInvoke()

# Wait for runspaces to complete
$nas1Runspace.EndInvoke($nas1Handle)
$nas2Runspace.EndInvoke($nas2Handle)

# Close runspace pool
$runspacePool.Close()

# Log end of script
Write-Log "Script completed."
