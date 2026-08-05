import numpy as np 
from astropy.coordinates import SkyCoord
import os 
from subprocess import getoutput 
import wget 
import sys 
import requests
import shutil

# 获取当前脚本所在目录，支持可移植部署
LIB_DIR = os.path.dirname(os.path.abspath(__file__))
if LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

# 本地模块导入
from astronames import to_dmshms
from NVSS_cutout import dl_NVSS_cutout
import dataselection as ds 

# VLASS cutouts (可选依赖)
try:
    import get_VLASS_cutouts as gvlass
except ImportError:
    gvlass = None
    print("Note: get_VLASS_cutouts not found. VLASS download will be disabled.")
    print("Install from: https://github.com/ygordon/VLASS_cutouts")
    print("Then put the get_VLASS_cutouts.py in the same directory as DLtools.py")

import astropy.units as u 
from astroquery.image_cutouts.first import First 
from bs4 import BeautifulSoup
from astroquery.casda import Casda
import pyvo as vo
import re 
from astropy.table import Table
'''
DL code sum up.
'''
# CASDA 实例（延迟初始化，需要时再登录）
casda = None

def _get_casda(username=None, password=None):
    """
    获取 CASDA 实例并登录（支持参数、环境变量或 keyring）。

    登录凭据优先级：
    1. 函数参数 username/password
    2. 环境变量 CASDA_USERNAME / CASDA_PASSWORD
    3. 若未提供 username，则返回匿名实例（仅访问公开数据）
    """
    global casda
    if casda is None:
        casda = Casda()

    # 优先级：函数参数 > 环境变量
    if username is None:
        username = os.environ.get('CASDA_USERNAME')
    if password is None:
        password = os.environ.get('CASDA_PASSWORD')

    if not username:
        return casda

    # 若已以相同凭据登录，直接复用
    current_auth = getattr(casda, '_auth', None)
    if current_auth and current_auth[0] == username and current_auth[1] == password:
        return casda

    # 未提供密码时，尝试 login()（使用 keyring 或交互式输入）
    if not password:
        print(f'  CASDA username provided: {username}. Attempting login...')
        try:
            casda._authenticated = casda.login(username=username)
        except Exception as e:
            raise RuntimeError(f'CASDA login failed for {username}: {e}')
        if not casda._authenticated:
            raise RuntimeError(f'CASDA login failed for {username}.')
        print(f'  CASDA login successful as {username}.')
        return casda

    # 提供用户名+密码，直接验证并设置认证信息
    auth = (username, password)
    try:
        r = requests.get(casda._login_url, auth=auth, timeout=casda.TIMEOUT)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f'CASDA login request failed: {e}')
    if r.status_code != 200:
        raise RuntimeError(f'CASDA login failed for {username} (HTTP {r.status_code}).')

    casda._auth = auth
    casda._authenticated = True
    casda.USERNAME = username
    print(f'  CASDA login successful as {username}.')
    return casda

