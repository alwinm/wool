Warning: cloning this repo also means downloading 100 MB of test data. If you just want the code it is all in one file: wool.py

# Algorithm

 - First create label array (same dimensions as input array) with scipy.ndimage.label
 - Define and Apply boundary function to label array to create a list of tuples. Each tuple represents two labels that are connected. 
 - Apply unionfind on list of connected labels to merge. 
 - Create a dictionary from label array where dict[label] = list(flattened indices of cells with that label)
 - Merge lists according to unionfind, this merges regions that are found to be contiguous due to the boundary function. 

# Usage

 - As with scipy.ndimage.label, user defines a masking function to convert an input numpy array into a True/False array. 

```python    
    import numpy
    example = numpy.random.random([100,100,100])
    mask = example > 0.2
```

- As with scipy.ndimage.label, user uses scipy.ndimage.generate_binary_structure to define a struct. 

```python
    import scipy.ndimage
    struct = scipy.ndimage.generate_binary_structure(3,3)
```

- User defines a boundary function which accepts boundary arguments (see wool.tigress example)

```python
    def boundary(label,bargs):
    	connectset = set()
        ...
	
        return connectset
```

- Put mask, struct, and boundary correction together to make a dictionary of objects. 

```python
    output_dictionary, owner_dictionary = wool.make_dict(mask,struct,boundary,bargs)
```

# Boundary Function

A boundary function takes in the label array resulting from scipy.ndimage.label and optional arguments. Then, it should find tuples of labels which neighbor each other due to boundary correction. I provide examples wool.periodic and wool.shear_periodic which pick out labels on faces, and wool.connect_faces_rank(face1,face2) connects two faces. 

# test_wool.py

I provide some example masks under the data directory. You can try running 

```
python test_wool.py
```

which will show the results of boundary correction. It also shows how the example functions work with both 2D and 3D arrays. The data arrays are 3D and are summed over axis 2 to create 2D arrays. 