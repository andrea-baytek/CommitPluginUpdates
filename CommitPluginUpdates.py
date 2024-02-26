#!/usr/bin/python3

import os
import subprocess
from typing import Final
from typing import Callable
from typing import List
from pathlib import Path



class Commit:
    def __init__(self, folderName:str, commitMessage:str, type:str) -> None:
        self.folderName = folderName
        self.commitMessage = commitMessage
        self.type = type


def ExecuteCmd(cmd):
    p = subprocess.check_output(cmd, cwd=kWorkingDirectory, encoding="utf-8", text=True)
    result = p.split("\n")
    return result


def GetGitStatus(folder=""):
    cmd = ['git', 'status']
    if folder != "":
        cmd.append(folder) 
    
    return ExecuteCmd(cmd)


def GitAdd(foldername: str):
    cmd = ['git', 'add', foldername]
    return ExecuteCmd(cmd)


def GitDiff(filename: str):
    cmd = ['git', 'diff', filename]
    return ExecuteCmd(cmd)


def GitCommit(commitMessage: str):
    cmd = ['git', 'commit', '-m {}'.format(commitMessage)]
    if kDryRun:
        cmd.append("--dry-run")
    
    return ExecuteCmd(cmd)


def GitMerge(branchNameToMerge: str, mergeStrategy=''):
    cmd = ['git', 'merge', branchNameToMerge]
    if mergeStrategy != '':
        cmd = ['git', 'merge', '-s', mergeStrategy, branchNameToMerge]

    return ExecuteCmd(cmd)


def GitPullAll():
    cmd = ['git', 'pull', '--all']
    return ExecuteCmd(cmd)


def GitPush():
    cmd = ['git', 'push']
    return ExecuteCmd(cmd)


def GitCreateBranch(branchName: str):
    try:
        cmd = ['git', 'checkout', '-b', branchName]
        return ExecuteCmd(cmd)
    except:
        # most likely failed due to existing branch. Try again just switching
        cmd = ['git', 'checkout', branchName]
        return ExecuteCmd(cmd)


def GitDeleteBranch(branchName: str):
    cmd = ['git', 'branch', '-d', branchName]
    return ExecuteCmd(cmd)


def GitCheckoutBranch(branchName: str):
    cmd = ['git', 'checkout', branchName]
    return ExecuteCmd(cmd)


def GetFileArray(folder: str) -> dict[list[str]]:
    """ Returns a two dimensional array of files where the first dimension is the child
    folder and the 2nd is the filenames (with subfolder, if applicable.) in each child
    folder.  

    It uses 'git status' to collect the list of files, and ignores anything not in the
    subfolders of the folder that you pass in.
    
    I'm not super familiar with python's path lib, so I didn't use it much. If you ever 
    need to re-write any of this its probably best to use that instead of just string 
    manipulation. (I sincerely hope you != me in that case)

    example folder structure:
    wp-content/plugins/block/block.php
    wp-content/plugins/block/styles.css
    wp-content/plugins/visibility/visibility.php
    wp-content/plugins/visibility/stylesheets/styles.css
    wp-admin/someFolder/notAPlugin.php  # will be ignored!

    our 2D list:
    ["block"] -> ["block.php"]["styles.css"]
    ["visibility"] -> ["block.php"]["stylesheets/styles.css"]
    """
    result = dict()
    rawData = GetGitStatus()
    for line in rawData:
        # Example input line:
        # "     modified:   wp-content/plugins/baytek-rewrites/app/BaytekRewrites/Plugin.php" 
        cleanLine = line.strip()

        # line is now like: "modified:   wp-content/plugins/baytek-rewrites/app/BaytekRewrites/Plugin.php"      
        if not cleanLine.startswith(kModifiedFilePrefix):
            continue
        
        # This is a tad risky. 
        # If your directory structure ever has nested files with the same name it may fail.
        if not cleanLine.__contains__(folder):
            continue

        # by breaking the line up in separate calls with .strip() between them,
        # it should hold up changes in whitespace (like if some git status messages
        # pad their string with fewer tabs)
        cleanLine = cleanLine.removeprefix(kModifiedFilePrefix)
         # line is now like: "wp-content/plugins/baytek-rewrites/app/BaytekRewrites/Plugin.php"

        cleanLine = cleanLine.strip()
        cleanLine = cleanLine.removeprefix(folder)
         # line is now like: "/baytek-rewrites/app/BaytekRewrites/Plugin.php"

        cleanLine = cleanLine.strip()
        cleanLine = cleanLine.removeprefix("/")
         # line is now like: "baytek-rewrites/app/BaytekRewrites/Plugin.php"

        tokens = cleanLine.split("/")
        if len(tokens) < 2:
            print("Encountered a file in the root plugins folder: {0}".format(cleanLine))
            print("Skipping this file...")
            continue

        folderName = tokens[0]
        # folder name is like: "baytek-rewrites"

        fileWithSubfolder = cleanLine.removeprefix(folderName + "/")
        # fileWithSubfolder is now like: "app/BaytekRewrites/Plugin.php"

        if not folderName in result:
            result[folderName] = list()
        
        result[folderName].append(fileWithSubfolder)
        
    return result


