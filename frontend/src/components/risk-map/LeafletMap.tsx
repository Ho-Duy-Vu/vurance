'use client';

import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import type { Layer, LeafletMouseEvent, Path, PathOptions } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { GeoRisk } from '@/types';

interface Props {
  riskData: GeoRisk[];
  geoJson: GeoJSON.FeatureCollection;
  onProvinceClick: (province: GeoRisk | null) => void;
}

function riskColor(score: number): string {
  if (score >= 80) return '#dc2626';
  if (score >= 60) return '#ea580c';
  if (score >= 40) return '#ca8a04';
  return '#16a34a';
}

function normalize(name: string): string {
  return name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/đ/g, 'd')
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

// Highcharts uses English-ish names — map to normalized Vietnamese
const NAME_OVERRIDE: Record<string, string> = {
  'ho chi minh city': 'tp ho chi minh',
  'ba ria vung tau province': 'ba ria vung tau',
  'thua thien hue province': 'thua thien hue',
  'dak lak province': 'dak lak',
  'dak nong province': 'dak nong',
  'can tho city': 'can tho',
  'hai phong city': 'hai phong',
  'ha noi city': 'ha noi',
  'da nang city': 'da nang',
};

function buildIndex(riskData: GeoRisk[]): Map<string, GeoRisk> {
  const idx = new Map<string, GeoRisk>();
  for (const r of riskData) {
    idx.set(normalize(r.province_name), r);
  }
  return idx;
}

function lookupRisk(featureName: string, idx: Map<string, GeoRisk>): GeoRisk | undefined {
  const key = normalize(featureName);
  if (idx.has(key)) return idx.get(key);

  const overrideKey = NAME_OVERRIDE[key];
  if (overrideKey && idx.has(overrideKey)) return idx.get(overrideKey);

  // Partial match: any province whose normalized name overlaps
  for (const [dbKey, risk] of idx.entries()) {
    if (key.includes(dbKey) || dbKey.includes(key)) return risk;
  }
  return undefined;
}

export default function LeafletMap({ riskData, geoJson, onProvinceClick }: Props) {
  // Build index once per render (both datasets already ready when this component mounts)
  const riskIndex = buildIndex(riskData);

  const style = (feature?: GeoJSON.Feature): PathOptions => {
    const name: string = feature?.properties?.name ?? feature?.properties?.Name ?? '';
    const risk = lookupRisk(name, riskIndex);
    return {
      fillColor: risk ? riskColor(risk.overall_risk_score) : '#94a3b8',
      fillOpacity: 0.7,
      color: '#ffffff',
      weight: 1,
    };
  };

  const onEachFeature = (feature: GeoJSON.Feature, layer: Layer) => {
    const name: string = feature?.properties?.name ?? feature?.properties?.Name ?? '';
    const risk = lookupRisk(name, riskIndex);

    layer.on({
      mouseover: (e: LeafletMouseEvent) => {
        (e.target as Path).setStyle({ fillOpacity: 0.9, weight: 2, color: '#1e40af' });
      },
      mouseout: (e: LeafletMouseEvent) => {
        (e.target as Path).setStyle({ fillOpacity: 0.7, weight: 1, color: '#ffffff' });
      },
      click: () => onProvinceClick(risk ?? null),
    });

    const scoreText = risk ? ` — ${risk.overall_risk_score}/100` : '';
    layer.bindTooltip(`${name}${scoreText}`, {
      permanent: false,
      direction: 'auto',
      sticky: true,
    });
  };

  return (
    <MapContainer
      center={[16.047, 108.206]}
      zoom={6}
      style={{ height: '100%', width: '100%' }}
      scrollWheelZoom
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <GeoJSON
        key={riskData.length}
        data={geoJson}
        style={style}
        onEachFeature={onEachFeature}
      />
    </MapContainer>
  );
}