class img_download():
    """
    Astronomical image downloader for multiple sky surveys.
    
    This class provides unified interfaces to download FITS/image cutouts 
    from various astronomical surveys including VLASS, FIRST, TGSS, etc.
    
    Attributes
    ----------
    ra : float
        Right Ascension in decimal degrees
    dec : float
        Declination in decimal degrees
    size : float
        Cutout size in arcseconds -- NOT radius!
    downloader : list
        List of successfully downloaded survey names
    outfiles : list
        List of output file paths
    position : SkyCoord
        Astropy SkyCoord object of the target position
    """

    def __init__(self,ra,dec,size_in_arcsec=90):
        """
        Initialize the image downloader with target coordinates.
        
        Parameters
        ----------
        ra : float
            Right Ascension in decimal degrees (0-360)
        dec : float
            Declination in decimal degrees (-90 to 90)
        size_in_arcsec : float, optional
            Cutout size in arcseconds (default: 90)
        """
        self.ra = ra 
        self.dec = dec
        self.size = size_in_arcsec
        self.downloader = []
        self.outfiles = []
        self.position = SkyCoord(self.ra,self.dec,unit='deg')
    
    def lotss_img(self,out='lotss.fits',low=False,dr=2):

        """
        Download LOFAR Two-metre Sky Survey (LoTSS) image.
        
        Parameters
        ----------
        out : str, optional
            Output filename (default: 'lotss.fits')
        low : bool, optional
            If True, uses low-resolution data (default: False)
        dr : int, optional
            Data release version (default: 2)
            
        Returns
        -------
        None
            Downloads file and appends to self.outfiles

        Notes: Adjusted from Martin's cutout code. See: https://github.com/mhardcastle/lotss-cutout-api
        """
       
        pos = to_dmshms(self.ra,self.dec)
        size_in_arcmin = self.size/60. 
        url='https://lofar-surveys.org/'
        if low:
            page='dr%i-low-cutout.fits'%dr
        else:
            page='dr%i-cutout.fits'%dr
        r=requests.get(url+page,params={'pos':pos,'size':size_in_arcmin},auth=('surveys','150megahertz'))
        with open(out,'wb') as o:
            o.write(r.content)
            self.outfiles.append(out)
            if low:
                self.downloader.append('LoTSS-Low')
            else:
                self.downloader.append('LoTSS')
        r.close()
        
    def _download_ls_hips2fits(self, out, pixscale, bands, release):
        """
        Download Legacy Survey image via CDS HiPS2FITS as fallback.
        
        Downloads individual band images and combines them into a single
        multi-extension FITS (MEF) file, or a color JPG.
        """
        from astropy.io import fits
        import time
        
        HIPS2FITS_URL = "https://alasky.u-strasbg.fr/hips-image-services/hips2fits"
        hips = "CDS/P/DESI-Legacy-Surveys/DR%i" % release
        
        size_pix = int(self.size / pixscale)
        fov_deg = self.size / 3600.0
        
        is_fits = out.split('.')[-1].lower() == 'fits'
        
        if is_fits:
            tmpdir = os.path.join(os.path.dirname(os.path.abspath(out)) or '.',
                                  '_hips2fits_tmp_%d' % int(time.time()))
            os.makedirs(tmpdir, exist_ok=True)
            try:
                band_paths = {}
                for band in bands:
                    params = {
                        'hips': f'{hips}/{band}',
                        'ra': f'{self.ra:.6f}',
                        'dec': f'{self.dec:.6f}',
                        'width': size_pix,
                        'height': size_pix,
                        'fov': f'{fov_deg:.7f}',
                        'projection': 'TAN',
                        'format': 'fits',
                    }
                    band_out = os.path.join(tmpdir, f'cut_{band}.fits')
                    r = requests.get(HIPS2FITS_URL, params=params, timeout=300)
                    r.raise_for_status()
                    with open(band_out, 'wb') as f:
                        f.write(r.content)
                    band_paths[band] = band_out
                
                # Combine into MEF
                hdus = [fits.PrimaryHDU()]
                ph = hdus[0].header
                ph['SURVEY'] = ('DESI Legacy Surveys', 'Imaging survey name')
                ph['RELEASE'] = (release, 'Data release')
                ph['RA'] = (self.ra, '[deg] Cutout center RA (ICRS)')
                ph['DEC'] = (self.dec, '[deg] Cutout center Dec (ICRS)')
                ph['SIZE'] = (self.size, '[arcsec] Cutout side length')
                ph['PIXSCALE'] = (pixscale, '[arcsec/pixel] Requested pixel scale')
                ph['BANDS'] = (bands, 'Photometric bands included')
                ph['SOURCE'] = (f'CDS HiPS2FITS / {hips}', 'Data provenance')
                
                for band, path in band_paths.items():
                    with fits.open(path) as h:
                        data = h[0].data
                        hdr = h[0].header.copy()
                    ext = fits.ImageHDU(data=data, header=hdr, name=band.upper())
                    ext.header['EXTNAME'] = (band.upper(), f'{band}-band image')
                    ext.header['BAND'] = (band, 'Photometric band')
                    ext.header['BUNIT'] = ('nanomaggy', 'Flux unit (as in LS coadds)')
                    hdus.append(ext)
                
                fits.HDUList(hdus).writeto(out, overwrite=True)
                print(f'[LS] HiPS2FITS fallback: saved MEF to {out}')
            finally:
                shutil.rmtree(tmpdir, ignore_errors=True)
        else:
            # Download color JPG
            params = {
                'hips': f'{hips}/color',
                'ra': f'{self.ra:.6f}',
                'dec': f'{self.dec:.6f}',
                'width': size_pix,
                'height': size_pix,
                'fov': f'{fov_deg:.7f}',
                'projection': 'TAN',
                'coordsys': 'icrs',
                'rotation': 0,
                'format': 'jpg',
            }
            r = requests.get(HIPS2FITS_URL, params=params, timeout=300)
            r.raise_for_status()
            with open(out, 'wb') as f:
                f.write(r.content)
            print(f'[LS] HiPS2FITS fallback: saved JPG to {out}')

    def LS_img(self,out='LS.fits',pixscale=0.3,bands='grz',release=10):
        """
        Download Legacy Survey (LS) optical image.
        
        Parameters
        ----------
        out : str, optional
            Output filename (default: 'LS.fits')
        pixscale : float, optional
            Pixel scale in arcsec/pixel (default: 0.3)
        bands : str, optional
            Filter bands to download (e.g. 'grz', 'i') (default: 'grz')
        release : int, optional
            Data release version (default: 10)
            
        Notes
        -----
        Uses Legacy Survey DR10 by default. Supported bands depend on release.
        If the direct legacysurvey.org download fails, falls back to the
        CDS HiPS2FITS service (DESI Legacy Surveys HiPS).
        """
        size_pix = int(self.size/pixscale)
        if out.split('.')[-1] == 'fits':
            url = 'https://www.legacysurvey.org/viewer/fits-cutout?ra=%f&dec=%f&pixscale=%.1f&layer=ls-dr%i&size=%i&bands=%s'%(self.ra,self.dec,pixscale,release,size_pix,bands)
        else:
            url = 'https://www.legacysurvey.org/viewer/cutout.jpg?ra=%f&dec=%f&pixscale=%.1f&layer=ls-dr%i&size=%i'%(self.ra,self.dec,pixscale,release,size_pix)
        downloaded = False
        try:
            wget.download(url,out=out)
            downloaded = True
        except Exception as e:
            print(f'[LS] Direct legacysurvey.org download failed: {e}')
            print(f'[LS] Falling back to CDS HiPS2FITS...')
            try:
                self._download_ls_hips2fits(out, pixscale, bands, release)
                downloaded = True
            except Exception as e2:
                print(f'[LS] HiPS2FITS fallback also failed: {e2}')
        if downloaded:
            self.outfiles.append(out)
            self.downloader.append('LS')

    def VLASS_img(self,outdir='./',epoch=1,image_type='ql',out='vlass.fits',overwrite_existing=True):
        """
        Download VLA Sky Survey (VLASS) radio image.
        
        Parameters
        ----------
        outdir : str, optional
            Output directory (default: './')
        epoch : int, optional
            Observation epoch (1, 2, or 3) (default: 1)
        image_type: str, optional
            Image type (ql, se) (default: 'ql')
        out : str, optional
            Output filename (default: 'vlass.fits')
        overwrite_existing : bool, optional
            Overwrite if file exists (default: True)
            
        """
        if gvlass is None:
            print('VLASS download requires get_VLASS_cutouts module.')
            print('Install from: https://github.com/ygordon/VLASS_cutouts')
            return
            
        pos = SkyCoord(self.ra,self.dec,unit='deg')
        try:
            print('[VLASS] Connecting to CADC for VLASS cutout query...')
            print(f'  Position: {pos.to_string("hmsdms", sep=" ")}')
            print(f'  Cutout size: {self.size} arcsec')
            print(f'  Epoch: {epoch}, Image type: {image_type}')
            print(f'  Output: {os.path.join(outdir, out)}')
            gvlass.download_cutouts(pos,self.size*u.arcsec,outdir=outdir,epoch=epoch,image_type=image_type,filename=out,overwrite_existing=overwrite_existing)
            self.outfiles.append(os.path.join(outdir,out))
            self.downloader.append('VLASS%i'%epoch)
            print(f'[VLASS] Download completed successfully.')
        except requests.exceptions.ConnectionError as e:
            print(f'[VLASS Error] Cannot connect to CADC server.')
            print(f'  Detail: {e}')
            print(f'  Tip: Check your network connection or try again later.')
            print(f'  CADC service status: https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/')
        except requests.exceptions.Timeout as e:
            print(f'[VLASS Error] Connection to CADC timed out.')
            print(f'  Detail: {e}')
            print(f'  Tip: The server may be busy, try a smaller cutout size or retry later.')
        except Exception as e:
            import traceback
            print(f'[VLASS Error] {type(e).__name__}: {e}')
            traceback.print_exc()
            print(f'  Tip: Check if the target coordinates are covered by VLASS (Dec > -40 deg).')
    
    def NVSS_img(self,out='NVSS.fits'):
        """
        Download NRAO VLA Sky Survey (NVSS) 1.4 GHz image.
        
        Parameters
        ----------
        out : str, optional
            Output filename (default: 'NVSS.fits')
            
        Notes
        -----
        Resolution is ~45 arcsec. Uses NVSS cutout service.
        
        Note: Adjusted from Jackieyma's Automatic-NVSS-cutout
        """
        dl_NVSS_cutout(self.ra,self.dec,size_in_degree=self.size/3600,output=out)
        self.outfiles.append(out)
        self.downloader.append('NVSS')

    def FIRST_img(self,out='FIRST.fits'):
        """
        Download Faint Images of the Radio Sky (FIRST) survey image.
        
        Parameters
        ----------
        out : str, optional
            Output filename (default: 'FIRST.fits')
            
        Notes
        -----
        Resolution is ~5 arcsec. Uses astroquery interface.
        """
        size = self.size*u.arcsec
        try:
            img_first = First.get_images(self.position,image_size=size)
        except:
            img_first = None 
            print('FIRST img not found.')
        if img_first:
            img_first[0].writeto(out,overwrite=True,output_verify='ignore')
            self.outfiles.append(out)
            self.downloader.append('FIRST')

    def SDSS_img(self,out='SDSS.fits',pixscale=0.3,bands='grz'):
        """
        Download Sloan Digital Sky Survey (SDSS) optical image.
        
        Parameters
        ----------
        out : str, optional
            Output filename (default: 'SDSS.fits')
        pixscale : float, optional
            Pixel scale in arcsec/pixel (default: 0.3)
        bands : str, optional
            Filter bands (e.g. 'ugriz' combinations) (default: 'grz')
        """
        size_pix = int(self.size/pixscale)
        if out.split('.')[-1] == 'fits':
            url = 'https://www.legacysurvey.org/viewer/fits-cutout?ra=%f&dec=%f&pixscale=%.1f&layer=sdss&size=%i&bands=%s'%(self.ra,self.dec,pixscale,size_pix,bands)
        else:
            url = 'https://www.legacysurvey.org/viewer/cutout.jpg?ra=%f&dec=%f&pixscale=%.1f&layer=sdss&size=%i'%(self.ra,self.dec,pixscale,size_pix)
        try:
            wget.download(url,out=out)
            self.outfiles.append(out)
            self.downloader.append('SDSS')
        except:
            print('SDSS img download error.')

    def SMSS_img(self,out='SMSS.fits',band='g'):
        """
        Download SkyMapper Surveys (SMSS) optical image.

        Parameters
        ----------------------
        out : str, optional
            Output filename (default: 'SMSS.fits')
        bands : str, optional
            Filter bands (e.g. 'ugriz' combinations) (default: 'grz')
        """
        base_url = 'https://api.skymapper.nci.org.au/public/siap/dr4/query?'
        _band = ','.join(list(band)) # insert comma between bands
        getoutput('rm tmpSMSS*.csv')
        try:
            parms = f'POS={self.ra},{self.dec}&SIZE={self.size/3600}&BAND={_band}&FORMAT=image/fits&RESPONSEFORMAT=CSV&INTERSECT=COVERS'
            url = base_url + parms
            wget.download(url,out='tmpSMSS.csv')
            _tab = Table.read('tmpSMSS.csv')
            _imgurl = _tab['get_image'][0]
            print(_imgurl)
            getoutput('rm tmpSMSS.csv')
            wget.download(_imgurl,out=out)
            self.outfiles.append(out)
            self.downloader.append('SMSS')
        except:
            getoutput('rm tmpSMSS*.csv')
            try:
                parms = f'POS={self.ra},{self.dec}&SIZE={self.size/3600}&BAND={_band}&FORMAT=image/fits&RESPONSEFORMAT=CSV&INTERSECT=CENTER'
                url = base_url + parms
                wget.download(url,out='tmpSMSS.csv')
                _tab = Table.read('tmpSMSS.csv')
                _imgurl = _tab['get_image'][0]
                print(_imgurl)
                getoutput('rm tmpSMSS.csv')
                wget.download(_imgurl,out=out)
                self.outfiles.append(out)
                self.downloader.append('SMSS')
            except:
                print('SMSS img download error.')


    def VLBI_img(self,jname,band,out='VLBI.fits'):
        """
        Download VLBI image from Astrogeo database.
        
        Parameters
        ----------
        jname : str
            Source J2000 name (e.g. 'J123456+654321')
        band : str
            Observing band (e.g. 'L', 'C', 'X', 'K')
        out : str, optional
            Output filename (default: 'VLBI.fits')
            
        Notes
        -----
        Currently supports name-based search only. Uses astrogeo.org service.
        """
        base_url = 'http://astrogeo.org/'
        search_url = base_url + 'cgi-bin/imdb_get_source.csh'
        search_query = jname  # 替换为实际的天体名字
        # 构建查询参数
        params = {
            'source_name': search_query  # 根据HTML内容，表单字段名为'source_name'
        }

        # 发送GET请求
        response = requests.get(search_url, params=params)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text,'html.parser')
            hlinks = soup.find_all('a',href=True)
            pattern = r'/images/.*'+band+r'.*map.fits' 
            for i in range(len(hlinks)):
                _m = re.findall(pattern, hlinks[i]['href'])
                if len(_m)>0:
                    fitsurl = base_url+_m[0]
                    wget.download(fitsurl,out=out)
                    self.outfiles.append(out)
                    self.downloader.append('VLBI')
                    break

    def RACS_img(self,band='Low',poltype='i',out_dir='RACS',out=None,username=None,password=None):
        """
        Download Rapid ASKAP Continuum Survey (RACS) image.
        
        Parameters
        ----------
        band : str, optional
            Frequency band ('Low', 'Mid', or 'High') (default: 'Low')
        poltype : str, optional
            Polarization type ('i', 'q', 'u', 'v') (default: 'i')
        out_dir : str, optional
            Output directory (default: 'RACS')
        out : str, optional
            Output filename. If given, the downloaded image is renamed to this
            name inside ``out_dir`` (or to the full path if ``out`` contains a
            directory component). If None, the original CASDA filename is kept.
        username : str, optional
            CASDA username (default: read from CASDA_USERNAME env var)
        password : str, optional
            CASDA password (default: read from CASDA_PASSWORD env var)
            
        Notes
        -----
        Requires CASDA authentication. Band frequencies:
        - Low: 887 MHz
        - Mid: 1.3 GHz
        - High: 1.7 GHz
        """
        try:
            print(f'[RACS-{band}] Step 1/5: Initializing CASDA connection...')
            _casda = _get_casda(username=username,password=password)
            print(f'[RACS-{band}]   CASDA ready.')

            print(f'[RACS-{band}] Step 2/5: Querying CASDA for images near {self.position.to_string("hmsdms", sep=" ")}...')
            print(f'[RACS-{band}]   Search radius: {0.5*self.size}" arcsec')
            result = Casda.query_region(self.position,radius=0.5*self.size*u.arcsec)
            print(f'[RACS-{band}]   Found {len(result)} total records.')

            print(f'[RACS-{band}] Step 3/5: Filtering unreleased data...')
            public_data = Casda.filter_out_unreleased(result)
            print(f'[RACS-{band}]   {len(public_data)} public records after filtering.')

            # Find closest image, constrain filename, quality level, frequency, data type
            print(f'[RACS-{band}] Step 4/5: Selecting image (band={band}, pol={poltype}, quality=GOOD)...')

            if band=='Low':
                bandind = ds.find_between(public_data['em_res_power'],887e6,888e6)
            elif band=='Mid':
                bandind = ds.find_between(public_data['em_res_power'],1.3e9,1.4e9)
            elif band=='High':
                bandind = ds.find_between(public_data['em_res_power'],1.6e9,1.7e9)
            racsfile = ds.find_str(public_data['filename'],'RACS')
            image = ds.find_str(public_data['filename'],'image.%s'%poltype)
            imagetype = ds.find_str(public_data['filename'],'taylor.0.restored')
            quality = ds.find_str(public_data['quality_level'],'GOOD')
            fin_ind = ds.intersectND([bandind,racsfile,image,imagetype,quality])

            if len(fin_ind)>0:
                selected_file = public_data[fin_ind[0]]['filename']
                print(f'[RACS-{band}]   Matched: {selected_file}')
                print(f'[RACS-{band}] Step 5/5: Requesting cutout and downloading...')
                url = _casda.cutout(public_data[fin_ind][:1],coordinates=self.position,radius=0.5*self.size*u.arcsec)
                os.makedirs(out_dir, exist_ok=True)
                filelist = _casda.download_files(url,savedir=out_dir)
                downloaded_file = filelist[0]
                if out is not None:
                    if os.path.dirname(out) == '':
                        target_path = os.path.join(out_dir, out)
                    else:
                        target_path = out
                    os.makedirs(os.path.dirname(os.path.abspath(target_path)) or '.', exist_ok=True)
                    shutil.move(downloaded_file, target_path)
                    downloaded_file = target_path
                self.outfiles.append(downloaded_file)
                self.downloader.append('RACS-%s'%band)
                print(f'[RACS-{band}] Download completed: {downloaded_file}')
            else:
                print(f'[RACS-{band}] No matching image found.')
                print(f'[RACS-{band}]   Candidates after each filter:')
                print(f'[RACS-{band}]     Band ({band}): {len(bandind)} records')
                print(f'[RACS-{band}]     RACS: {len(racsfile)} records')
                print(f'[RACS-{band}]     Polarization (image.{poltype}): {len(image)} records')
                print(f'[RACS-{band}]     Image type (taylor.0.restored): {len(imagetype)} records')
                print(f'[RACS-{band}]     Quality (GOOD): {len(quality)} records')
        except requests.exceptions.ConnectionError as e:
            print(f'[RACS-{band} Error] Cannot connect to CASDA server.')
            print(f'  Detail: {e}')
            print(f'  Tip: Check your network connection or try again later.')
        except Exception as e:
            import traceback
            print(f'[RACS-{band} Error] {type(e).__name__}: {e}')
            traceback.print_exc()
        
    def EMU_img(self,poltype='i',out_dir='EMU',out=None,username=None,password=None):
        """
        Download Evolutionary Map of the Universe (EMU) survey image.
        
        Parameters
        ----------
        poltype : str, optional
            Polarization type ('i', 'q', 'u', 'v') (default: 'i')
        out_dir : str, optional
            Output directory (default: 'EMU')
        out : str, optional
            Output filename. If given, the downloaded image is renamed to this
            name inside ``out_dir`` (or to the full path if ``out`` contains a
            directory component). If None, the original CASDA filename is kept.
        username : str, optional
            CASDA username (default: read from CASDA_USERNAME env var)
        password : str, optional
            CASDA password (default: read from CASDA_PASSWORD env var)
            
        Notes
        -----
        EMU is an ASKAP all-sky continuum survey at 1.3 GHz.
        """
        try:
            print(f'[EMU] Step 1/5: Initializing CASDA connection...')
            _casda = _get_casda(username=username,password=password)
            print(f'[EMU]   CASDA ready.')

            print(f'[EMU] Step 2/5: Querying CASDA for images near {self.position.to_string("hmsdms", sep=" ")}...')
            print(f'[EMU]   Search radius: {2*self.size}" arcsec')
            result = Casda.query_region(self.position,radius=2*self.size*u.arcsec)
            print(f'[EMU]   Found {len(result)} total records.')

            print(f'[EMU] Step 3/5: Filtering unreleased data...')
            public_data = Casda.filter_out_unreleased(result)
            print(f'[EMU]   {len(public_data)} public records after filtering.')

            print(f'[EMU] Step 4/5: Selecting image (pol={poltype}, quality=GOOD)...')
            emufile =  ds.find_str(public_data['filename'],'EMU')
            image = ds.find_str(public_data['filename'],'image.%s'%poltype)
            imagetype = ds.find_str(public_data['filename'],'taylor.0.restored')
            quality = ds.find_str(public_data['quality_level'],'GOOD')
            fin_ind =  ds.intersectND([emufile,image,imagetype,quality])

            if len(fin_ind)>0:
                selected_file = public_data[fin_ind[0]]['filename']
                print(f'[EMU]   Matched: {selected_file}')
                print(f'[EMU] Step 5/5: Requesting cutout and downloading...')
                url = _casda.cutout(public_data[fin_ind][:1],coordinates=self.position,radius=0.5*self.size*u.arcsec)
                os.makedirs(out_dir, exist_ok=True)
                filelist = _casda.download_files(url,savedir=out_dir)
                downloaded_file = filelist[0]
                if out is not None:
                    if os.path.dirname(out) == '':
                        target_path = os.path.join(out_dir, out)
                    else:
                        target_path = out
                    os.makedirs(os.path.dirname(os.path.abspath(target_path)) or '.', exist_ok=True)
                    shutil.move(downloaded_file, target_path)
                    downloaded_file = target_path
                self.outfiles.append(downloaded_file)
                self.downloader.append('EMU')
                print(f'[EMU] Download completed: {downloaded_file}')
            else:
                print(f'[EMU] No matching image found.')
                print(f'[EMU]   Candidates after each filter:')
                print(f'[EMU]     EMU: {len(emufile)} records')
                print(f'[EMU]     Polarization (image.{poltype}): {len(image)} records')
                print(f'[EMU]     Image type (taylor.0.restored): {len(imagetype)} records')
                print(f'[EMU]     Quality (GOOD): {len(quality)} records')
        except requests.exceptions.ConnectionError as e:
            print(f'[EMU Error] Cannot connect to CASDA server.')
            print(f'  Detail: {e}')
            print(f'  Tip: Check your network connection or try again later.')
        except Exception as e:
            import traceback
            print(f'[EMU Error] {type(e).__name__}: {e}')
            traceback.print_exc()

    def TGSS_img(self,out='TGSS.fits'):
        """
        Download TIFR GMRT Sky Survey (TGSS) 150 MHz image.
        
        Parameters
        ----------
        out : str, optional
            Output filename (default: 'TGSS.fits')
            
        Notes
        -----
        Resolution is ~25 arcsec. Uses VO SIAP service.
        """
        size_pix = int(self.size/0.3)
        url = 'https://vo.astron.nl/tgssadr/q_fits/cutout/siap.xml'
        ser = vo.sia.SIAService(url)
        result = ser.search(pos=self.position,size=self.size/3600)
        if not result:
            raise ValueError("Requested coordinates not covered by the specified VO!")
        im = result.getrecord(0)
        if im.format == "image/fits":
            print('FITS image found. Downloading...')
            try:
                im.cachedataset(filename=out)
                self.outfiles.append(out)
                self.downloader.append('TGSS')
            except:
                print('TGSS img download error.')