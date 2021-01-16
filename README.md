# quodlibet-filesorter
Reorganize your mp3 music collection at the file system based on their id3 tags, managed with quodlibet.  

## Why do I use this script
I manage my mp3 files with quodlibet. It is easy to edit and manage ID3 tags Quolibet, but I like to have a structured an ordered mp3 collection on the system folders. So I have to manually edit or move the files, or use software scripting "tags to path" to do that. This is manually done and it requires a little work or configuration to get done. With this script I easily maintain a coherent folder structure for my mp3 music collection based on their id3 tags.  

For example, if I change an artist name, album, or even the name, their tracknumbers, genre, running this script will reorder my mp3 on the filesystem. It will rename or move the mp3 files accordingly. Even more, I use to store jpg images other kind of file, or folders besides the mp3, with this script, extra folders or files are also moved following the associated mp3.  

Quodlibet can easily follow the file movements by itself, I also can force to rescan the libraries. So everithing works fine.  

If you use Quodlibet to manage your music, and set your id3 Tags, this script is for you.  

You can learn more about quodlibet vissiting it's page : <https://quodlibet.readthedocs.io/en/latest/index.html>  

## What does this script does
This script reads Quodlibet config information about where are placed your music libraries.  
It reads Id3 tags from the mp3 files and moves them based on your custom _path expression_ for each file. The _path expression_ is also stored as an id3 tag into the file. This allows you to easily manage it from quodlibet itself.  

Imagin that you use to store your Music collection a path structure as is: library-path/Albums/name_of_the_album/cdnumber/tracknumber - title.mp3  

This is the expression you have to use: ~/Albums/<album\>/[<discnumber\>/][<tracknumber\> - ]<title\>.<ext\>  

You can easily assign this expression an set it into a bunch of selected files at quodlibet.  

Run this script and your mp3 files will get placed as your defined expression.  

You can afterwards, edit id3 tags... title, album etc...  by running this script the files will be renamed and moved to the corresponding path.  

### Dependencies
this script relies on quodlibet
eyed3 python library

you can install them typing:

    sudo apt-get install quodlibet python3-eyed3

### Aim:
Keep a coherent tree of files only managing tags at quodlibet.  

More info about how to use this script at wiki page <https://github.com/pablo33/quodlibet-filesorter/wiki>  
