# Scipy Measurements Label with boundary correction

import scipy.ndimage as sn
import numpy as n

default_struct = sn.generate_binary_structure(3,3)

def clean_tuples(tuples):
    return sorted(set([(min(pair),max(pair)) for pair in tuples]))

def merge_tuples_unionfind(tuples):
    # use classic algorithms union find with path compression
    # https://en.wikipedia.org/wiki/Disjoint-set_data_structure
    parent_dict = {}

    def subfind(x):
        # update roots while visiting parents 
        if parent_dict[x] != x:
            parent_dict[x] = subfind(parent_dict[x])
        return parent_dict[x]

    def find(x):
        if x not in parent_dict:
            # x forms new set and becomes a root
            parent_dict[x] = x
            return x
        if parent_dict[x] != x:
            # follow chain of parents of parents to find root 
            parent_dict[x] = subfind(parent_dict[x])
        return parent_dict[x]

    # each tuple represents a connection between two items 
    # so merge them by setting root to be the lower root. 
    for p0,p1 in list(tuples):
        r0 = find(p0)
        r1 = find(p1)
        if r0 < r1:
            parent_dict[r1] = r0
        elif r1 < r0:
            parent_dict[r0] = r1

    # for unique parents, subfind the root, replace occurrences with root
    vs = set(parent_dict.values())
    for parent in vs:
        sp = subfind(parent)
        if sp != parent:
            for key in parent_dict:
                if parent_dict[key] == parent:
                    parent_dict[key] = sp

    return parent_dict

def make_dict(mask,struct,boundary,bargs):
    label,things = sn.label(mask,structure=struct)
    cs = clean_tuples(boundary(label,bargs))
    slc = sn.labeled_comprehension(mask,label,range(1,things+1),
                                   lambda a,b: b,
                                   list,
                                   None,
                                   pass_positions=True)
    outdict = dict(zip(range(1,things+1),slc))
    ownerof = merge_tuples_unionfind(cs)
    for key in ownerof:
        if key != ownerof[key]:
            # add key to its owner and remove key
            outdict[ownerof[key]] = n.append(outdict[ownerof[key]],outdict[key])
            outdict.pop(key)
    return outdict,ownerof

def shear_periodic(label,axis,cell_shear,shear_axis):
    # just return the tuple of the one axis
    # 1. get faces
    dim = label.ndim
    size = label.shape[axis]
    select1 = [slice(None)]*dim
    select2 = [slice(None)]*dim
    select1[axis] = 0
    select2[axis] = size-1
    lf1 = label[tuple(select1)]
    lf2 = label[tuple(select2)]
    # 2. now cell shear
    axes = list(range(dim))
    axes.remove(axis)
    aisa = axes.index(shear_axis)
    lf2 = n.roll(lf2,cell_shear,axis=aisa)
    return connect_faces(lf1,lf2)

def periodic(label,axis):
    dim = label.ndim
    size = label.shape[axis]
    select1 = [slice(None)]*dim
    select2 = [slice(None)]*dim
    select1[axis] = 0
    select2[axis] = size-1
    lf1 = label[tuple(select1)]
    lf2 = label[tuple(select2)]
    return connect_faces(lf1,lf2)

def tigress(label,cell_shear):
    # open in Z
    # periodic in Y, so axis = 1
    connectset = set()
    connectset = connectset.union(periodic(label,1))
    # shear periodic in X, so axis = 0, shear_axis = 1
    connectset = connectset.union(shear_periodic(label,0,cell_shear,1))
    return connectset

def connect_faces_simple(lf1,lf2):
    # lf1 and lf2 are label faces
    select = lf1*lf2 > 0
    stack = n.zeros(list(lf1.shape)+[2])
    stack[:,:,0] = lf1
    stack[:,:,1] = lf2
    pairs = stack[select]
    return set([tuple(pair) for pair in pairs])

def connect_faces_rank(lf1,lf2):

    stack = n.zeros([2]+list(lf1.shape))
    stack[0] = lf1
    stack[1] = lf2
    label,things = sn.label(stack > 0,structure=default_struct)
    if things == 0:
        return set()
    slc = sn.labeled_comprehension(stack,label,range(1,things+1),
                                   lambda a: list(set(a)),
                                   list,
                                   None,
                                   pass_positions=False)
    tuples = []
    for region in slc:
        if len(region) == 0:
            continue
        owner = n.min(region)
        for cell in region:
            if cell != owner:
                tuples += [(owner,cell)]
    return set(tuples)

connect_faces = connect_faces_rank
