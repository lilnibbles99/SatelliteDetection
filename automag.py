#!/usr/bin/env python
#
# To find aperture magitudes for a set of x, y position
#
# Command line inputs:   filename
# File input:            objects.cat
#
# Output:  amag.out
# Output:  line appended to "summary.obs"
#

import pyfits, numarray, math, sys, os, socket, commands

def jmedian(arr):
    tarr=arr[:]
    tarr.sort()
    n = len(tarr)
    if n == 0: return 0.0
    if n == 1: return tarr[0]

    mid = n / 2
    if (n % 2) == 0:
       med = (tarr[mid] + tarr[mid-1])/2
    else:
       med = tarr[mid]
    return med

def robust_stddev(arr):
    n = len(arr)
    if n < 1: return 0.0
    tarr=arr[:]
    tarr.sort()
    q_16 = int(float(n-1)*0.16+0.5)
    q_84 = int(float(n-1)*0.84+0.5)
    return (tarr[q_84] - tarr[q_16])/2.


def find_image_bgd ( nx, ny, image):
    bgd=[]
    for iy in range(0,ny,4):          # restricted positions for speed only
        for ix in range(0, nx, 4):
            pix_value = image[iy,ix]  # note order , i.e. row, coloumn!
            bgd.append(pix_value)
    jmed = jmedian(bgd)
    bgd_rms = robust_stddev(bgd)
    jlow = jmed - 2.*bgd_rms
    jtop = jmed + 2.*bgd_rms
    sum = 0
    nsky = 0
    for i in range(len(bgd)):
        bgd_value = float(bgd[i])
        if bgd_value > jlow and bgd_value < jtop:
           sum = sum + bgd_value
           nsky = nsky + 1
    mean_bgd = float(sum)/float(nsky)
    return (mean_bgd, bgd_rms)


def find_sky ( nx, ny, image, xcen, ycen, radius_1, radius_2):
#
# find counts in sky annulus
#
#    print radius_1, radius_2
    rad_sq1 = radius_1**2
    rad_sq2 = radius_2**2
    ylimit = radius_2 + 2 
    xlimit = radius_2 + 2
    ylow = max(1,int(ycen-ylimit))
    ytop = min(ny,int(ycen+ylimit))
    xlow = max(1,int(xcen-xlimit))
    xtop = min(nx,int(xcen+xlimit))           
#    print "outer:", xlow, xtop, ylow, ytop

    bgd=[]
    for iy in range(ylow,ytop):
        for ix in range(xlow,xtop):
            rsquared= (float(ix)-xcen)**2 + (float(iy)-ycen)**2
            if rsquared > rad_sq1 and rsquared < rad_sq2 :
               pix_value = image[iy,ix]          # note order , i.e. row, column!
               bgd.append(pix_value)

#    print len(bgd)
    jmed = jmedian(bgd)
    bgd_rms = robust_stddev(bgd)
    jlow = jmed - 2.*bgd_rms
    jtop = jmed + 2.*bgd_rms
    sum = 0
    nsky = 0
    for i in range(len(bgd)):
        bgd_value = float(bgd[i])
        if bgd_value > jlow and bgd_value < jtop:
           sum = sum + bgd_value
           nsky = nsky + 1

    mean_bgd = float(sum)/float(nsky)    
    return (nsky, mean_bgd, bgd_rms)


def new_centroid (nx, ny, image, xcen, ycen, bgd):
#
# find an improved(?) centroid
#
    ixcen = int(xcen)
    iycen = int(ycen)
    nhalf = 7
    ylow = max(1,int(iycen-nhalf))
    ytop = min(ny,int(iycen+nhalf))
    xlow = max(1,int(ixcen-nhalf))
    xtop = min(nx,int(ixcen+nhalf))

    sum = 0.0
    xsum = 0.0
    ysum = 0.0
    for ix in range (xlow, xtop):
        for iy in range (ylow, ytop):
            value = image[iy,ix] - bgd
            sum = sum + value**2
            xsum = xsum + float(ix-ixcen)*(value**2)
            ysum = ysum + float(iy-iycen)*(value**2)            
    
    new_xcen = xsum/sum + ixcen + 1.
    new_ycen = ysum/sum + iycen + 1.   
    return (new_xcen, new_ycen)


