#!/usr/bin/env python

#import addons_xml_generator as generate
import os
import shutil
import time
import subprocess

import glob
import zipfile
import xml.etree.ElementTree as ET

def zipdir(path, zip):
    for root, dirs, files in os.walk(path):
        for file in files:
            zip.write(os.path.join(root, file))

def buildrepo(f):
    print "Checking for location: "+f
    #folder
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
	print "Not Found! Creating: "+d

print "-----------------------------------------------------------------------------"
print "------------------------------------START------------------------------------"
print "-----------------------------------------------------------------------------"

# MOVED DIRECTORY TO build script:  subprocess.Popen("./addons_xml_generator.py", shell=True, close_fds=True))
addonxml      = "./addons.xml"
addonxmlmd5   = "./addons.xml.md5"

for x in os.listdir('./'):
    if (os.path.isfile(x)) or ('.git' in x):
        #print("SKIPPING: "+x)
        pass
    else: 
        print("Add-on Found: "+x)
        #### Make VARS:
        dest_dir = "../repo/"+x+"/"
	tree = ET.parse('./'+x+'/addon.xml')
	root = tree.getroot()
	version = root.get('version')
        if x[:4]!='repo': #skip repo version
            addonVersion = version
        else:
            repoVersion = version
        print "Version: "+version
        #### DO:
	buildrepo(dest_dir+"*")
        for file in glob.glob('./'+x+'/*changelog.txt'):
            print 'Copying: '+file+' >>>> '+dest_dir+'changelog-'+version+'.txt'
            shutil.copy(file, dest_dir+'changelog-'+version+'.txt')
        for file in glob.glob('./'+x+'/*icon.*'):
            print 'Copying: '+file+' >>>> '+dest_dir+'icon.png'
            shutil.copy(file, dest_dir)
        for file in glob.glob('./'+x+'/*fanart.*'):
            print 'Copying: '+file+' >>>> '+dest_dir+'fanart.jpg'
            shutil.copy(file, dest_dir)
        print("Compressing "+x+'-'+version+'.zip...')
        zipf = zipfile.ZipFile('../repo/'+x+'/'+x+'-'+version+'.zip', 'w', zipfile.ZIP_DEFLATED)
        zipdir(x, zipf)
        zipf.close()
        print("Making copy of "+x+'-'+version+'.zip in Downloads DIR...')
        shutil.copy('../repo/'+x+'/'+x+'-'+version+'.zip', "../downloads/")
        print("Add-on '"+x+"' Successfully Processed")
        print("")

shutil.copy(addonxml, "../repo/")
shutil.copy(addonxmlmd5, "../repo/")

#add addonVersion numbers to Readme.md
print('Update addon links in "downloads/README.md": ' + addonVersion)
newreadme = "sed -i -e 's:frodo-.\..\..\.zip:frodo-'"+addonVersion+"'.zip:g' -e 's:gotham-.\..\..\.zip:gotham-'"+addonVersion+"'.zip:g' -e 's:streams-.\..\..\.zip:streams-'"+repoVersion+"'.zip:g' ../downloads/README.md"
subprocess.Popen(newreadme, shell=True, close_fds=True)
print('Update addon links in "/README.md": ' + addonVersion)
newreadme = "sed -i -e 's:frodo-.\..\..\.zip:frodo-'"+addonVersion+"'.zip:g' -e 's:gotham-.\..\..\.zip:gotham-'"+addonVersion+"'.zip:g' -e 's:streams-.\..\..\.zip:streams-'"+repoVersion+"'.zip:g' ../README.md"
subprocess.Popen(newreadme, shell=True, close_fds=True)


print "---------------------------------------------------------------------------"
print "------------------------------------END------------------------------------"
print "---------------------------------------------------------------------------"

