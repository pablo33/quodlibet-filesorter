# quodlibet-filesorter
Reorganize your mp3 music collection at the file system based on their id3 tags, managed with quodlibet.  

## Why do I use this script
I manage my mp3 files with quodlibet. It is easy to edit and manage ID3 tags with Quolibet, but I also like to have a structured an ordered mp3 collection on the system folders. So I have to manually edit names or move the files, to do that. This is manually done and it requires a little work or configuration to get done. You can get tags from the path, this is OK, but with this script you can put 'your tags on the path' and in a consistent manner. With this script I easily maintain a coherent file-folder structure for my mp3 music collection based on their id3 tags. So I only care about a correct metadation.  

For example, if I change an artist name, album, or even the name, their tracknumbers, genre, running this script will reorder my mp3 on the filesystem. It will rename or move the mp3 files accordingly. Even more, I use to store jpg images and other kind of files, or folders besides the mp3, with this script, extra folders or files are also moved following the associated mp3s.  

Once the files are moved, Quodlibet can easily follow the file movements by itself, I also can force to rescan the libraries. So everything works fine.  

If you use Quodlibet to manage your music, and set your id3 Tags, this script is for you.  

You can learn more about quodlibet vissiting it's page : <https://quodlibet.readthedocs.io/en/latest/index.html>  

## What does this script do
This script reads Quodlibet config information about where are placed your music libraries.  
It reads Id3 tags from the mp3 files and moves them based on your custom _path expression_ for each file. The _path expression_ is also stored as an id3 tag into the file. This allows you to easily manage everything from quodlibet itself.  

Imagin that you use to store your Music collection a path structure like this: library-path/Albums/name_of_the_album/cdnumber/tracknumber - title.mp3  

This is the expression you have to use: ~/Albums/<album\>/[<discnumber\>/][<tracknumber\> - ]<title\>.<ext\>  

You can easily assign this expression and set it into a bunch of selected files at quodlibet.  

Run this script and your mp3 files will get placed as your defined expression.  

You can afterwards, edit id3 tags... title, album etc...  by running this script the files will be renamed and moved to the corresponding path and with their associated extra files.  

### Dependencies
This script relies on quodlibet custom taggin and 
eyed3 python library

You can install them typing:

    sudo apt-get install quodlibet python3-eyed3

### Aim:
Keep a coherent tree of files only managing tags at quodlibet.  

More info about how to use this script at wiki page <https://github.com/pablo33/quodlibet-filesorter/wiki>  
