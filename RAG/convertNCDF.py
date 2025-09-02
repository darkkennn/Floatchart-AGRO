import xarray as xr
import numpy as np
from pathlib import Path

profiles_dir = Path(__file__).resolve().parent.parent / "data" / "aoml" / "5907049" / "profiles"
nc_files = sorted(list(profiles_dir.glob("*.nc")))
datasets = []

# First pass: find maximum dimensions across all files
max_dimensions = {}
varying_dims = ['N_LEVELS', 'N_HISTORY', 'N_PARAM', 'N_CALIB']

for file in nc_files:
   ds = xr.open_dataset(file)
   for dim in varying_dims:
       if dim in ds.sizes:
           current_size = ds.sizes[dim]
           if dim not in max_dimensions or current_size > max_dimensions[dim]:
               max_dimensions[dim] = current_size
   ds.close()

# Second pass: load and pad all datasets to match maximum dimensions
for i, file in enumerate(nc_files):
   ds = xr.open_dataset(file)
   needs_padding = False
   
   # Check which dimensions need padding
   padding_info = {}
   for dim in max_dimensions:
       if dim in ds.sizes:
           current_size = ds.sizes[dim]
           if current_size < max_dimensions[dim]:
               padding_info[dim] = max_dimensions[dim] - current_size
               needs_padding = True
   
   if needs_padding:
       # Pad variables that have dimensions requiring padding
       padded_vars = {}
       for var_name, var_data in ds.data_vars.items():
           var_needs_padding = any(dim in var_data.dims for dim in padding_info.keys())
           
           if var_needs_padding:
               pad_width = []
               for dim in var_data.dims:
                   if dim in padding_info:
                       pad_width.append((0, padding_info[dim]))
                   else:
                       pad_width.append((0, 0))
               
               # Choose fill value based on data type
               if np.issubdtype(var_data.dtype, np.floating):
                   fill_value = np.nan
               elif np.issubdtype(var_data.dtype, np.integer):
                   fill_value = -999
               elif var_data.dtype.kind in ['U', 'S', 'O']:
                   fill_value = ''
               else:
                   fill_value = 0
               
               padded_data = np.pad(var_data.values, pad_width, 
                                  mode='constant', constant_values=fill_value)
               
               padded_vars[var_name] = xr.DataArray(
                   padded_data,
                   dims=var_data.dims,
                   attrs=var_data.attrs
               )
           else:
               padded_vars[var_name] = var_data
       
       # Handle coordinate padding
       new_coords = {}
       for coord_name, coord_data in ds.coords.items():
           if coord_name in padding_info:
               if coord_name in ds.coords and len(coord_data.values) == ds.sizes[coord_name]:
                   orig_values = coord_data.values
                   if coord_name == 'N_LEVELS':
                       if len(orig_values) > 1:
                           step = orig_values[-1] - orig_values[-2] if len(orig_values) > 1 else 1
                           new_values = np.concatenate([
                               orig_values,
                               np.arange(orig_values[-1] + step, 
                                        orig_values[-1] + step + padding_info[coord_name] * step, step)
                           ])
                       else:
                           new_values = np.arange(max_dimensions[coord_name])
                   else:
                       new_values = np.arange(max_dimensions[coord_name])
                   
                   new_coords[coord_name] = new_values
               else:
                   new_coords[coord_name] = np.arange(max_dimensions[coord_name])
           elif coord_name not in max_dimensions or coord_name not in padding_info:
               new_coords[coord_name] = coord_data
       
       ds_padded = xr.Dataset(padded_vars, coords=new_coords, attrs=ds.attrs)
       datasets.append(ds_padded)
   else:
       datasets.append(ds)

# Concatenate all datasets along N_PROF dimension
data_all = xr.concat(datasets, dim='N_PROF')