# astronames.py
from astropy.coordinates import SkyCoord
import astropy.units as u 

def to_Jname(ra,dec,digits=4):
    '''
    From ra, dec (degrees) to Jxxxx+xxxx names.
    '''
    pos = SkyCoord(ra, dec, unit='deg')
    if digits == 4:
        if pos.dec.dms.d>0:
            posstr = 'J%02i%02i+%02i%02i'%(pos.ra.hms.h,pos.ra.hms.m,pos.dec.dms.d,pos.dec.dms.m)
        else:
            posstr = 'J%02i%02i-%02i%02i'%(pos.ra.hms.h,pos.ra.hms.m,-pos.dec.dms.d,-pos.dec.dms.m)
    else:
        if pos.dec.dms.d>0:
            posstr = 'J%02i%02i%05.2f+%02i%02i%05.2f'%(pos.ra.hms.h,pos.ra.hms.m,pos.ra.hms.s,pos.dec.dms.d,pos.dec.dms.m,pos.dec.dms.s)
        else:
            posstr = 'J%02i%02i%05.2f-%02i%02i%05.2f'%(pos.ra.hms.h,pos.ra.hms.m,pos.ra.hms.s,-pos.dec.dms.d,-pos.dec.dms.m,-pos.dec.dms.s)
    return posstr

def to_dmshms(ra,dec):
    '''
    From ra, dec (degrees) to xx:xx:xx.x +xx:xx:xx.x .
    '''
    pos = SkyCoord(ra, dec, unit='deg')
    digits =6
    if digits == 4:
        if pos.dec.dms.d>0:
            posstr = 'J%02i%02i+%02i%02i'%(pos.ra.hms.h,pos.ra.hms.m,pos.dec.dms.d,pos.dec.dms.m)
        else:
            posstr = 'J%02i%02i-%02i%02i'%(pos.ra.hms.h,pos.ra.hms.m,-pos.dec.dms.d,-pos.dec.dms.m)
    else:
        if pos.dec.dms.d>0:
            posstr = '%02i:%02i:%04.1f +%02i:%02i:%04.1f'%(pos.ra.hms.h,pos.ra.hms.m,pos.ra.hms.s,pos.dec.dms.d,pos.dec.dms.m,pos.dec.dms.s)
        else:
            posstr = '%02i:%02i:%04.1f -%02i:%02i:%01.2f'%(pos.ra.hms.h,pos.ra.hms.m,pos.ra.hms.s,-pos.dec.dms.d,-pos.dec.dms.m,-pos.dec.dms.s)
    return posstr

