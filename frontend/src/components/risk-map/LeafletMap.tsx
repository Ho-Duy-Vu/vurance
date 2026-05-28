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

const GEOJSON_URL =
  'https://raw.githubusercontent.com/haitrieu1811/vietnam-geojson/main/vietnam-provinces.geojson';

function riskColor(score: number): string {
  if (score >= 80) return '#dc2626';
  if (score >= 60) return '#ea580c';
  if (score >= 40) return '#ca8a04';
  return '#16a34a';
}

function normalizeProvince(name: string): string {
  return name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/đ/g, 'd')
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function buildRiskIndex(riskData: GeoRisk[]): Map<string, GeoRisk> {
  const idx = new Map<string, GeoRisk>();
  for (const r of riskData) {
    idx.set(normalizeProvince(r.province_name), r);
  }
  return idx;
}

function GeoJsonLayer({
  riskData,
  onProvinceClick,
}: {
  riskData: GeoRisk[];
  onProvinceClick: (r: GeoRisk | null) => void;
}) {
  const [geoJson, setGeoJson] = useState<GeoJSON.FeatureCollection | null>(null);
  const riskIndex = useRef(buildRiskIndex(riskData));

  useEffect(() => {
    riskIndex.current = buildRiskIndex(riskData);
  }, [riskData]);

  useEffect(() => {
    fetch(GEOJSON_URL)
      .then((r) => r.json())
      .then(setGeoJson)
      .catch(console.error);
  }, []);

  if (!geoJson) return null;

  const style = (feature?: GeoJSON.Feature): PathOptions => {
    const name: string = feature?.properties?.Name ?? feature?.properties?.name ?? '';
    const risk = riskIndex.current.get(normalizeProvince(name));
    return {
      fillColor: risk ? riskColor(risk.overall_risk_score) : '#94a3b8',
      fillOpacity: 0.65,
      color: '#fff',
      weight: 1,
    };
  };

  const onEachFeature = (feature: GeoJSON.Feature, layer: Layer) => {
    const name: string = feature?.properties?.Name ?? feature?.properties?.name ?? '';
    const risk = riskIndex.current.get(normalizeProvince(name));

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

  return <GeoJSON key={geoJson.type} data={geoJson} style={style} onEachFeature={onEachFeature} />;
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
