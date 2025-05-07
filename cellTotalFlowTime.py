from osgeo import gdal
from math import asin


dirname = 'C:\\szakdolg_KNI\\py'
fn_flwacc = dirname+'\\flowacc_vagott.tif'
fn_rastcalc = dirname+'\\cflwTrk.tif'
fn_dir = dirname+'\\flowdir_vagott.tif'
outfn_time = '\\cTotFlwTime.tif'
outfn_grid = '\\Grid_py.tif'

ds = gdal.Open(fn_flwacc)
flwacc = ds.GetRasterBand(1).ReadAsArray()
flwacols = len(flwacc)
flwarows = len(flwacc[0])


time = flwacc.copy()
grid = flwacc.copy()
maxVal=0
for y in range(0, flwarows):
    x=0
    for x in range(0, flwacols):
        grid[x,y] = -1*(y+x*10000)
        time[x,y] = -1
        if (flwacc[x,y] > maxVal):
            maxVal = flwacc[x,y]
            maxx = x
            maxy = y            

ds = None
#raster calculation
ds = gdal.Open(fn_rastcalc)
rastcalc = ds.GetRasterBand(1).ReadAsArray()

ds = None
#flow direction (aspect)
ds = gdal.Open(fn_dir)
dir = ds.GetRasterBand(1).ReadAsArray()


#rastcalc[ix,iy] - a cellákon való átfolyási időket cellánként tároló raszter
#time[ix,iy] - az újonnan létrehozandó, teljes lefolyási időket cellánként tároló raszter
#dx és dy azaz directionx és directiony, vagyis az ix-től és iy-tól dir[ix,iy] (lefolyási) irányban lévő cella koordinátái
#cx és cy-ba gyűlnek azon koordináták amik a következő wkile i ciklusokban vizsgálva lesznek, mert belőlük víz folyik olyan cellákba amiknek már van a time[]-ban lefolyási idejük

cx=[maxx]
cy=[maxy]
if (rastcalc[maxx,maxy] >= 0): 
    time[maxx,maxy]=rastcalc[maxx,maxy]    
else:
    time[maxx,maxy]=0

    
rc=[]
i=0
while (i < len(cx)):
    x = cx[i]
    y = cy[i]
    ix = x-1    
    while ( (ix <= x+1) and (ix>=0) and (ix < len(flwacc)) ):
        iy = y-1
        while ( (iy <= y+1) and (iy>=0) and (iy < len(flwacc[0])) ):                
            if (flwacc [ix,iy] > 0):
                
                #if there is no data in the ultimate cells
                if (dir[ix,iy]>=0):
                    dirxy = dir[ix,iy]
                elif ( ((x-ix)== 0) and ((x-ix)== 0) ):
                    dir[ix,iy]=0
                    dirxy=2
                else:
                    dir[ix,iy] = asin( (ix-x)/((x-ix)**2+(y-iy)**2)**(1/2) )
                    if ((dirxy >= 337.5) or (dirxy <= 22.5)):
                        dirxy=2
                    elif ((dirxy >= 22.5) and (dirxy <= 67.5)): 
                        dirxy=1
                    elif ((dirxy >= 67.5) and (dirxy <= 112.5)):
                        dirxy=8
                    elif ((dirxy >= 112.5) and (dirxy <= 157.5)):
                        dirxy=7
                    elif ((dirxy >= 157.5) and (dirxy <= 202.5)):
                        dirxy=6
                    elif ((dirxy >= 202.5) and (dirxy <= 247.5)):
                        dirxy=5
                    elif ((dirxy >= 247.5) and (dirxy <= 292.5)):
                        dirxy=4                        
                    elif ((dirxy >= 292.5) and (dirxy <= 337.5)): 
                        dirxy=3
                   
                  
                if (rastcalc[ix,iy]>=0):
                    dirxy = dir[ix,iy]
                else:   #if the cell has no value
                    del rc
                    rc=[]
                    if rastcalc[ix-1,iy] > 0:
                        rc.append(rastcalc[ix-1,iy])
                    if rastcalc[ix+1,iy] > 0:
                        rc.append(rastcalc[ix+1,iy])
                    if rastcalc[ix,iy-1] > 0:
                        rc.append(rastcalc[ix,iy-1])
                    if rastcalc[ix,iy+1] > 0:
                        rc.append(rastcalc[ix,iy+1])
                    if len(rc)>0:
                        rastcalc[ix,iy] = sum(rc)/len(rc)
                    else:
                        rastcalc[ix,iy] = 0
                        
#           depending if neighbour cell flows into the central cell
            if ((ix != x) or (iy != y)) and (flwacc [ix,iy] > 0):                
                dx = ix
                dy = iy
                dirxy = dir[ix,iy]
                if (dirxy==1):
                    dx=ix-1
                    dy=iy+1
                elif (dirxy==2):
                    dx=ix-1
                elif (dirxy==3):
                    dx=ix-1
                    dy=iy-1
                elif (dirxy==4):
                    dy=iy-1
                elif (dirxy==5):
                    dx=ix+1
                    dy=iy-1
                elif (dirxy==6):
                    dx=ix+1
                elif (dirxy==7):
                    dx=ix+1
                    dy=iy+1
                elif (dirxy==8):
                    dy=iy+1
                if ((dx==x) and (dy==y)): 
                    time[ix,iy] = time[x,y] + rastcalc[ix,iy]
                    cx.append(ix)
                    cy.append(iy)
            iy+=1
        ix+=1
    i+=1
else:
    print("ready cycle")

cx = None
cy = None

# create the output image
driver = ds.GetDriver()

rows = ds.RasterYSize
cols = ds.RasterXSize

#TIME.tif
outDs = driver.Create(dirname+outfn_time, cols, rows, 1, gdal.GDT_Float32)
#if outDs is None:
#    print 'Could not create time.tif'
#    sys.exit(1)
outBand = outDs.GetRasterBand(1)
# write the data
outBand.WriteArray(time, 0, 0)
# flush data to disk, set the NoData value and calculate stats
outBand.FlushCache()
outBand.SetNoDataValue(-99)

# georeference the image and set the projection
outDs.SetGeoTransform(ds.GetGeoTransform())
outDs.SetProjection(ds.GetProjection())
#outDs.ImportFromEPSG(3857)


#GRID.tif
outDs = driver.Create(dirname+outfn_grid, cols, rows, 1, gdal.GDT_Float32)
#if outDs is None:
#    print 'Could not create time.tif'
#    sys.exit(1)
outBand = outDs.GetRasterBand(1)
# write the data
outBand.WriteArray(grid, 0, 0)
# flush data to disk, set the NoData value and calculate stats
outBand.FlushCache()
outBand.SetNoDataValue(-99)

# georeference the image and set the projection
outDs.SetGeoTransform(ds.GetGeoTransform())
outDs.SetProjection(ds.GetProjection())
#outDs.ImportFromEPSG(3857)


ds = None
del flwacc
del time
del rastcalc
del dir

#saving the raster:
outDs = None
print("ready")
