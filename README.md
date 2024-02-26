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
4. Run `CommitPluginUpdates.py`


--------

### SET PERMANENT PATH ENVIRONMENT VARIABLE
#### MAC OS
When running scripts it is easier to enter only the file name of the script you want to run (e.g. my-script.py), 
rather than the entire path (e.g. /Users/ThisUser/Documents/my-script.py). 

To do this, create a folder to store your script(s). The conventional name for this type of folder is 'bin' but it can be named anything.
Then create a path variable to this folder by following the instructions below.

To set path environment variable:
1. In terminal, enter: `sudo nano /etc/paths`
2. Paste the path you want to save (e.g. /Users/ThisUser/Documents/my-script.py).
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