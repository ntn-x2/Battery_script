# Battery_script

Small python script to check battery level and notify user if it is under a certain threshold with an alert.

## Usage

Script can run only on OS X devices, since there are some calls to the osascript library.

Script can be launched directly with the command <strong>python file.py [-b N,] [-c M,] [-s K]</strong> where -b is the level of battery under which
user wants to get notified, -c is the frequency (in seconds) at which script checks for a change in battery status (charging, discharging, charged, ...),
-s is the frequency (in seconds) at which script checks for the battery level and eventually notifies user.

By default, -b = 20% -c = 60s and -s = 20s.

## Automatic execution

To automatically execute the script at boot time, move the com.user.battery_list.plist file into ~/Library/LaunchAgents and after that, from within the same folder in which now the file is, type the commands 
<strong>launchctl start com.user.battery_script.plist</strong> and <strong>launchctl load com.user.battery_script.plist</strong>.
If arguments other then default wants need to be set, just modify the plist file adding the needed parameter and value (as you would in the command line)
in the <key>ProgramArguments<key> section, inside the <array></array> section. For example, adding the tag <string>-b 30</string> will execute the script
with a battery threshold level of 30% instead of 20%.

In order to stop script from executing automatically, just either remove the plist file from the directory or type <strong>launchctl stop com.user.battery_script.plist</strong> and <strong>launchctl unload com.user.battery_script.plist</strong>.