def find_mag ( nx, ny, image, xcen, ycen, exposed, readout, gain, bgd_rms, radius, constant):
#
# find counts in aperture
#
    saturate = "false"
    rad_sq = radius**2
    ylimit = radius + 2
    xlimit = radius + 2
    ylow = max(1,int(ycen-ylimit))
    ytop = min(ny,int(ycen+ylimit))
    xlow = max(1,int(xcen-xlimit))
    xtop = min(nx,int(xcen+xlimit))           
#   print "inner:", xlow, xtop, ylow, ytop

    peak = 0
    npix = 0
    total = 0
    for iy in range(ylow,ytop):
        for ix in range(xlow,xtop):
            rsquared = (float(ix)-xcen)**2 + (float(iy)-ycen)**2
            if rsquared < rad_sq :
               npix = npix + 1
               pix_value = image[iy,ix]   # note order , i.e. row, coloumn!
               if pix_value >  peak: peak = pix_value
               if pix_value >= 65000: peak = 65000
               total = total + pix_value
#    print npix, total, peak, exposed

    signal = total - float(npix)*mean_bgd
    noise=math.sqrt(signal/gain + npix*bgd_rms**2 + (npix/nsky)*bgd_rms**2 + (readout/gain)**2 )

    if signal > 0.0 :
       mag    = constant - 2.5*math.log10(float(signal)/float(exposed)) 
       magerr = 1.0857*noise/signal
    else:
       mag    = 99.999
       magerr = 99.999

    return (npix, peak, signal, mag, magerr, saturate)


def JulianAstro(day, month, year):
    if month < 3:
        year  = year - 1
        month = month + 12
    julian = int(365.25*year) + int(30.6001*(month+1)) + day + 1720994.5
    tmp = year + month / 100.0 + day / 10000.0
    if tmp >= 1582.1015:
        A = year / 100
        B = 2 - A + A/4
        julian = julian + B
    julian = julian - 2400000.5
    return julian * 1.0

# ---------- main part starts here ------------------

if os.path.exists('automag_driver'):
   driver = open('automag_driver','r')
   while 1:
      line = driver.readline()
      if line == '': break
      word = line.split()
      if word[0] == 'constant': constant = float(word[2])
      if word[0] == 'readout': readout = float(word[2])
      if word[0] == 'gain': gain = float(word[2])
      if word[0] == 'pixscale': pixscale = float(word[2])
      if word[0] == 'radius': radius = float(word[2])
      if word[0] == 'radius_1': radius_1 = float(word[2])
      if word[0] == 'radius_2': radius_2 = float(word[2])
   driver.close()
else:
   constant = 17.0
   readout = 15.0
   gain = 1.6
   pixscale = 1.28
   radius = 8
   radius_1 = 20
   radius_2 = 30

results = open('amag.out','w')
filename = sys.argv[1]
 
results.write(" Results from        : "+filename+"\n")
hdulist=pyfits.open(filename)
head=hdulist[0].header
nx = int(head['NAXIS1'])
ny = int(head['NAXIS2'])
image=hdulist[0].data

tele= head['TELESCOP']
if tele[0:5] == "DRACO":
    exposure = float(head['EXPTIME'])    
    obsdate = head['DATE-OBS']
    day = obsdate[0:2]
    month = obsdate[3:5]
    year = obsdate[6:10]
    utstart = head['UTSTART']
    shour = utstart[0:2]
    smin = utstart[3:5]
    ssec = utstart[6:8]
    hour_start = float(shour) + float(smin)/60.0 + float(ssec)/3600.0
