/*
Code by : Pablo Angulo
pa@geoluxcs.com
WAB : +506 7284-0988
www.geoluxcs.com
*/
/***************************************
 * 1. ROI
 ***************************************/
var roi = ee.Geometry.Polygon(
 [[[-85.61232980041379, 10.54825590165948],
 [-85.61232980041379, 10.368642636958164],
 [-85.35827096252316, 10.368642636958164],
 [-85.35827096252316, 10.54825590165948]]], null, false
);

/***************************************
 * 2. Index Functions
 ***************************************/
function addIndices(image) {

 var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
 var ndre = image.normalizedDifference(['B8', 'B5']).rename('NDRE');

 var evi = image.expression(
 '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
 NIR: image.select('B8'),
 RED: image.select('B4'),
 BLUE: image.select('B2')
 }).rename('EVI');

 return image.addBands([ndvi, ndre, evi]);
}

/***************************************
 * 3. Sentinel-2 Collection
 ***************************************/
var s2 = ee.ImageCollection('COPERNICUS/S2')
 .filterBounds(roi)
 .filterDate('2025-12-01', '2026-01-31')
 .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))
 .map(addIndices);

var composite = s2.median().clip(roi);


/***************************************
 * 4. Generic 4-Class Classifier
 ***************************************/
function classifyIndex(image, bandName) {
 return image.select(bandName).expression(
 "(b < 0.2) ? 1" +
 ": (b < 0.4) ? 2" +
 ": (b < 0.6) ? 3" +
 ": 4", {
 b: image.select(bandName)
 }).rename('Class');
}


/***************************************
 * 5. Area Calculation (ha)
 ***************************************/
function computeStats(classImage) {

 var pixelArea = ee.Image.pixelArea().divide(10000);

 var areas = pixelArea.addBands(classImage)
 .reduceRegion({
 reducer: ee.Reducer.sum().group({
 groupField: 1,
 groupName: 'Class'
 }),
 geometry: roi,
 scale: 10,
 maxPixels: 1e13
 });

 return ee.FeatureCollection(
 ee.List(areas.get('groups')).map(function(item) {
 item = ee.Dictionary(item);
 var c = ee.Number(item.get('Class'));

 var label = ee.Algorithms.If(c.eq(1), '< 0.2 (Bare/Water)',
 ee.Algorithms.If(c.eq(2), '0.2–0.4 (Low Veg)',
 ee.Algorithms.If(c.eq(3), '0.4–0.6 (Moderate Veg)',
 '> 0.6 (High Veg)'
 )
 )
 );

 return ee.Feature(null, {
 'NDVI_Class': label,
 'Area_ha': item.get('sum')
 });
 })
 );
}

/***************************************
 * 6. UI DASHBOARD
 ***************************************/
var panel = ui.Panel({
 style: {
 width: '420px',
 position: 'bottom-left',
 padding: '10px'
 }
});

panel.add(ui.Label({
 value: 'Multi-Index Classification Dashboard',
 style: {fontSize: '18px', fontWeight: 'bold'}
}));

panel.add(ui.Label(
 'Classes:\n' +
 '1: < 0.2 (Bare/Water)\n' +
 '2: 0.2–0.4 (Low Veg)\n' +
 '3: 0.4–0.6 (Moderate Veg)\n' +
 '4: > 0.6 (High Veg)'
));

var indexSelect = ui.Select({
 items: ['NDVI', 'EVI', 'NDRE'],
 value: 'NDVI',
 style: {stretch: 'horizontal'}
});

panel.add(ui.Label('Select Index:'));
panel.add(indexSelect);

var chartPanel = ui.Panel();
panel.add(chartPanel);

ui.root.add(panel);

/***************************************
 * 7. Dynamic Update Function
 ***************************************/
function updateDashboard(indexName) {

 Map.layers().reset();
 chartPanel.clear();

 var classified = classifyIndex(composite, indexName).clip(roi);

 Map.addLayer(classified, {
 min: 1,
 max: 4,
 palette: ['hashtag#d9d9d9', 'hashtag#fdae61', 'hashtag#66bd63', 'hashtag#1a9850']
 }, indexName + ' Classes');

 var stats = computeStats(classified);

 var chart = ui.Chart.feature.groups({
 features: stats,
 xProperty: 'NDVI_Class',
 yProperty: 'Area_ha',
 seriesProperty: 'NDVI_Class'
 })
 .setChartType('ColumnChart')
 .setOptions({
 title: indexName + ' Area by Class (ha)',
 hAxis: {title: 'Class'},
 vAxis: {title: 'Area (ha)'},
 legend: {position: 'none'},
 colors: ['hashtag#d9d9d9', 'hashtag#fdae61', 'hashtag#66bd63', 'hashtag#1a9850']
 });

 chartPanel.add(chart);
}

/***************************************
 * 8. Map Initialization
 ***************************************/
Map.centerObject(roi, 12);
indexSelect.onChange(updateDashboard);
updateDashboard('NDVI');