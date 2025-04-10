HitravaConvert2Garmin
version 0.1
2025-04-03

HitravaConvert2Garmin.py
Structure:
HitravaConvert2Garmin.py
conversion_log.txt
  ConvertedFiles/
  UniqueFiles/

Developed and tested on Python: Python 3.11.4

Main reasons for Hitrava converted files not being able to import directly to Garmin Connect:

1. Missing correct header declarations
2. Activity names
3. Timeformat issues
4. If missing heartratebpm at every trackpoint, the heartrate graph will not be shown correctly

1. Missing correct header declarations
Hitrava: (import to garmin with this info does not work)
<?xml version="1.0"?>
<TrainingCenterDatabase
 xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"    xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
 xmlns:xsd="http://www.w3.org/2001/XMLSchema"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2">

Garmin Connect: (this is according to Garmin TCX schema and is OK to import with)
<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase
  xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
  xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1"
  xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2"
  xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2"
  xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1">
  
2. Activity names
Seems like Garmin Connect needs to have the activities in Capital starting letter.
Activities will be imported, but classified as "other" and not the actual activity
Not "OK":
<Activity Sport="biking">
OK:
<Activity Sport="Biking">

3. Timezone issues
Garmin will not import activities with a timeformat other than:
2025-03-28T15:22:38.000Z

What the script does:
1. Identify the unique files for each activity (the ones I have tested with, had 3 identical files for each activity, dont know why)
2. Copy the unique files to a folder (UniqueFiles)
3. Analyzes the files and does the following:
3.1. Replaced the header with correct information according to Garmin Schema
3.2. Corrects the timeformat and adjusts according to timezone
example:
From: 2025-01-08T16:54:38.000+0100
To: 2025-01-08T15:54:38.000z
3.3. Adds missing HeartRateBMP if missing from a Trackpoint(if missing, the script copies the latest value)
Also related to the HeartRate-graph in Garmin Connect, i added one extension, since this is believed to be present for the graph to be created.
<Extensions>
	<ns3:TPX/>
</Extensions>

Based on filenaming:
Hitrack_YYYYMMDD_HHMMSS_ID.tcx
Example:
HiTrack_20190520_010556_001.tcx

To run application: (in the same directory as the Hitrava export files are located)
python HitravaConvert2Garmin.py

Make sure to have 2 subfolders:
ConvertedFiles
UniqueFiles
