# Commit Plugin Updates Tool

This script it intended to speed up the process of committing updates to plugins, themes, and translations on Wordpress sites.

Commit messages include the following:
- **Plugin**: each plugin has its own commit with the plugin name, previous version and the current version.
- **Theme**: each theme has its own commit with the theme name .
- **Translations**: All translations are grouped in one commit.

*Note*: This script does not handle Wordpress core updates.


## USING THE UPDATE TOOL

1. Add the script to a PATH folder (See below).
2. Open a terminal.
3. Change the directory to the root directory of the site to be updated.
4. Run `CommitPluginUpdates.py`.
5. Follow the prompts from the script:
    1. Enter the repos production name. ***The script will push all commits to the branch name specified here***
    2. When prompted to update all themes, etc. open the backend of the site locally.
    3. Once all updates are complete, hit enter to prompt the script to continue.
    4. Choose whether to make the commits automatically or manually. 
        * **Automatically**
        : will run through all updated and untracked files and commit them without any additional input.
        * **Manually** 
        : Script will prompt you for for an action with each plugin, etc. Choices are: 
            1. Commit plugin 
            2. List all files set to be commited 
            3. Skips this plugin, etc.
    5. Finally, hit enter to push all changes to the repo.




--------

### SET PERMANENT PATH ENVIRONMENT VARIABLE
#### MAC OS
When running scripts it is easier to enter only the file name of the script you want to run (e.g. my-script.py), 
rather than the entire path (e.g. /Users/ThisUser/Documents/bin/my-script.py). 

To do this, create a folder to store your script(s). The conventional name for this type of folder is 'bin' but it can be named anything.
Then create a path variable to this folder by following the instructions below.

To set path environment variable:
1. In terminal, enter: `sudo nano /etc/paths`
2. Paste the path you want to save (e.g. /Users/ThisUser/Documents/bin).
3. Press `Ctrl + O` to save, and then `Ctrl + X` to quit nano.
4. Restart all terminal windows for the changes to take effect.
5. You can now access all files in that path simply by entering the file name in the terminal.


#### WINDOWS

1. Right-click on the Start Button
2. Select “System” from the context menu.
3. Click “Advanced system settings”
4. Go to the “Advanced” tab
5. Click “Environment Variables…”
6. Click variable called “Path” and click “Edit…”
7. Click “New”
8. Enter the path to the folder containing the binary you want on your PATH. 

-----

### TROUBLESHOOTING 
**[Errno 2] No such file or directory** : 
- Confirm that Python3 is installed on your machine. 
- Check the path to your python 3 file by entering the command `which python3` into the terminal. 
- If the value returned does not match `/usr/bin/python3`, edit the path in line one of the script to match the path that was returned.