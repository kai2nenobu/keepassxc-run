$ErrorActionPreference = 'Stop'; # stop on all errors

$toolsPath = Split-Path $MyInvocation.MyCommand.Definition
$url = 'https://github.com/kai2nenobu/keepassxc-run/releases/download/v0.1.0/keepassxc-run_Windows_x86_64.zip'
$checksum = 'A53BE240857F51609242E489EE99561647C47C220300C99B70C707282554E0B9'
$packageArgs = @{
    PackageName = 'keepassxc-run'
    Url = $url
    Checksum = $checksum
    ChecksumType = 'sha256'
    UnzipLocation = $toolsPath
}

## Download and unpack a zip file - https://chocolatey.org/docs/helpers-install-chocolatey-zip-package
Install-ChocolateyZipPackage @packageArgs
