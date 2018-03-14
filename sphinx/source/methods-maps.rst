
Methodology for the monthly precipitation, surface water, and groundwater maps
==============================================================================

Introduction
------------
The goal of the freshwater maps is to visually provide a representative monthly wetness or dryness generalisation over large areas in Canterbury. For the surface water and precipitation maps, these areas represent the different hydrologic landscapes according to differences in elevation and latitude. The groundwater maps were meant to be representative for the CWMS zones.

The monthly generalisation is meant to be categorical rather than numerical. The development of the statistics and the associated maps followed this goal.
The mapping model was built in Python and mapped using the open source interactive python plotting library called Bokeh.

Surface water and precipitation
-----------------------------------
The sites selection for the surface water and precipitation was based on sites having at least 10 years of data ending in the beginning of 2017 and, in the case of surface water sites, their overall contribution to the mapping areas. Since surface water sites aggregate the surface water flow from their entire upstream catchment, only one site from one particular river was generally used to ensure there was no overlapping contributing areas. This is different from the precipitation and groundwater sites as those are discrete datasets without massive contributing areas.

The site selection for the surface water and precipitation sites are a fixed input to the model. This should likely stay this way for surface water sites due to the complexity in the selection, but precipitation sites could be automatically updated within the model in the future similar to the site selection for groundwater sites.

First, all of the quality controlled data was extracted from Hydstra and monthly aggregates were calculated. As the statistics are meant to represent the overall monthly dryness or wetness, the monthly median was used for the flow data to ensure that flooding events would not bias the statistic (i.e. compared to mean or sum). The monthly sum was used for precipitation. The sites were then grouped by month and order rankings were calculated for the entire dataset.

For the map statistics, the last six months of telemetered data was extracted from HydroTel to ensure that the most up-to-date data is always available at the time of the map creation. Again, the sites were aggregated and grouped by month. The telemetered monthly values for each site were then ranked within the earlier quality controlled data to determine its percentile.

Once all of the percentiles for the past six months are calculated for all sites, the site percentiles were aggregated to the larger hydrologic areas. The aggregation procedure was different for surface water sites and precipitation sites. All precipitation sites were given equal weight for each area, so consequently a simple mean of all monthly site values were used. As flow measured at a particular point along a river represents everything up gradient of that site, each flow value within the larger hydrologic area was weighted by its catchment size.

Once the monthly site values are aggregated to each hydrologic area, a categorical index is applied. 0-10%tile: very low, 10-25%tile: below average, 25-75%tile: average, 75-90%tile: above average, 90-100%tile: very high. These categories are identical to maps created by the USGS in their `Active Groundwater Level Network <https://groundwaterwatch.usgs.gov/default.asp>`_.

The mapping process is performed using the open source interactive python plotting library called Bokeh. The previous six months of the categories are presented on the map.

Groundwater
-----------
Most of the procedures for the groundwater map is similar to the surface water and precipitation map, but there are some key differences.

The areas used for the map presentation (and aggregation) for groundwater are the Canterbury Water Management Strategy (CWMS) zones as opposed to the larger hydrologic areas for surface water and precipitation.

The site selection for surface water and precipitation was performed once and is a fixed input to the mapping model, while the groundwater mapping makes the site selection every time the model is run. For the CWMS zones other than the Upper Waitaki, the criteria is that there is at least 10 years of data. Due to a necessity of including the Upper Waitaki even though no well meets the criteria of having at least 10 years of data, the year limit was lowered to 5 years.

The only data that was utilised for the groundwater mapping was the monthly manual water level measurements. This was done to increase the number of available wells for the mapping as compared to the wells with continuous data. All values up to the previous month were extracted. As the monthly sampling is performed at various times of the month and may even occasionally occur twice or not at all in a month, a linear interpolation was performed for all sites and the monthly median was taken to provide a more consistent and comparable dataset between sites.

The percentiles for the all sites for the entire dataset were calculated and, as with the surface water and precipitation mapping, the previous six months of percentiles were aggregated to the CWMS zones. The categories were then calculated according to the above and plotted using Bokeh.
