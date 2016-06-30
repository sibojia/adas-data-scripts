import gpxpy,os,sys,gpxpy.gpx,datetime
epoch=datetime.datetime(2001,1,1)
fin=open(sys.argv[1]).readlines()
fout=open(sys.argv[2],'w')

gpx = gpxpy.gpx.GPX() 

# Create first track in our GPX: 
gpx_track = gpxpy.gpx.GPXTrack() 
gpx.tracks.append(gpx_track) 

# Create first segment in our GPX track: 
gpx_segment = gpxpy.gpx.GPXTrackSegment() 
gpx_track.segments.append(gpx_segment) 

# Create points:
for line in fin:
	tok=line.split(',')
	if len(tok) == 6:
		gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(float(tok[1]), float(tok[0]), float(tok[2]), datetime.timedelta(seconds=float(tok[-1]))+epoch))
fout.write(gpx.to_xml())
fout.close()
