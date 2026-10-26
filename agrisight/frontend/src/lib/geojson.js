/**
 * Helpers for API responses produced by djangorestframework-gis.
 *
 * GeoFeatureModelSerializer endpoints (regions, stress events, conflict
 * events, ...) return a paginated payload whose `results` is a GeoJSON
 * FeatureCollection, not an array:
 *
 *   { count, next, previous, results: { type: 'FeatureCollection', features: [...] } }
 *
 * Each feature keeps its fields under `.properties`. Pages that did
 * `data.results.map(...)` crashed ("regions.map is not a function") or showed
 * empty states. Normalise once with these helpers instead.
 */

/**
 * Flatten a FeatureCollection, a feature array, or a plain array into plain
 * objects: `{ id, ...properties, geometry }`. Non-feature items pass through.
 */
export const toFlatFeatureList = (value) => {
  if (!value) return [];
  const features = Array.isArray(value) ? value : (Array.isArray(value.features) ? value.features : []);
  return features.map((feature) =>
    feature && feature.type === 'Feature'
      ? { id: feature.id ?? feature.properties?.id, ...feature.properties, geometry: feature.geometry }
      : feature
  );
};

/**
 * Accept any list-endpoint response shape (paginated, FeatureCollection,
 * bare array) and return a flat array of records.
 */
export const listFromResponse = (response) => {
  if (!response) return [];
  if (Array.isArray(response)) return toFlatFeatureList(response);
  if (response.type === 'FeatureCollection') return toFlatFeatureList(response);
  if ('results' in response) return toFlatFeatureList(response.results);
  return [];
};

/**
 * Return a FeatureCollection from any list-endpoint response, for exports.
 */
export const featureCollectionFromResponse = (response) => {
  if (response?.type === 'FeatureCollection') return response;
  if (response?.results?.type === 'FeatureCollection') return response.results;
  const records = listFromResponse(response);
  return {
    type: 'FeatureCollection',
    features: records.map(({ geometry = null, ...properties }) => ({
      type: 'Feature',
      id: properties.id,
      geometry,
      properties,
    })),
  };
};

/**
 * All [lng, lat] positions in a GeoJSON geometry (Point, Polygon,
 * MultiPolygon, ...), at any nesting depth.
 */
export const geometryPositions = (geometry) => {
  if (!geometry) return [];
  if (geometry.type === 'GeometryCollection') {
    return (geometry.geometries || []).flatMap(geometryPositions);
  }
  const out = [];
  const walk = (node) => {
    if (!Array.isArray(node)) return;
    if (node.length >= 2 && typeof node[0] === 'number' && typeof node[1] === 'number') {
      out.push(node);
      return;
    }
    node.forEach(walk);
  };
  walk(geometry.coordinates);
  return out;
};

/** Leaflet-style [[lat, lng], ...] points for fitBounds. */
export const geometryLatLngs = (geometry) =>
  geometryPositions(geometry).map(([lng, lat]) => [lat, lng]);

/** Mean [lat, lng] of a geometry's positions, or null. */
export const geometryCenter = (geometry) => {
  const points = geometryLatLngs(geometry);
  if (!points.length) return null;
  const sum = points.reduce((acc, [lat, lng]) => [acc[0] + lat, acc[1] + lng], [0, 0]);
  return [sum[0] / points.length, sum[1] / points.length];
};

/** Region id of a record whose `region` may be an id or a nested object. */
export const regionIdOf = (record) =>
  record?.region && typeof record.region === 'object' ? record.region.id : record?.region;
