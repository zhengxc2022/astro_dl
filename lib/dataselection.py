import numpy as np
from astropy.table import Table
import matplotlib.pyplot as plt 
from functools import reduce

#### A collection of data selection tools

def _non_mask(arr):
    '''
    When applying the tools to masked arrays, it is important to consider masked value. 
    '''
    all_id = list(range(len(arr)))
    try:
        _masked_id = np.where(arr.mask)[0]
        masked_id = np.setdiff1d(all_id,_masked_id)
    except:
        masked_id = all_id
    return masked_id

def find_between(arr,pmin=-np.inf,pmax=np.inf):
    '''
    Find elements within (pmin,pmax] in array. Return the element indices in the array.
    '''
    ind1 = np.where(arr>pmin)[0]
    ind2 = np.where(arr<=pmax)[0]
    masked = _non_mask(arr)
    res_ind = reduce(np.intersect1d,(ind1,ind2,masked))
    return res_ind

def find_value(arr,data):
    '''
    Find the element with the indicated (exact) value. 
    '''
    ind = np.where(arr==data)[0]
    return ind

def find_str(arr,strval):
    '''
    Find the element with the specific string.
    '''
    ind = []
    for i in range(len(arr)):
        if strval in arr[i]:
            ind.append(i)
    return ind

def match_inds(arr_to_match,big_array):
    '''
    Find the position in the big_array for each element of arr_to_match.
    '''
    ind = list(-1*np.ones(len(arr_to_match),dtype=int))
    for i in range(len(ind)):
        _ind = find_value(big_array,arr_to_match[i])
        if len(_ind) > 0 :
            ind[i] = int(_ind[0])
        else:
            ind[i] = -1 
    return ind 
    

def intersectND(indx):
    '''
    Return the intersect of N arrays.
    '''
    nends = 1
    _ind = indx[0]
    while(nends<len(indx)):
        _ind = np.intersect1d(_ind,indx[nends])
        nends += 1
    return _ind

def find_between_multiarray(array_list,prange=[[-np.inf,np.inf]]):
    '''
    Find element indices with multiple constraints. E.g. property A within ( prange[0][0],prange[0][1] ], property B within ( prange[1][0],prange[1][1] ] ...
    Return element indices.
    '''
    assert len(array_list) == len(prange)
    indx = []
    for i in range(len(array_list)):
        indx.append(find_between(array_list[i],pmin=prange[i][0],pmax=prange[i][1]))
    inter_ind = intersectND(indx)
    return inter_ind

def _make_pranges_from_bins(arr,bins):
    '''
    Make prange used in find_between from bins used in histograms.
    '''
    nums, edges = np.histogram(arr,bins) # get the edges
    pranges = [ [edges[i], edges[i+1]] for i in range(len(nums)) ]
    return pranges

def hist_with_indices(arr,bins=5):
    '''
    Similar to histogram in numpy, but also return the element indices in each bin.
    '''
    ### Normal output in np.histogram
    nums, edges = np.histogram(arr,bins)
    ### find indices
    indices = [ find_between(arr,edges[i],edges[i+1]) for i in range(len(nums)) ]
    return (nums,edges,np.array(indices))

