$xml = [Xml] (Get-Content .\Directory.Build.props)
$buildVersion = [Version] $xml.Project.PropertyGroup.Version
$repository = $xml.Project.PropertyGroup.ImageRepository
$imageName = $xml.Project.PropertyGroup.ImageName
$completeImageName = "${repository}/${imageName}"
Write-Host "the imagename is: $completeImageName"
Write-Host "the product version is: $buildVersion"

$exe = "docker"
$allArgs = @("run", "-d", "-p", "5111:80",
	"--env", "config:section:parameter=<Password>",
	"${completeImageName}:${buildVersion}")
Write-Host "Execute command: $exe $allArgs"
& $exe $allArgs
