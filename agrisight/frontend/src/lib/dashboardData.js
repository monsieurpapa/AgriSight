/**
 * Pure helpers that turn API payloads into the Dashboard's view model.
 *
 * Several Dashboard figures used to be placeholders: every region showed
 * NDVI 0.5 and "healthy", the "Region Health" donut mixed stress-event
 * counts with region counts, "0 active" read a field the API never sends,
 * and a "Satellite data processing ... 2 hours ago" activity item was
 * fabricated. These helpers compute each value from real data, and return
 * null / "No data" when the data is missing instead of inventing it.
 */

/** Map a 1–5 stress severity (or a label) to low / medium / high. */
export const severityLevel = (severity) => {
  if (severity == null) return null;
  const n = Number(severity);
  if (!Number.isNaN(n)) {
    if (n >= 4) return 'high';
    if (n >= 2) return 'medium';
    return 'low';
  }
  const s = String(severity).toLowerCase();
  if (['high', 'critical', 'severe'].includes(s)) return 'high';
  if (['medium', 'moderate', 'warning'].includes(s)) return 'medium';
  if (['low', 'minor', 'info'].includes(s)) return 'low';
  return null;
};

const LEVEL_RANK = { low: 1, medium: 2, high: 3 };

const regionIdOfEvent = (event) =>
  event?.region && typeof event.region === 'object' ? event.region.id : event?.region;

/** Worst recent stress level per region id. */
export const worstStressByRegion = (stressEvents = []) => {
  const worst = new Map();
  stressEvents.forEach((event) => {
    const id = regionIdOfEvent(event);
    const level = severityLevel(event?.severity);
    if (id == null || !level) return;
    const current = worst.get(id);
    if (!current || LEVEL_RANK[level] > LEVEL_RANK[current]) worst.set(id, level);
  });
  return worst;
};

/**
 * Region Health donut: each region counted once, by its worst stress event
 * in the summary window; regions without events are "No recent stress".
 */
export const buildRegionStatus = (regions = [], stressEvents = []) => {
  const worst = worstStressByRegion(stressEvents);
  const counts = { high: 0, medium: 0, low: 0, none: 0 };
  regions.forEach((region) => {
    counts[worst.get(region.id) || 'none'] += 1;
  });
  return [
    { name: 'Severe stress', value: counts.high, color: '#ef4444' },
    { name: 'Moderate stress', value: counts.medium, color: '#f59e0b' },
    { name: 'Low stress', value: counts.low, color: '#10b981' },
    { name: 'No recent stress', value: counts.none, color: '#6b7280' },
  ];
};

/** Vegetation points from /satellite-processing/vegetation/<id>/ (object or legacy array). */
export const vegetationSeries = (regionData) => {
  if (!regionData) return [];
  if (Array.isArray(regionData)) return regionData;
  return Array.isArray(regionData.vegetation_data) ? regionData.vegetation_data : [];
};

/** Average each index per date across regions, sorted by date. */
export const buildVegetationTrends = (regionDataList = []) => {
  const byDate = {};
  regionDataList.forEach((regionData) => {
    vegetationSeries(regionData).forEach((point) => {
      const key = point.date;
      if (!key) return;
      byDate[key] ||= { date: key, sums: {}, counts: {} };
      const type = String(point.index_type || '').toLowerCase();
      if (!['ndvi', 'evi', 'ndwi', 'savi'].includes(type)) return;
      byDate[key].sums[type] = (byDate[key].sums[type] || 0) + Number(point.mean_value);
      byDate[key].counts[type] = (byDate[key].counts[type] || 0) + 1;
    });
  });
  return Object.values(byDate)
    .map(({ date, sums, counts }) => {
      const out = { date };
      ['ndvi', 'evi', 'ndwi', 'savi'].forEach((t) => {
        out[t] = counts[t] ? sums[t] / counts[t] : null;
      });
      return out;
    })
    .sort((a, b) => new Date(a.date) - new Date(b.date));
};

/** Latest NDVI and change over the window for one region, or nulls. */
export const ndviSummary = (regionData) => {
  const ndvi = vegetationSeries(regionData)
    .filter((p) => String(p.index_type).toUpperCase() === 'NDVI' && p.mean_value != null)
    .sort((a, b) => new Date(a.date) - new Date(b.date));
  if (!ndvi.length) return { ndvi: null, change: null };
  const latest = Number(ndvi[ndvi.length - 1].mean_value);
  const first = Number(ndvi[0].mean_value);
  return { ndvi: latest, change: ndvi.length > 1 ? latest - first : null };
};

/**
 * Region performance rows. `vegetationByRegionId` maps region id to the
 * vegetation endpoint payload (missing when not fetched or failed).
 */
export const buildTopRegions = (regions = [], vegetationByRegionId = {}, stressEvents = []) => {
  const worst = worstStressByRegion(stressEvents);
  return regions.map((region) => {
    const { ndvi, change } = ndviSummary(vegetationByRegionId[region.id]);
    return {
      id: region.id,
      name: region.name,
      ndvi,
      change,
      area: region.area_hectares != null ? region.area_hectares / 100 : null, // km²
      stress: worst.get(region.id) || null,
    };
  });
};
