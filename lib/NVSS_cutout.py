# Adjusted from Jackieyma's Automatic-NVSS-cutout

## Automatically download FITS files from NVSS postage server
## File in format: <Src-Name>\t<RA-h>\t<RA-m>\t<RA-s>\t<DEC-d>\t<DEC-m>\t<DEC-s>\n
## File output will be <Src-Name>.fits
## WARNING! Do not start this script if there are other files named "postage.pl..." in the same directory
## Or they will disappear... :D

import numpy as np
import os
from astropy.coordinates import SkyCoord

## Change settings below
def dl_NVSS_cutout(ra,dec,size_in_degree=0.5,output='tmp.fits'):
    pos = SkyCoord(ra,dec,unit='deg')
    rah,ram,ras = pos.ra.hms.h, pos.ra.hms.m, pos.ra.hms.s 
    ded,dem,des = pos.dec.dms.d, pos.dec.dms.m, pos.dec.dms.s
    if ded>0:
        s = 'string,%02i,%02i,%05.2f,+%02i,%02i,%05.2f'%(rah,ram,ras,ded,dem,des)
    else:
        s = 'string,%02i,%02i,%05.2f,-%02i,%02i,%05.2f'%(rah,ram,ras,-ded,-dem,-des)
    equinox = 'J2000'
    #equinox = 'B1950'

    poltype = 'I'
    #poltype = 'IQU'

    imsize = '%.2f+%.2f'%(size_in_degree,size_in_degree) ## In degrees; use "+" to separate the two values

    pixelsize = '15+15' ## In arcseconds; use "+" to separate the two values

    proj = 'SIN' ## Can be: SIN TAN ARC NCP GLS MER AIT STG

    rotation = '0.0'

    #imtype = 'image/x-fits' ## FITS Image
    imtype = 'application/octet-stream' ## FITS save to disk
    #imtype = 'application/postscript' ## Contour Map
    #imtype='image/jpeg' ## JPEG Image

    #filein = 'my_sources.dat' ## File to read source name, RA, and DEC from
    ## See top of the page to see file format

    fileout = '.fits' ## File extension of output file
    #fileout = '.jpg'

    ## Change settings above
    src = s.split(',')
    #data = np.genfromtxt(filein, dtype='str')
    imtype2 = imtype.split('/')[0]+'%2F'+imtype.split('/')[1] ## Change '/' to '%2F' to rename file in terminal

    #for src in data:
    os.system('wget "http://www.cv.nrao.edu/cgi-bin/postage.pl?Equinox='+equinox+'&PolType='+poltype+'&ObjName=&RA='+src[1]+'+'+src[2]+'+'+src[3]+'&Dec='+src[4]+'+'+src[5]+'+'+src[6]+'&Size='+imsize+'&Cells='+pixelsize+'&MAPROJ='+proj+'&rotate='+rotation+'&Type='+imtype+'" -O '+output)
    #os.system('mv postage.pl\?Equinox='+equinox+'\&PolType='+poltype+'\&ObjName=\&RA='+src[1]+'+'+src[2]+'+'+src[3]+'\&Dec='+src[4]+'+'+src[5]+'+'+src[6]+'\&Size='+imsize+'\&Cells='+pixelsize+'\&MAPROJ='+proj+'\&rotate='+rotation+'\&Type='+imtype2+' '+src[0]+fileout)