def control_sample_construct(target_tab,ref_tab,ref_keys,key_bins,size=100,repeat=True):
    '''
    From target table, construct a controlled sample based on the distribution of the reference table. The key element and bins (defining cells) should be indicated.
    Return the indices of sources in the target table with similar distribution as the reference table.
    If repeat=True, allow repeated sources, otherwise allow small deviation from the reference distribution.
    '''
    ## First, calculate the reference dsitribution.
    assert len(ref_keys) == len(key_bins)
    ref_pranges = [ _make_pranges_from_bins(ref_tab[ref_keys[i]], key_bins[i]) for i in range(len(ref_keys)) ] # pranges for find_between_multiarray
    ref_key_arrays = [ref_tab[ref_keys[i]] for i in range(len(ref_keys))]

    cells_shape = []
    for keyi in range(len(ref_keys)):
        cells_shape.append(len(ref_pranges[keyi])) # nd cells: for example, 3 keys with 3,4,5 bins, then the resulting cells number and shape of the sampling block should be 3x4x5
    freq_distribution = np.zeros(shape=cells_shape)
    _cell_indices = np.indices(cells_shape) # The indices of each cell in the sampling block
    _flatten_cell_indices = np.array([ _cell_indices[i].flatten() for i in range(len(ref_keys)) ]) # flatten indices, _flatten_cell_indices[:,i] is the bin indices corresponding to each keyword of the ith cell 
    cell_nums = len(_flatten_cell_indices[0]) # total cell number
    
    def _take_prange(i):
        '''
        Take the pranges of the ith cell to use find_between_multiarray.
        '''
        _pranges = []
        for keyi in range(len(_flatten_cell_indices[:,i])):
            bini = _flatten_cell_indices[:,i][keyi]
            _pranges.append(ref_pranges[keyi][bini]) # the keyith keyword, and the binith bin
        return _pranges

    freq_in_cells = []
    for i in range(cell_nums):
        _pranges = _take_prange(i)
        _inds = find_between_multiarray(ref_key_arrays,_pranges)
        freq_in_cells.append(len(_inds))
    ref_freq_array = np.array(freq_in_cells)/np.sum(freq_in_cells) ## to frequencies of each cell.

    #### Take sample based on the frequency distribution
    target_key_arrays = [target_tab[ref_keys[i]] for i in range(len(ref_keys))]
    ind_in_cells = []
    for i in range(cell_nums):
        _pranges = _take_prange(i)
        _inds = find_between_multiarray(target_key_arrays,_pranges)
        expected_nums = round(ref_freq_array[i]*size) 
        if repeat: # if repeated sampling is allowed
            ind_in_cells.append(np.random.choice(_inds,size=expected_nums)) 
        else: # otherwise, choose the maximum size allowed
            _cell_size = min(expected_nums,len(_inds))
            ind_in_cells.append(np.random.choice(_inds,size=_cell_size))
    fin_inds = np.concatenate(ind_in_cells)

    return fin_inds

def check_control_results(result_tab,ref_tab,ref_keys,key_bins):
    '''
    Check sampling results.
    '''
    axe_num = len(ref_keys)
    fig,axs = plt.subplots(1,axe_num,tight_layout=True)
    for i in range(axe_num):
        axs[i].hist(ref_tab[ref_keys[i]],bins=key_bins[i],histtype='step',density=True)
        axs[i].hist(result_tab[ref_keys[i]],bins=key_bins[i],histtype='step',hatch='//',density=True)
        axs[i].legend(['ref','con'])
    return fig
    

def test():
    '''
    For test.
    '''
    ref_col1, ref_col2, ref_col3 = np.random.random((3,100))
    tar_col1, tar_col2, tar_col3 = np.random.random((3,1000))
    ref_col2 = 3*ref_col2+3 # 3 to 6
    tar_col2 = 5*tar_col2+2 # 2 to 7
    ref_col3 = 100*ref_col3 # 0 to 100
    tar_col3 = 98*tar_col3+2 # 2 to 100

    ref_tab = Table([ref_col1,ref_col2,ref_col3],names=('col1','col2','col3'))
    tar_tab = Table([tar_col1,tar_col2,tar_col3],names=('col1','col2','col3'))

    new_control = control_sample_construct(tar_tab,ref_tab,['col1','col2','col3'],[5,3,[0,15,30,60,90,100]],size=2000,repeat=True)
    new_control_non_repeat = control_sample_construct(tar_tab,ref_tab,['col1','col2','col3'],[5,3,[0,15,30,60,90,100]],size=2000,repeat=False)

    check_control_results(tar_tab[new_control],ref_tab,['col1','col2','col3'],[5,3,[0,15,30,60,90,100]])
    check_control_results(tar_tab[new_control_non_repeat],ref_tab,['col1','col2','col3'],[5,3,[0,15,30,60,90,100]])
