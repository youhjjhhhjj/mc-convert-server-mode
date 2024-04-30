Use this script to convert a minecraft server from online mode to offline mode, or vice versa. Works for self-hosted servers on Linux.

Usage:
1. stop your server
2. install python and dependencies
3. navigate to the root folder of your server
4. run the script `python convert-server.py`
5. edit your server.properties online-mode setting
6. start your server

And now all of your player data (inventory, stats, advancements) should persist after your server has changed mode.

By default it does an online to offline conversion. Pass a command line argument for offline to online.
