The rastercalculator.txt file contains formulas into raster calculator of QGIS to determin the overflow time of a the cells in a raster-map.
The calculation tries the modelling of the USDA NRCS TR-55 calculation in determining velocity of flowing water during sheet flow, during shallow flow and during channel flow
Firt I had to determin the Sheet flow and the Shalow flow to every cell.(vSHSHrk.tif) From this I can estimate a water yield, from that I can calculate the velocity of the channel flow too(vSHSHCHrk.tif)
The last cflwTrk.tif file is an input data of the python calculation, which calculates the total runoff time of a cell until the bottom of a watershed basin
