#!/usr/bin/env python3

#######################################
## File system gid/uid migration mapper
## By: Afaque Siddiqui
##   : July 6, 2023
#######################################
#Imports
from distutils.log import debug
import os
import csv
import subprocess
from os.path import join, getsize
import argparse


def processGrpAcl(type, item, groupLu, debug):
    proc = subprocess.Popen(["getfacl", "-cEp", item], stdout=subprocess.PIPE)
    output = proc.communicate()[0]
    for line in str(output).split('\\n'):
        if 'group' in line:
            attr = line.split(":")
            for x,y in groupLu.items():
                if attr[1] == x :
                    oacl = "g:" + x + ":" + attr[2]
                    nacl = "g:" + y + ":" + attr[2]
                    if(debug):
                        print("ACL: %s, %s, %s->%s" % (type, item, oacl, nacl))
                    else:
                        pset1 = subprocess.Popen(["setfacl", "-m", nacl, item], stdout=subprocess.PIPE)
                        pset2 = subprocess.Popen(["setfacl", "-x", "g:"+x, item], stdout=subprocess.PIPE)

def processItem(type, item, userLu, groupLu, debug, preview):
    "This manages file or folder ownership changes or prints what its doing or problems encountered"
    problem = False
    lstat = ()
    newUid = -1
    newGid = -1

    try:
        lstat = os.lstat(item)
    except IOError as e:
        if e.errno == errno.EACCES:
            problem = True
            print("ERROR_OS: changing ownership of %s : %s ->%s" % (type, item, e.strerror))
        #more critical failure, raise and bubble up
        raise

    #Pull User map
    try:
        newUid = int(userLu[str(lstat.st_uid)])
    except KeyError:
        print("map user miss, %s, %s, %s" % (lstat.st_uid, type, item))

    #Pull Group map
    try:
        newGid = int(groupLu[str(lstat.st_gid)])
    except KeyError:
        print("map group miss, %s, %s, %s" % (lstat.st_gid, type, item))

    #Process the change based on the debugging flags
    if (newUid >= 0 or newGid >= 0):
        try:
            if (debug):
                print("%s, %s, uid:%s->%s,gid:%s->%s" % (type, item, lstat.st_uid, newUid, lstat.st_gid, newGid))
            elif (preview == False):
                os.lchown(item, newUid, newGid)
        except IOError as e:
            if e.errno == errno.EACCES:
                print("ERROR_OS: Changing ownership of %s:%s ->%s" % (type, item, e.strerror))
            #more critical failure, raise and bubble up
            raise
    return;

def main():
    parser = argparse.ArgumentParser(
        description="Run chown mapping user:group. Does not follow symlinks.")

    parser.add_argument('-path', required=True, help='root folder to start')
    parser.add_argument('-usrmap', required=True, metavar='{usrmap}.csv', help='User Map file')
    parser.add_argument('-grpmap', required=True, metavar='{grpmap}.csv', help='Group Map file')
    parser.add_argument('-v', action='version', version='%(progs)s 1.0.0')
    parser.add_argument('-r', action='store_true', dest='recur', help='Recursive folder operation, does not follow symlinks')
    parser.add_argument('-dp', action='store_true', dest='debugPrint', help='Debug support, "prints" action instead of running chmod')
    parser.add_argument('-dt', action='store_true', dest='debugTest', help='Debug support, no chown only printing errors')

    args = parser.parse_args();

    #test
    #args = parser.parse_args(['-h'])
    #args = parser.parse_args('-r -path /tmp/testauth -usrmap /tmp/users_t1.csv -grpmap /tmp/groups_t1.csv -dp'.split())

    if not args.path:
        quit()

    #Driving params
    toplvl = args.path
    userFile = args.usrmap
    groupFile = args.grpmap

    #Globals
    debugPreview=args.debugPrint
    testLookup=args.debugTest
    recur=args.recur
    userLookup = {}
    groupLookup = {}
    files=os.listdir(toplvl)

    print("Processing top level of '%s'" % toplvl)
    print("  Using user  map:'%s'" % userFile)
    print("  Using group map:'%s'" % groupFile)
    if (debugPreview):
        print("  NOTE: Printing change proposals instead of running chown")
    if (testLookup):
        print("  NOTE: Running normal flow but not running chown")
    print()

    #Read the users csv
    with open(userFile) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            userLookup[row['OLD PID']] = row['NEW PID']

    #Read the groups csv
    with open(groupFile) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            groupLookup[row['OLD']] = row['NEW']

    for root, dirs, files in os.walk(toplvl):
        for dir in dirs:
            processItem('Folder', join(root,dir), userLookup, groupLookup, debugPreview, testLookup)
            processGrpAcl('Folder', join(root,dir), groupLookup, debugPreview)
        for file in files:
            processItem('File', join(root,file), userLookup, groupLookup, debugPreview, testLookup)
            processGrpAcl('File', join(root,file), groupLookup, debugPreview)
        if (recur == False):
            print("Exiting as recursion was flagged false")
            break;


if __name__ == "__main__":
    main()