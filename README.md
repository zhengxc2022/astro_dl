# Astronomical Image Downloader (Web Interface)

A web-based tool for downloading astronomical images from various surveys.

## Features

- Web interface for easy access
- Multiple surveys supported: LoTSS, Legacy Survey, VLASS, NVSS, FIRST, SDSS, SMSS, VLBI, RACS, EMU, TGSS
- Directory browser for output selection
- Real-time download progress display
- Portable - easy to share with colleagues

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the installer
./install.sh

# Start service (restart terminal first if using alias)
dltools-start

# Or run directly
./start.sh
```

Then open http://localhost:5000 in your browser.

## Installation

1. Make sure you have Python 3.6+ and required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the installer:
   ```bash
   ./install.sh
   ```

3. Restart your terminal, then use:
   - `dltools-start` - Start service
   - `dltools-stop` - Stop service

## Directory Structure

```
dltools_web/
├── app.py              # Flask web application
├── start.sh            # Start service script
├── stop.sh             # Stop service script
├── install.sh          # Installation script
├── requirements.txt    # Python dependencies
├── lib/
│   ├── DLtools.py          # Core download library
│   ├── astronames.py       # Astronomical name utilities
│   ├── dataselection.py    # Data selection tools
│   ├── NVSS_cutout.py      # NVSS download utility
│   └── get_VLASS_cutouts.py # VLASS download utility
└── templates/
    └── index.html      # Web interface
```

## Dependencies

### Core Dependencies
- flask, numpy, astropy, requests, wget

### Astronomy Tools
- astroquery, pyvo, beautifulsoup4

### VLASS Support
- reproject - Image reprojection and mosaicking
- radio-beam - Radio astronomy beam handling

## Supported Surveys

| Survey | Description | Special Parameters |
|--------|-------------|-------------------|
| LoTSS | LOFAR Two-metre Sky Survey | Data Release (1/2/3), Low Resolution |
| Legacy Survey | DECam Legacy Survey | Pixel Scale, Bands, Data Release; auto fallback to CDS HiPS2FITS |
| VLASS | VLA Sky Survey | Epoch (1/2/3), Image Type (ql/se) |
| NVSS | NRAO VLA Sky Survey | - |
| FIRST | Faint Images of the Radio Sky | - |
| SDSS | Sloan Digital Sky Survey | Pixel Scale, Bands |
| SMSS | SkyMapper Southern Survey | Band |
| VLBI | VLBI Astrometric Catalog | J2000 Name, Band (L/C/X/K) |
| RACS | Rapid ASKAP Continuum Survey | Band (Low/Mid/High), Polarization, Output Filename |
| EMU | Evolutionary Map of the Universe | Polarization, Output Filename |
| TGSS | TIFR GMRT Sky Survey | - |

### VLASS Image Types

- **ql (Quick Look)**: Standard quick-look images, faster to download
- **se (Single Epoch)**: Single epoch images with full calibration

### Legacy Survey fallback
If `legacysurvey.org` is unreachable, `LS_img()` automatically falls back to the CDS HiPS2FITS service (`alasky.u-strasbg.fr`). For FITS output, individual band cutouts are downloaded and combined into a multi-extension FITS (MEF) with HDUs `PRIMARY`, `G`, `R`, `Z` (or whichever bands were requested). For JPG output, a color composite from the HiPS color layer is downloaded.

## Sharing with Colleagues

This tool is fully portable. To share:

1. Copy the entire `dltools_web` folder
2. Recipient runs:
   ```bash
   pip install -r requirements.txt
   ./install.sh
   ```
3. Done!

The installer automatically detects the installation directory, so the folder can be placed anywhere.

## Troubleshooting

### VLASS downloads not working
Make sure `reproject` and `radio-beam` are installed:
```bash
pip install reproject radio-beam
```

### RACS/EMU downloads require authentication
These surveys use CASDA which requires authentication. You can provide credentials in one of the following ways:

1. **Environment variables (recommended for servers):**
   ```bash
   export CASDA_USERNAME="your_opal_username"
   export CASDA_PASSWORD="your_opal_password"
   ./start.sh
   ```

2. **In the web form:**
   When downloading RACS or EMU, fill in the **CASDA Username** and **CASDA Password** fields. These are the same as your ATNF OPAL credentials.

3. **Hard-code in `config.py` (not recommended for shared machines):**
   ```python
   CASDA_USERNAME = 'your_opal_username'
   CASDA_PASSWORD = 'your_opal_password'
   ```

If you don't have an account, register at [https://opal.atnf.csiro.au/](https://opal.atnf.csiro.au/).

### RACS/EMU output filename
Both RACS and EMU support an optional `out` parameter (or **Output Filename** in the web form). If left blank, the original CASDA filename is kept. If you set it to a filename (e.g. `racs.fits`), the downloaded image is renamed to that name inside `out_dir`. You can also provide a full path.

```python
from dltools_web.lib.DLtools import img_download
dl = img_download(ra, dec, size)
dl.RACS_img(out_dir='RACS', out='my_racs.fits', username='user', password='pass')
```

### For multiple sources download
It is good to use `from dltools_web.lib.DLtools import img_download` in your script for more flexible usage like multiple sources download.

## License

This project is for academic use. Individual survey data has its own terms of use.
