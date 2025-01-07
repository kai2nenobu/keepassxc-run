$ErrorActionPreference = 'Stop'
$PSNativeCommandErrorActionPreference = $true

# Install KeePassXC
choco install -y --no-progress keepassxc autohotkey

# Install git-credential-keepassxc
$zip_url = 'https://github.com/Frederick888/git-credential-keepassxc/releases/download/v0.14.1/windows-latest-minimal.zip'
$zip_path = "${env:TEMP%}\git-credential-keepassxc.zip"
curl.exe -sSL $zip_url -o $zip_path
7z x $zip_path -o"$env:USERPROFILE\.cargo\bin"

# Import a KeePassXC database in XML format
$keepassxc_cli = 'C:\Program Files\KeePassXC\keepassxc-cli.exe'
&$keepassxc_cli import --set-key-file .\tests\data\test_db.keyx .\tests\data\test_db.xml .\tests\data\test_db.kdbx
