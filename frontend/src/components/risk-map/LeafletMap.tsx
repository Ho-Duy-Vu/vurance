'use client';

import { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import type { Layer, LeafletMouseEvent, Path, PathOptions } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { GeoRisk } from '@/types';

interface Props {
  riskData: GeoRisk[];
  onProvinceClick: (province: GeoRisk | null) => void;
}

// Highcharts map collection — verified working, 63 VN provinces, property key = "name"
const GEOJSON_URL =
  'https://raw.githubusercontent.com/highcharts/map-collection-dist/master/countries/vn/vn-all.geo.json';

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
    // strip combining diacritical marks
    .replace(/[̀-ͯ]/g, '')
    // đ → d
    .replace(/đ/g, 'd')
    // strip non-alphanumeric except spaces
    .replace(/[^a-z0-9\s]/g, '')
    // collapse whitespace
    .replace(/\s+/g, ' ')
    .trim();
}

// Manual overrides: Highcharts English name → MongoDB Vietnamese name (normalized)
const HIGHCHARTS_OVERRIDE: Record<string, string> = {
  'ho chi minh city': 'tp ho chi minh',
  'hô chi minh': 'tp ho chi minh',
  'ba ria vung tau': 'ba ria vung tau',
  'thua thien hue': 'thua thien hue',
  'dak lak': 'dak lak',
  'dak nong': 'dak nong',
  'dien bien': 'dien bien',
  'ha giang': 'ha giang',
};

function buildRiskIndex(riskData: GeoRisk[]): Map<string, GeoRisk> {
  const idx = new Map<string, GeoRisk>();
  for (const r of riskData) {
    idx.set(normalize(r.province_name), r);
  }
  return idx;
}

function lookupRisk(featureName: string, idx: Map<string, GeoRisk>): GeoRisk | undefined {
  const key = normalize(featureName);
  // Direct match
  if (idx.has(key)) return idx.get(key);
  // Override match
  const overrideKey = HIGHCHARTS_OVERRIDE[key];
  if (overrideKey && idx.has(overrideKey)) return idx.get(overrideKey);
  // Partial match: feature name is substring of a province key or vice versa
  for (const [dbKey, risk] of idx.entries()) {
    if (dbKey.includes(key) || key.includes(dbKey)) return risk;
  }
  return undefined;
}

function GeoJsonLayer({
  riskData,
  onProvinceClick,
}: {
  riskData: GeoRisk[];
  onProvinceClick: (r: GeoRisk | null) => void;
}) {
  const [geoJson, setGeoJson] = useState<GeoJSON.FeatureCollection | null>(null);
  const [geoError, setGeoError] = useState('');
  const riskIndex = useRef(buildRiskIndex(riskData));

  useEffect(() => {
    riskIndex.current = buildRiskIndex(riskData);
  }, [riskData]);

  useEffect(() => {
    fetch(GEOJSON_URL)
      .then((r) => {
        if (!r.ok) throw new Error(`GeoJSON fetch failed: ${r.status}`);
        return r.json();
      })
      .then(setGeoJson)
      .catch((err) => {
        console.error('GeoJSON load error:', err);
        setGeoError(err.message);
      });
  }, []);

  if (geoError) {
    return (
      <div className="absolute inset-0 flex items-center justify-center z-[1000] pointer-events-none">
        <div className="bg-red-50 border border-red-200 text-red-600 text-sm px-4 py-2 rounded-lg">
          Không tải được bản đồ tỉnh: {geoError}
        </div>
      </div>
    );
  }

  if (!geoJson) return null;

  const style = (feature?: GeoJSON.Feature): PathOptions => {
    const name: string = feature?.properties?.name ?? feature?.properties?.Name ?? '';
    const risk = lookupRisk(name, riskIndex.current);
    return {
      fillColor: risk ? riskColor(risk.overall_risk_score) : '#94a3b8',
      fillOpacity: 0.65,
      color: '#fff',
      weight: 1,
    };
  };

  const onEachFeature = (feature: GeoJSON.Feature, layer: Layer) => {
    const name: string = feature?.properties?.name ?? feature?.properties?.Name ?? '';
    const risk = lookupRisk(name, riskIndex.current);

    layer.on({
      mouseover: (e: LeafletMouseEvent) => {
        (e.target as Path).setStyle({ fillOpacity: 0.9, weight: 2, color: '#1e40af' });
      },
      mouseout: (e: LeafletMouseEvent) => {
        (e.target as Path).setStyle({ fillOpacity: 0.65, weight: 1, color: '#fff' });
      },
      click: () => onProvinceClick(risk ?? null),
    });

    layer.bindTooltip(name, { permanent: false, direction: 'auto', sticky: true });
  };

  return <GeoJSON key={JSON.stringify(geoJson).length} data={geoJson} style={style} onEachFeature={onEachFeature} />;
}

export default function LeafletMap({ riskData, onProvinceClick }: Props) {
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
      <GeoJsonLayer riskData={riskData} onProvinceClick={onProvinceClick} />
    </MapContainer>
  );
}
