#!/usr/bin/env python3
import argparse
import subprocess
import os
from xml.etree.ElementTree import ElementTree

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
parser = argparse.ArgumentParser(description="Run this script to push the Docker container image defined in the Directory.Build.props. The working folder is the folder of this script. when using --acrlogin az login should already be executed!", epilog="@Author: michael.helfenstein@noser.com")
parser.add_argument("-p", "--directoryBuildPropsFile",
                    help="The .net Directory.Build.props with common parameters.",
                    default=f"{scriptFolderPath}/Directory.Build.props",
                    type=argparse.FileType("r", encoding="UTF-8"), # Returns a open file
                    required=False)
parser.add_argument("-r", "--registry",
                    help="The docker registry to deploy the image. It will override the value in the Directory.Build.props file under the node ImageRepository.",
                    type=str,
                    required=False)
parser.add_argument("--acrlogin",
                    help="Login to the azure container registry before push",
                    action='store_true',
                    required=False)
parser.add_argument("-s", "--subscription",
                    help="Azure subscription Name or ID to use for deploy resources. You can read the subscirptions by using `az account list`. You can configure the default subscription using `az account set -s NAME_OR_ID`.",
                    type=str,
                    required=False)

args = parser.parse_args()

print("╔══════════════════════════════════════════════════════════╗")
print("║                        Prepare                           ║")
print("╚══════════════════════════════════════════════════════════╝")
print(f"Use directoryBuildPropsFile='{args.directoryBuildPropsFile.name}'")

subscriptionArg: str = ""
if args.subscription:
    subscriptionArg = f" --subscription {args.subscription}"
    print(f"Use Subscription={args.subscription}")

# Read parameter file
directoryBuildPropsTree = ElementTree()
directoryBuildPropsTree.parse(args.directoryBuildPropsFile)
xmlElements = directoryBuildPropsTree.getroot().find('PropertyGroup')
xmlDict = {}
for item in xmlElements:
    xmlDict[item.tag]=item.text

buildVersion = xmlDict['Version']
product = xmlDict['Product']
imageName = xmlDict['ImageName']

registry = str('')
if args.registry:
    registry = args.registry
else:
    registry = xmlDict['ImageRepository']
print(f"Use registry={registry}")

sourceCommitId = subprocess.run("git rev-parse HEAD",
                                shell=True,
                                check=True,
                                universal_newlines=True,
                                stdout=subprocess.PIPE).stdout.strip() # the result is not printed in the python stdout

completeImageName = f"{registry}/{imageName}"
completeImageNameTagged = f"{completeImageName}:{buildVersion}"
completeImageNameTaggedCommitId = f"{completeImageName}:{sourceCommitId}"

if args.acrlogin:
    print(f"Login to registry={registry} with azure cli")
    subprocess.run(f"az acr login -n {registry} {subscriptionArg}",
                    cwd=f"{scriptFolderPath}",
                    shell=True,
                    check=True,
                    universal_newlines=True)

# functions:
def pushImage(completeImage: str):
    exe = "docker"
    allArgs = ("push "
        f"{completeImage} ")

    print(f"Push container with command: {exe} {allArgs}")
    subprocess.run(f"{exe} {allArgs}",
                    cwd=f"{scriptFolderPath}",
                    shell=True,
                    check=True,
                    universal_newlines=True)

def tagImage(orgImage: str, imageTag: str):
    exe = "docker"
    allArgs = ("image " "tag "
        f"{orgImage} "
        f"{imageTag} ")

    print(f"Push container with command: {exe} {allArgs}")
    subprocess.run(f"{exe} {allArgs}",
                    cwd=f"{scriptFolderPath}",
                    shell=True,
                    check=True,
                    universal_newlines=True)


print(bcolors.OKGREEN + "done\n" + bcolors.ENDC)
print("╔══════════════════════════════════════════════════════════╗")
print("║                 Push Container Image                     ║")
print("╚══════════════════════════════════════════════════════════╝")
print(f"Push image={completeImageNameTagged} and {completeImageNameTaggedCommitId} of the product={product}")

tagImage(completeImageNameTagged, completeImageNameTaggedCommitId)
pushImage(completeImageNameTagged)
pushImage(completeImageNameTaggedCommitId)

# Cleanup
args.directoryBuildPropsFile.close()
print(bcolors.OKGREEN + "done" + bcolors.ENDC)
print(bcolors.OKGREEN + "±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±" + bcolors.ENDC)
