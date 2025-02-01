$ErrorActionPreference = 'Stop'; # stop on all errors

$toolsPath = Split-Path $MyInvocation.MyCommand.Definition
$url = 'https://github.com/kai2nenobu/keepassxc-run/releases/download/{{ tag_version }}/{{ zip_file }}'
$checksum = '{{ zip_checksum }}'
$packageArgs = @{
    PackageName = 'keepassxc-run'
    Url = $url
    Checksum = $checksum
    ChecksumType = 'sha256'
    UnzipLocation = $toolsPath
}

## Download and unpack a zip file - https://chocolatey.org/docs/helpers-install-chocolatey-zip-package
Install-ChocolateyZipPackage @packageArgs
