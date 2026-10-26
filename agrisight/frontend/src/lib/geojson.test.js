import { describe, it, expect } from 'vitest';
import {
  toFlatFeatureList, listFromResponse, featureCollectionFromResponse,
  geometryLatLngs, geometryCenter, regionIdOf,
} from './geojson';

// Regression: GeoFeatureModelSerializer endpoints return
// { results: { type: 'FeatureCollection', features } }. Map, Analytics,
// Exports and Conflict Reports crashed with "regions.map is not a function";
// Regions and Stress Events silently showed empty states.
// Report: .gstack/qa-reports/qa-report-agrisight-2026-10-26.md (P0 #3, #4)

const multiPolygon = {
  type: 'MultiPolygon',
  coordinates: [[[[29.2, -1.4], [29.6, -1.4], [29.6, -0.9], [29.2, -0.9], [29.2, -1.4]]]],
};
const paginated = {
  count: 1, next: null, previous: null,
  results: {
    type: 'FeatureCollection',
    features: [{ id: 1, type: 'Feature', geometry: multiPolygon, properties: { name: 'Rutshuru', province: 'North Kivu' } }],
  },
};

describe('geojson helpers', () => {
  it('flattens a paginated FeatureCollection response', () => {
    expect(listFromResponse(paginated)).toEqual([
      { id: 1, name: 'Rutshuru', province: 'North Kivu', geometry: multiPolygon },
    ]);
  });

  it('handles bare arrays, bare FeatureCollections and empty input', () => {
    expect(listFromResponse([{ id: 2 }])).toEqual([{ id: 2 }]);
    expect(listFromResponse(paginated.results)).toHaveLength(1);
    expect(listFromResponse({ count: 0, results: { type: 'FeatureCollection', features: [] } })).toEqual([]);
    expect(listFromResponse(null)).toEqual([]);
    expect(toFlatFeatureList(undefined)).toEqual([]);
  });

  it('returns the FeatureCollection for exports', () => {
    expect(featureCollectionFromResponse(paginated)).toBe(paginated.results);
    const fc = featureCollectionFromResponse([{ id: 3, name: 'Kalehe', geometry: null }]);
    expect(fc.type).toBe('FeatureCollection');
    expect(fc.features[0]).toMatchObject({ type: 'Feature', id: 3, properties: { name: 'Kalehe' } });
  });

  it('extracts Leaflet lat/lng points from a MultiPolygon', () => {
    const pts = geometryLatLngs(multiPolygon);
    expect(pts).toHaveLength(5);
    expect(pts[0]).toEqual([-1.4, 29.2]);
    const [lat, lng] = geometryCenter(multiPolygon);
    expect(lat).toBeCloseTo(-1.2, 2);
    expect(lng).toBeCloseTo(29.36, 2);
    expect(geometryCenter(null)).toBeNull();
    expect(geometryLatLngs({ type: 'Point', coordinates: [29, -1] })).toEqual([[-1, 29]]);
  });

  it('reads a region id from an id or a nested object', () => {
    expect(regionIdOf({ region: 4 })).toBe(4);
    expect(regionIdOf({ region: { id: 5 } })).toBe(5);
    expect(regionIdOf({})).toBeUndefined();
  });
});
