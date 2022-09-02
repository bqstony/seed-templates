$xml = [Xml] (Get-Content .\Directory.Build.props)
$buildVersion = [Version] $xml.Project.PropertyGroup.Version

$imageName = $xml.Project.PropertyGroup.ImageName
Write-Host "The ImageName is: $imageName"
Write-Host "The ProductVersion is: $buildVersion"

$exe = "docker"
$allArgs = @("run", "-d", "--env", "config:section:parameter=<Password>", "--env", "ApplicationInsights:ConnectionString=<InstrumentationKey>", "registry.azurecr.io/${imageName}:${buildVersion}")
Write-Host "Execute command: $exe $allArgs"
& $exe $allArgs