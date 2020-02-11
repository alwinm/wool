import wool as csp
import pylab as p
import scipy.ndimage as sn
import numpy as n
import matplotlib.colors as mco

def process(index,bool2d=False):
    cell_shear = index
    filename = 'data/wool{}.npy'.format(index)
    mask = n.load(filename)
    if bool2d:
        mask = mask.sum(axis=2) > 0
    
    #    struct = sn.generate_binary_structure(3,3)
    dim = mask.ndim
    struct = sn.generate_binary_structure(dim,dim)
    csp.default_struct = struct
    label,things = sn.label(mask,structure=struct)

    od,ownerof = csp.make_dict(mask,struct,csp.tigress,cell_shear)
    newlabel = n.zeros(n.prod(label.shape))
    for key in od:
        newlabel[od[key]] = key
    newlabel = newlabel.reshape(label.shape)

    plot(newlabel,cell_shear)
    return label, cell_shear

def plot(label,cell_shear):
    ml = n.max(label)
    big = 1000000
    bigpart = (label == 0)
    label[bigpart] = big
    if label.ndim == 2:
        image = label.transpose()
    else:
        image = n.min(label,axis=2).transpose()
    image[image > ml] = 0
    fullimage = n.zeros([image.shape[0],3*image.shape[1]])
    data_LHS = n.roll(image,cell_shear,axis=0)
    data_RHS = n.roll(image,-cell_shear,axis=0)
    fullimage[:,0:image.shape[1]] = data_LHS
    fullimage[:,image.shape[1]:2*image.shape[1]] = image
    fullimage[:,2*image.shape[1]:3*image.shape[1]] = data_RHS
    p.pcolormesh(fullimage,norm=mco.LogNorm())


ni = 1
nh = 6
nw = 4
testlist = [61,97,133,168,204,240]
for index in testlist:
    p.subplot(nh,nw,ni)
    oldlabel,cell_shear = process(int(index))
    p.ylabel(index)

    if ni <= nw:
        p.title('Good 3D')

    ni += 1
    p.subplot(nh,nw,ni)
    plot(oldlabel,cell_shear)
    if ni <= nw:
        p.title('Bad 3D')
    ni += 1

    p.subplot(nh,nw,ni)
    oldlabel,cell_shear = process(int(index),bool2d=True)

    if ni <= nw:
        p.title('Good 2D')

    ni += 1
    p.subplot(nh,nw,ni)
    plot(oldlabel,cell_shear)

    if ni <= nw:
        p.title('Bad 2D')

    ni += 1



p.show()