#    utend = head['UTEND']
#    ehour = utend[0:2]
#    emin = utend[3:5]
#    esec = utend[6:8]
#    hour_end = float(ehour) + float(emin)/60.0 + float(esec)/3600.0
#    if hour_start < hour_end:
#        hour_mid = (hour_start + hour_end)/2.0
#    else:
#        hour_mid = (hour_start + hour_end + 24.0)/2.0
    mjd_start = JulianAstro(int(day), int(month), int(year)) + hour_start/24.0
    mjd_mid = "%12.5f" %  ( mjd_start + exposure/(60.0*60.0*24.0*2.0) )
    obstime = head['UTSTART']
else:
    obsdate = head['OBSDATE']
    obstime = head['OBSTIME']
    mjd_mid = "%12.5f" % head['MJD_MID']
    exposure = float(head['EXPOSED'])

results.write(" Image taken on      : "+obsdate+"\n")

results.write(" Image taken at      : "+obstime+"\n")

results.write(" Modified Julian Day : "+str(mjd_mid)+"\n")

exposed = "%6.2f" % exposure
results.write(" Exposure time       : "+exposed+"\n")

ctmp = "%5.2f" % float(pixscale)
results.write(" Scale (arcsec/pix)  :  "+ctmp+"\n")

ctmp = "%6.2f" % float(radius)
results.write(" Radius(arcsec)      : "+ctmp+"\n")
radius = radius/pixscale

ctmp = "%6.2f" % float(radius_1)
results.write(" Sky radius1(arcsec) : "+ctmp+"\n")
radius_1 = radius_1/pixscale

ctmp = "%6.2f" % float(radius_2)
results.write(" Sky radius2(arcsec) : "+ctmp+"\n")
radius_2 = radius_2/pixscale

ctmp = "%6.2f" % constant
results.write(" Adopted constant    : "+ctmp+"\n")

(image_bgd,image_rms) = find_image_bgd(nx,ny,image)

ctmp = "%6.2f" % image_bgd
results.write(" Mean background     : "+ctmp+"\n")

ctmp = "%6.2f" % image_rms
results.write(" Bgd rms scatter     : "+ctmp+"\n")

hdulist.close()


results.write(' obj   n    xcen    ycen   npix   ipeak   bgd      total      mag    err    ra             dec'+'\n')

if not os.path.exists('objects.cat'):
   print "No 'objects.cat' file, running sextractor ..."
   hostname = socket.gethostname()
   print hostname
   if hostname == "capella":
      out=commands.getoutput('/star/bin/extractor/sex -c /home/aa/bin/sex_config/default.sex '+filename)
      print out
   else:
      out=commands.getoutput('/star/bin/extractor/sex -c /remote/aa_bin/sex_config/remote_default.sex '+filename)
      print out

cat = open('objects.cat','r')
istar = 0
var_hit = "no"
cal1_hit = "no"
cal2_hit = "no"
while 1:
    line = cat.readline()
    if line == "":break
    word = line.split()
    if word[0] == "#": continue
    istar = istar + 1
    xcen = float(word[1])
    ycen = float(word[2])
    ra = float(word[7])  ## AMS
    dec = float(word[8]) ## AMS
#    print ra,dec
#    sex_mag = float(word[5])
    (nsky, mean_bgd, bgd_rms) = find_sky ( nx, ny, image, xcen, ycen, radius_1, radius_2)

    (new_xcen, new_ycen) = new_centroid (nx, ny, image, xcen, ycen, mean_bgd)
#    print (xcen - new_xcen), (ycen - new_ycen)

    (npix, peak, signal, mag, magerr, saturate) = find_mag ( nx, ny, image, new_xcen, new_ycen, exposed, readout, gain, bgd_rms, radius, constant)
    
    outline = " star %2d %7.1f %7.1f %6d %7d %6.1f %10.1f %8.3f %6.3f %12.6f %12.6f" % \
              (istar, new_xcen, new_ycen, npix, peak, mean_bgd, signal, mag, magerr, ra, dec)
    if saturate == "true": outline = outline + "  Sat"
    results.write(outline+'\n')

results.close()