def GetAbsoloutePath(filename:str, folderName: str):
    """ Converts a filename like 'file.php' into a full path like '/home/user/file.php'
    using the current working directory. It also assumes that the script runs from the
    root of the site repo, and plugins exist in ./wp-content/plugins 
    """
    return os.path.join(kWorkingDirectory, folderName, filename)


def GetPluginMainFilePath(folder: list, folderName: str) -> str:
    """ Finds a file that we think is the 'main' file of a plugin. We look for files
    with the same name as the folder which also have the exension .php, or files called
    'main.php' 
    """
    # this method explicitly filters out matching files in subdirectories
    for filename in folder:  
        if  "/" in filename:
            continue

        if Path(filename).suffix != ".php":
            continue

        fullPath = GetAbsoloutePath(filename, folderName)
        with open(fullPath, "r") as file:
            for line in file.readlines():
                if "Plugin Name" in line:
                    return fullPath
                    
    return ""


def GetHumanReadablePluginName(mainFileName: str) -> str:
    """ If the passed-in file has a line like 'Plugin Name: My Cool Plugin', this
    function will find and return it. In case of failure, it returns an empty 
    string
    """
    result = ""
    file = open(mainFileName, "r")
    for line in file.readlines():
        if "Plugin Name:" not in line:
            continue
        
        # We do these treatments in steps because not all files have stars or coons in the name.
        # if you find yourself adding more logic here, consider a regular epression instead.
        cleanline = line.strip()    # removes whitespace
        cleanline = cleanline.removeprefix("*")
        cleanline = cleanline.strip()
        cleanline = cleanline.removeprefix("Plugin Name")
        cleanline = cleanline.strip()
        cleanline = cleanline.removeprefix(":")
        cleanline = cleanline.strip()
        result = cleanline
        break
    
    file.close()
    return result


def GetVersionNumberFromDiffLine(line:str):
    """ Takes a git diff line like '- * Version:             3.0.3' and extracts just
    the version number. Many assumptions included here: Vesrion numbers don't have spaces,
    the number is the last token on the line, etc.
    """
    cleanLine = line.strip()
    tokens = line.split(" ")
    return tokens.pop()


def GetVersionNumbers(filename) -> [str, str]:
    """ Returns a tuple of strings which represent the old version number and
    the new version number. It does this by parsing the output of the git diff
    and looking for lines changes with version numbers. 
    
    In case of failure, returns a tuple of empty strings 
    """
    oldVersion = ""
    newVersion = ""

    diffData = GitDiff(filename)
    for line in diffData:
        # line example: '- * Version:             3.0.3'
        cleanLine = line.strip()
        
        if "version:" not in cleanLine.lower():
            continue

        if cleanLine.startswith("-"):
            oldVersion = GetVersionNumberFromDiffLine(cleanLine)
        
        if cleanLine.startswith("+"):
            newVersion = GetVersionNumberFromDiffLine(cleanLine)

        if (oldVersion != "") and ( newVersion != ""):
            break
    
    if oldVersion == "" or newVersion == "":
        print("Failed to find version numbers in file {0}".format(filename))

    return [oldVersion, newVersion]


def GetCommitMessage(pluginName: str, versionOld: str, versionNew: str):
    return "{0} - {1} to {2}".format(pluginName, versionOld, versionNew)


def ProcessPluginFolder(fileList: list, folderName: str, rootFolder: str):
    # Call me paranoid but I just don't trust dynamic typing at all
    if (not isinstance(fileList, list)) or len(fileList) < 1:
        print("This is NOT a list: {0}".format(fileList))
        return
    
    if (not isinstance(folderName, str)) or (folderName == ""):
        print("Bad folder name: {0}".format(folderName))
        return

    pluginFolder=os.path.join(rootFolder, folderName)
    mainFileFullPath = GetPluginMainFilePath(fileList, pluginFolder)
    if mainFileFullPath == None or mainFileFullPath == "":
        print("Could not find a main php file in plugin folder '{0}'.".format(folderName))
        return
    
    pluginName = GetHumanReadablePluginName(mainFileFullPath)
    if pluginName == None or pluginName == "":
        pluginName = folderName
    
    versionOld, versionNew = GetVersionNumbers(mainFileFullPath)
    if versionOld == "" or versionNew == "":
        print("failed to find version numbers for '{0}'.".format(pluginName))
        return

    # At this point, we have everything we need, we can start doing mutating operations
    commitMessage = GetCommitMessage(pluginName, versionOld, versionNew)
    return Commit(pluginFolder, commitMessage, "Plugin")
    

def ProcessThemeFolder(_fileList: list, folderName: str, rootFolder: str):
    # Call me paranoid but I just don't trust dynamic typing at all
    
    if (not isinstance(folderName, str)) or (folderName == ""):
        print("Bad folder name: {0}".format(folderName))
        return
    
    commitMessage = "Updated Theme {0}".format(folderName)
    return Commit(os.path.join(rootFolder, folderName), commitMessage, "Theme")


