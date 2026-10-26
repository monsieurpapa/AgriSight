import { describe, it, expect } from 'vitest';
import {
  severityLevel, buildRegionStatus, buildVegetationTrends, ndviSummary, buildTopRegions, vegetationSeries,
} from './dashboardData';
import { formatBadgeCount } from '../hooks/useNavCounts';

// Regressions from docs/qa/qa-report-2026-10-26.md (P1 #10): the dashboard
// showed NDVI 0.5 / "healthy" for every region, the health donut mixed
// event counts with region counts, and vegetation trends were always empty
// because the endpoint returns { vegetation_data: [...] }, not an array.

const regions = [
  { id: 1, name: 'Rutshuru', area_hectares: 150000 },
  { id: 2, name: 'Masisi', area_hectares: 120000 },
  { id: 3, name: 'Kalehe', area_hectares: 90000 },
];
const events = [
  { id: 'a', region: 1, severity: 5 },
  { id: 'b', region: 1, severity: 2 },
  { id: 'c', region: 2, severity: 3 },
];
const veg = {
  region_id: 1,
  vegetation_data: [
    { date: '2026-10-01', index_type: 'NDVI', mean_value: 0.7 },
    { date: '2026-10-20', index_type: 'NDVI', mean_value: 0.55 },
    { date: '2026-10-20', index_type: 'EVI', mean_value: 0.4 },
  ],
};

describe('dashboardData', () => {
  it('maps severities', () => {
    expect(severityLevel(5)).toBe('high');
    expect(severityLevel(3)).toBe('medium');
    expect(severityLevel(1)).toBe('low');
    expect(severityLevel('critical')).toBe('high');
    expect(severityLevel(null)).toBeNull();
  });

  it('counts each region once by its worst recent stress', () => {
    const status = Object.fromEntries(buildRegionStatus(regions, events).map((s) => [s.name, s.value]));
    expect(status).toEqual({ 'Severe stress': 1, 'Moderate stress': 1, 'Low stress': 0, 'No recent stress': 1 });
  });

  it('reads vegetation points from the endpoint object', () => {
    expect(vegetationSeries(veg)).toHaveLength(3);
    expect(vegetationSeries(null)).toEqual([]);
    const trends = buildVegetationTrends([veg]);
    expect(trends.map((t) => t.date)).toEqual(['2026-10-01', '2026-10-20']);
    expect(trends[1]).toMatchObject({ ndvi: 0.55, evi: 0.4, ndwi: null });
  });

  it('derives latest NDVI and change, null without data', () => {
    const s = ndviSummary(veg);
    expect(s.ndvi).toBeCloseTo(0.55);
    expect(s.change).toBeCloseTo(-0.15);
    expect(ndviSummary(undefined)).toEqual({ ndvi: null, change: null });
  });

  it('never invents NDVI for regions without vegetation data', () => {
    const rows = buildTopRegions(regions, { 1: veg }, events);
    expect(rows[0]).toMatchObject({ name: 'Rutshuru', stress: 'high', area: 1500 });
    expect(rows[0].ndvi).toBeCloseTo(0.55);
    expect(rows[1]).toMatchObject({ name: 'Masisi', ndvi: null, change: null, stress: 'medium' });
    expect(rows[2]).toMatchObject({ name: 'Kalehe', ndvi: null, stress: null });
  });
});

describe('formatBadgeCount', () => {
  it('hides zero/unknown and caps large counts', () => {
    expect(formatBadgeCount(0)).toBeNull();
    expect(formatBadgeCount(undefined)).toBeNull();
    expect(formatBadgeCount(3)).toBe('3');
    expect(formatBadgeCount(150)).toBe('99+');
  });
});
