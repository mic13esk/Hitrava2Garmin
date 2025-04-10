## Hitrava2Garmin
  
### Why the need of this?
I had been using Huawei bands and watches for quire some time.
I felt locked down when not being able to view my training activities online, and not being able to export them.
Glanced at Garmin, and when I had some issues with my latest Huawei watch i decided to move to the Garmin ecosystem.

Now came the issue, there was no way of converting Huawei activities to Garmin!
After some googling i found Hitrava that did just that. Almost at least.
With Hitrava I could export all my activities to a format that could be imported to Strava and from there export to a Garmin-readable format.
A lot of converting to do, but it worked.
After converting 1000 activities the work was done.

When a friend of mine wanted to do the exact same journey, I wanted to find a better way to handle this.

### Special thanks to Hitrava!
Without Hitrava I wouldnt have been able to export my Huawei data at all!

### Intro
Hitrava2Garmin changes the Hitrava export so that the activities can be imported into Garmin directly.
No need to import them to Strava first.
Since Strava have currently a 100 activity import / day limit, importing many activities will cost a lot of hours and frustration.

## Table of Contents
- [Introduction](#intro)  
- [Features](#features)
- [Installation](#installation)
- [How2Use](#usage)
- [What the script does](#WhatItDoes)

## Features
Main reasons for Hitrava converted files not being able to import directly to Garmin Connect:

1. Missing correct header declarations
2. Activity names
3. Timeformat issues
4. If missing heartratebpm at every trackpoint, the heartrate graph will not be shown correctly

## Installation
All you need is the Python-script and 2 subdolders.<br>
ConvertedFiles<br>
UniqueFiles<br>
Place the Hitrava files in the same directory as the Python-script<br>
<br>
Based on filenaming:<br>
Hitrack_YYYYMMDD_HHMMSS_ID.tcx<br>
Example:<br>
HiTrack_20190520_010556_001.tcx<br>
Developed and tested on Python: Python 3.11.4

## Usage
To run application: (in the same directory as the Hitrava export files are located)
```
python HitravaConvert2Garmin.py
```

## WhatItDoes
First of all, the script does nothing to the original files.

1. Identifies the unique files (if there are more than 1 file for each activity) and copies the files to subfolder "UniqueFiles"

2. Corrects the header-information in the files<br>
Hitrava: (import to garmin with this info does not work)
```
<?xml version="1.0"?>
<TrainingCenterDatabase
xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"    xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2">
``` 
Garmin Connect: (this is according to Garmin TCX schema and is OK to import with)
```
<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1"
xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2"
xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2"
xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1">
```

3. Updating Activity names<br>
Seems like Garmin Connect needs to have the activities in Capital starting letter.<br>
Activities will be imported, but classified as "other" and not the actual activity<br>
- Not "OK" :
```
<Activity Sport="biking">
```

- OK:
```
<Activity Sport="Biking">
```

4. Correcting timezone issues<br>
Garmin will not import activities with a timeformat other than:<br>
2025-03-28T15:22:38.000Z<br>
example:<br>
From: 2025-01-08T16:54:38.000+0100<br>
To: 2025-01-08T15:54:38.000z<br>

5. Adds missing HeartRateBMPs in every <Trackpoint><br>
Adds missing HeartRateBMP if missing from a Trackpoint(if missing, the script copies the latest value)<br>
Also related to the HeartRate-graph in Garmin Connect, i added one extension, since this is believed to be present for the graph to be created.
```
<Extensions>
	<ns3:TPX/>
</Extensions>
```

Activities are not possible to import to Garmin Connect
