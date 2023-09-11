# Kickstart git submodule

## Add submodule

To add this submodule to a project, execute the following command...:

> Important, first navigate to the corresponding folder where the submodule stuff should be placed to. in this case `cd .\source\submodules`.

```cmd

git submodule add -f -b master --name dotnet-lib https://dev.azure.com/company/reponame/_git/dotnet-lib dotnet-lib
```

This creates a file named `.gitmodules` with the entry:

```
[submodule "dotnet-lib"]
	path = Source/submodules/dotnet-lib
	url = https://dev.azure.com/company/reponame/_git/dotnet-lib
	branch = master
```


Updating the submodules

```cmd
git submodule update --init --recursive
git submodule foreach --recursive git fetch
git submodule foreach git merge origin master
```

## QA

### fatal: no submodule mapping found in .gitmodules for path 'Source/submodules/dotnet-lib'
Example:

```cmd
 git submodule status
fatal: no submodule mapping found in .gitmodules for path 'source/submodules/dotnet-lib'
```

just clear the cache

```cmd
git rm --cached .\source\submodules\dotnet-lib\
git submodule update --init --recursive
```