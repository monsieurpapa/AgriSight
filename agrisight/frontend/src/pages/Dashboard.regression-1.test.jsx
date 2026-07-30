import { describe, it, expect } from 'vitest';
import { toFlatFeatureList } from './Dashboard';

// Regression: ISSUE-004 — endpoints backed by GeoDjango models (regions,
// stress events, conflict events) are served by a GeoFeatureModelSerializer,
// so list data comes back as a GeoJSON FeatureCollection ({type, features})
// with each item's fields nested under `.properties`, not a plain array.
// Dashboard.jsx called `.filter()`/`.slice()` directly on that object,
// throwing "regionsList.filter is not a function" / "recent_events?.slice is
// not a function" and surfacing as a misleading "Connection Error" banner
// to the user. Found by /qa on 2026-07-30.
// Report: .gstack/qa-reports/qa-report-agrisight-2026-07-30.md

describe('toFlatFeatureList', () => {
  it('returns an empty array for null/undefined', () => {
    expect(toFlatFeatureList(null)).toEqual([]);
    expect(toFlatFeatureList(undefined)).toEqual([]);
  });

  it('passes a plain array through unchanged', () => {
    const input = [{ id: 1, name: 'Djugu' }];
    expect(toFlatFeatureList(input)).toEqual(input);
  });

  it('flattens a GeoJSON FeatureCollection into plain objects with id/geometry at the top level', () => {
    const featureCollection = {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          id: 5,
          geometry: { type: 'Polygon', coordinates: [] },
          properties: { name: 'Djugu', area_hectares: 1200, is_active: true },
        },
      ],
    };

    expect(toFlatFeatureList(featureCollection)).toEqual([
      {
        id: 5,
        name: 'Djugu',
        area_hectares: 1200,
        is_active: true,
        geometry: { type: 'Polygon', coordinates: [] },
      },
    ]);
  });

  it('returns an empty array for an empty FeatureCollection (the zero-regions case that triggered this bug)', () => {
    expect(toFlatFeatureList({ type: 'FeatureCollection', features: [] })).toEqual([]);
  });

  it('produces objects that support .filter/.slice/.reduce like Dashboard.jsx expects', () => {
    const result = toFlatFeatureList({
      type: 'FeatureCollection',
      features: [
        { type: 'Feature', id: 1, geometry: null, properties: { is_active: true, area_hectares: 10 } },
        { type: 'Feature', id: 2, geometry: null, properties: { is_active: false, area_hectares: 20 } },
      ],
    });

    expect(result.filter(r => r.is_active)).toHaveLength(1);
    expect(result.reduce((sum, r) => sum + r.area_hectares, 0)).toBe(30);
    expect(result.slice(0, 1)).toHaveLength(1);
  });
});
