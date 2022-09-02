#!/usr/bin/env python3

import argparse
import subprocess
import os
import datetime
from xml.etree.ElementTree import ElementTree
import random
import string

class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKCYAN = '\033[96m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'

scriptFolderPath=os.path.dirname(os.path.realpath(__file__))

# Define the input argument parameters
parser = argparse.ArgumentParser(description="Run this script to build the Docker container. The working folder is the folder of this script.", epilog="@Author: michael.helfenstein@noser.com")
parser.add_argument("-p", "--directoryBuildPropsFile",
                    help="The .net Directory.Build.props with common parameters.",
                    default=f"{scriptFolderPath}/Directory.Build.props",
                    type=argparse.FileType("r", encoding="UTF-8"), # Returns a open file
                    required=False)
parser.add_argument("-r", "--registry", 
                    help="The docker registry to deploy the image. It will override the value in the Directory.Build.props file under the node ImageRepository.",
                    type=str,
                    required=False)
parser.add_argument("-f", "--file",
                    help=" Name of the Dockerfile.",
                    default=f"{scriptFolderPath}/Dockerfile",
                    type=argparse.FileType("r", encoding="UTF-8"), # Returns a open file
                    required=False)
parser.add_argument("-c", "--context",
                    help="The build context relative to this scripts folder. Default is ./",
                    default="./",
                    type=str, 
                    required=False)
parser.add_argument("--pull",
                    help="Always attempt to pull a newer version of the image",
                    default=True,
                    action='store_false',
                    required=False)
parser.add_argument("--no-cache",
                    help="Do not use cache when building the image",
                    default=True,
                    action='store_false',
                    required=False)
parser.add_argument("--testresultsCopy",
                    help="copy the testresults out of the container",
                    default=False,
                    action='store_true',
                    required=False)
parser.add_argument("--testresultsOutPath",
                    help="copy the testresults to the local path. Default is the testresults in this scriptfolder.",
                    default=f"{scriptFolderPath}/testresults",
                    type=str, 
                    required=False)
args = parser.parse_args()

print("╔══════════════════════════════════════════════════════════╗")
print("║                          prepare                         ║")
print("╚══════════════════════════════════════════════════════════╝")
print(f"Use directoryBuildPropsFile='{args.directoryBuildPropsFile.name}'")

# Read parameter file
directoryBuildPropsTree = ElementTree()
directoryBuildPropsTree.parse(args.directoryBuildPropsFile) 
xmlElements = directoryBuildPropsTree.getroot().find('PropertyGroup')
xmlDict = {}
for item in xmlElements:
    xmlDict[item.tag]=item.text

buildVersion = xmlDict['Version']
product = xmlDict['Product']
imageMaintainer = xmlDict['ImageMaintainer']
imageName = xmlDict['ImageName']

registry = str('')
if args.registry:
  registry = args.registry
else:
  registry = xmlDict['ImageRepository']
print(f"Use registry={registry}")

buildDate = f"{datetime.datetime.utcnow().strftime('%G-%m-%dT%H.%MZ')}"

sourceCommitId = subprocess.run("git rev-parse HEAD",
                            shell=True,
                            check=True,
                            universal_newlines=True,
                            stdout=subprocess.PIPE).stdout.strip() # the result is not printed in the python stdout
sourceUrl = subprocess.run("git remote get-url --all origin",
                            shell=True,
                            check=True,
                            universal_newlines=True,
                            stdout=subprocess.PIPE).stdout.strip() # the result is not printed in the python stdout

completeImageName = f"{registry}/{imageName}"
completeImageNameTagged = f"{completeImageName}:{buildVersion}"

print(f"Building image={completeImageNameTagged} using following parameters: buildDate={buildDate}; product={product}; imageMaintainer={imageMaintainer}")

exe = "docker"
pullArgument = "--pull " if args.pull == True else ""
noCacheArgument = "--no-cache " if args.no_cache == True else ""


print(bcolors.OKGREEN + "done\n" + bcolors.ENDC)
print("╔══════════════════════════════════════════════════════════╗")
print("║                     Build Container                      ║")
print("╚══════════════════════════════════════════════════════════╝")
buildArgs = ("build "
    f"--tag {completeImageNameTagged} "
    f"--build-arg BUILD_VERSION={buildVersion} "
    f"--build-arg BUILD_DATE={buildDate} "
    f"--build-arg MAINTAINER={imageMaintainer} "
    f"--build-arg PRODUCT=\"{product}\" "
    f"--build-arg SOURCECOMMITID={sourceCommitId} "
    f"--build-arg SOURCEURL={sourceUrl} "
    f"-f {args.file.name} " f"{args.context}")

print(f"Build container with command: {exe} {buildArgs}")
subprocess.run(f"{exe} {buildArgs}",
                cwd=f"{scriptFolderPath}",
                shell=True,
                check=True,
                universal_newlines=True)


print(bcolors.OKGREEN + "done\n" + bcolors.ENDC)
if args.testresultsCopy:
    print("╔══════════════════════════════════════════════════════════╗")
    print("║            Copy UniTests out of the Container            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    testresultsSource = "/app/testresults"
    testresultsTarget = args.testresultsOutPath
    containername = "build_" + ''.join(random.choice(string.ascii_lowercase) for i in range(10))
    print(bcolors.HEADER + f"Copy the unit test results out of the container from container folder={testresultsSource} to local folder={testresultsTarget}" + bcolors.ENDC)
    print(f"Create container={containername} to copy out unit test results")
    subprocess.run(f"docker create -ti --name {containername} {completeImageNameTagged}",
                cwd=f"{scriptFolderPath}",
                shell=True, check=True, universal_newlines=True)

    print(f"Copy unit test results to {testresultsTarget}")
    subprocess.run(f"docker cp {containername}:{testresultsSource} {testresultsTarget}",
                cwd=f"{scriptFolderPath}",
                shell=True, check=True, universal_newlines=True)

    print(f"Cleanup container={containername}")
    subprocess.run(f"docker rm -f {containername}",
                cwd=f"{scriptFolderPath}",
                shell=True, check=True, universal_newlines=True)

# Cleanup
args.directoryBuildPropsFile.close()
args.file.close()
print(bcolors.OKGREEN + "done" + bcolors.ENDC)
print(bcolors.OKGREEN + "±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±" + bcolors.ENDC)