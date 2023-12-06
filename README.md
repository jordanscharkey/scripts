# Scripts

A collection of various scripts I've created. Below is a list of their function and usage.

## commandhelper

Lists out DWM functional shortcuts for my window manager.

`./commandhelper`

## internet-status

Returns 'Online' or 'Offline' depending on the results of a wget call (may move this to a simple ping in the future).

`./internet-status`

## process-rss

INCOMPLETE: automatically feed a blog post HTML file into my RSS file.

`./process-rss $BLOG_POST.HTML $RSS_FEED.XML`

## random-music

Grabs a random list of songs to feed into an mpv playlist.

TODO: allow directories to be passed in

`./random-music $NUM_OF_SONGS`

## battery-life

Grabs remaining battery life on laptops, using acpi.

`./battery-life`

## adjust-brightness

Changes the brightness value of a screen, intended use being laptops.

TODO: Pass through directory as to not be hardcoded

`./adjust-brightness $+/-`

## backup.py

Creates file copies on another drive and an external server.

TODO: switch this to shell