def CreateTranslationList() -> list:
    folders = GetFileArray(kLanguagesFolder)
    if len(folders) == 0:
        return []
    
    return [Commit(kLanguagesFolder,"Updated Translations", "Translation")]


def ManualCommitOptions(commit: Commit):
    while True:
        print("----------------------------------------------------------")
        print("{} found: '{}', message: {}".format(commit.type, commit.folderName, commit.commitMessage))
        print()
        print("Choose an option:")
        print("1: commit this change")
        print("2: print files to be committed")
        print("3: skip this plugin")
        print("Enter anything else to quit")
        command = input()
        fullPluginPath = GetAbsoloutePath("", commit.folderName)
        if (command == "1"):
            GitAdd(fullPluginPath)
            print(GitCommit(commit.commitMessage))
            break

        if (command == "2"):
            print()
            PrintGitStatus(fullPluginPath)
            print()
            continue

        if (command == "3"):
            print("No changes committed, no files staged. Jumping to next plugin folder...")
            break

        print("Exiting...")
        quit()


def PrintGitStatus(folderPath):
    status = GetGitStatus(folderPath)
    for line in status:
        print(line.strip())


def GetProductionBranchName():
    print("Enter the repo's production branch name:")
    branchName = input()
    return branchName


def SetUpGitBranchesForUpdates(mainBranch: str, tempBranchName: str, pluginUpdatesBranchName: str):
    # git checkout $DEFAULT_BRANCH_NAME 
    GitCheckoutBranch(mainBranch)
    # git pull --all 
    GitPullAll()
    # # git checkout -b temp-plugin-updates 
    GitCreateBranch(tempBranchName)
    # # git merge -s ours plugin-updates
    # GitMerge(pluginUpdatesBranchName, "ours")


def MergeAndPushBranch(toBranch: str, fromBranch: str):
    GitCheckoutBranch(toBranch)
    GitMerge(fromBranch)
    GitPush()


def ManuallyCommitChanges(pluginList: List[Commit]):
    # Iterate through the list of plugin objects and provide options for each one
    for plugin in pluginList:
        ManualCommitOptions(plugin)


def AutomaticallyCommitChanges(list: List[Commit]):
    # Iterate through the list of objects and commit each one
    for item in list:
        fullPath = GetAbsoloutePath("", item.folderName)
        GitAdd(fullPath)
        print(GitCommit(item.commitMessage))


def CreateUpdateList(folder: str, Processor: Callable):
    fileList = GetFileArray(folder)
    if len(fileList) == 0:
        print("No plugin files found!")
        return []
    
    updateList = []
    for subfolder in fileList:
        plugin = Processor(fileList[subfolder], subfolder, folder)
        if plugin != None:
            updateList.append(plugin)
    
    return updateList



# Constant vlaues. Pretty please, never change them at run time.
# God I wish every language had C++'s concept of "const"...
kWorkingDirectory : Final[str] = os.getcwd()
kPluginsFolder : Final[str] = "wp-content/plugins"
kThemesFolder : Final[str] = "wp-content/themes"
kLanguagesFolder : Final[str] = "wp-content/languages"
kModifiedFilePrefix = "modified:"
kDryRun = False
kTempBranchName = "temp-plugin-updates"
kPluginUpdatesBranchName = "plugin-updates"

if __name__ == "__main__":
    os.system('clear') 
    print("Setting up git branches for updates.")

    branchName = GetProductionBranchName()

    SetUpGitBranchesForUpdates(branchName, kTempBranchName, kPluginUpdatesBranchName)
    
    print("Go update all themes, plugins, and translations on local site, then press enter to continue:")
    input()

    print("Searching the curent directory for plugin files....")

    # So now the first dimension of our list is a plugin folder, and the second is all files in that folder.
    
    commits = CreateUpdateList(kPluginsFolder, ProcessPluginFolder)
    commits += CreateUpdateList(kThemesFolder, ProcessThemeFolder)
    commits += CreateTranslationList()

    print("Would you like to commit files automatically or manually?")
    print("1: Automatically")
    print("2: Manually")
    command = input()
    if (command == "1"):
        AutomaticallyCommitChanges(commits)

    if (command == "2"):
        ManuallyCommitChanges(commits)

    print()
    print("----------------------------------------------------------")
    print("All automated commits complete.")
    print("You may now make any additonal commits if needed. When you're ready, press enter to push everything:")
    input()

    # Uncomment the line below to use the plugin-updates branch
    # MergeAndPushBranch(kPluginUpdatesBranchName, kTempBranchName)

    # print("First merge and push complete. When you're ready, press enter to complete merge:")
    # input()

    MergeAndPushBranch(branchName, kTempBranchName)

    GitDeleteBranch(kTempBranchName)

    print()
    print("----------------------------------------------------------")
    print("Updates complete. Exiting.")