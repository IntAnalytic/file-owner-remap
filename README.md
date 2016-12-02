# file-owner-remap
Change the owner and group member for files and folders in a directory tree. These changes are based on the user ID and group ID and mapped through a provided set of csv files. This utility is useful for tasks such as moving a folder to a new server where ID's need to be migrated from a local auth store to an AD store. Another example might be migration from a lower environments to upper environments where the user and or group id's are different.

## Tested with:
* Python 2.7
* Linux 6 and 7

## Running it
* To see the documentation
  * `python chownmap.py -h`
* Sample command line to recursive map a path using a user and group csv
  * `python chownmap.py -r -path /tmp/testauth -usrmap /tmp/users_t1.csv -grpmap /tmp/groups_t1.csv -dp`

## Parameters
| Command | Parm       | Notes                        |
| ---------- | ---------- |:---------------------------- |
| -v | | Print version of this utility
| -r | | Recursive processing into sub folders, leave this out and it will only process the level requested |
| -path | folder | Relative or absolute path to a folder to process changes against
| -usrmap | csvfile | The csv file used to map users, can be xls saved to .csv for example
| -grpmap | csvfile | The csv file used to map groups
| -dp | | "debug print" : will only print what it will do instead of doing it
| -dt | | "debug run" : will skip the chown and just print any errors like file permissions or missing user/group id's.

Test in a small folder you own. It will likely require root privileges to work properly as it needs rights to change ownership and groups. If you run it under your account in debug mode you'll get reports just like running with root as long as you have read access.

##File format for map csv files:
###Group file format
* Columns 1/2/3 can be any legal name and value for documentation, they are ignored
* Columns 4/5 must contain OLD/NEW as supplied, these are used in the script

Example File

        Server,Local Group,New AD Group,OLD,NEW
        my old server,oldgroup1,newgroup1,10005,100000123
        my old server,oldgroup2,newgroup2,1003,100000125

###User file format
* Columns 1/2 can be any legal name and value for documentation, they are ignored
* Columns 3/4 must contain OLD PID/NEW PID as supplied, these are used in the script

Example File

        Login,Name,OLD PID,NEW PID
        oldUser1,newUser1,11234,115655555
        John Doe,John Doe,11235,115656655
