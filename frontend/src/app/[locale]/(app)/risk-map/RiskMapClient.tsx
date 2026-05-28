'use client';

import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { AlertTriangle, CheckCircle, Info, Shield } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import type { GeoRisk } from '@/types';
import api from '@/lib/api';

const LeafletMap = dynamic(() => import('@/components/risk-map/LeafletMap'), {
  ssr: false,
  loading: () => <Skeleton className="h-full w-full rounded-xl" />,
});

function RiskBadge({ score }: { score: number }) {
  if (score >= 80) return <span className="inline-flex items-center gap-1 text-xs font-semibold text-white bg-red-600 px-2 py-0.5 rounded-full"><AlertTriangle size={11} /> Rất cao</span>;
  if (score >= 60) return <span className="inline-flex items-center gap-1 text-xs font-semibold text-white bg-orange-500 px-2 py-0.5 rounded-full"><AlertTriangle size={11} /> Cao</span>;
  if (score >= 40) return <span className="inline-flex items-center gap-1 text-xs font-semibold text-white bg-yellow-500 px-2 py-0.5 rounded-full"><Info size={11} /> Trung bình</span>;
  return <span className="inline-flex items-center gap-1 text-xs font-semibold text-white bg-green-600 px-2 py-0.5 rounded-full"><CheckCircle size={11} /> Thấp</span>;
}

export function RiskMapClient() {
  const t = useTranslations('geo');
  const [riskData, setRiskData] = useState<GeoRisk[]>([]);
  const [selected, setSelected] = useState<GeoRisk | null>(null);
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState('');

  useEffect(() => {
    api.get('/geo-risk/map')
      .then((r) => setRiskData(r.data))
      .catch((err) => {
        console.error('API error:', err);
        setApiError('Không kết nối được API backend. Hãy chạy: uvicorn app.main:app --reload');
      })
      .finally(() => setLoading(false));
  }, []);

  if (apiError) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-lg">
        {apiError}
      </div>
    );
  }

  return (
    <div className="flex gap-4 flex-1" style={{ minHeight: 520 }}>
      {/* Map */}
      <div className="flex-1 bg-white rounded-xl shadow-sm border overflow-hidden">
        {loading ? (
          <Skeleton className="h-full w-full" />
        ) : (
          <LeafletMap riskData={riskData} onProvinceClick={setSelected} />
        )}
      </div>

      {/* Side panel */}
      <div className="w-72 shrink-0 flex flex-col gap-3">
        {/* Legend */}
        <div className="bg-white rounded-xl shadow-sm border p-4">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Chú thích</p>
          {[
            { color: 'bg-green-600', label: t('lowRisk'), range: '0–39' },
            { color: 'bg-yellow-500', label: t('mediumRisk'), range: '40–59' },
            { color: 'bg-orange-500', label: t('highRisk') + ' (cao)', range: '60–79' },
            { color: 'bg-red-600', label: t('highRisk') + ' (rất cao)', range: '80–100' },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-2 mb-1.5">
              <span className={`w-3 h-3 rounded-sm ${item.color}`} />
              <span className="text-xs text-gray-600">{item.label}</span>
              <span className="text-xs text-gray-400 ml-auto">{item.range}</span>
            </div>
          ))}
        </div>

        {/* Province detail */}
        {selected ? (
          <div className="bg-white rounded-xl shadow-sm border p-4 flex flex-col gap-3">
            <div className="flex items-start justify-between gap-2">
              <h2 className="font-bold text-gray-900">{selected.province_name}</h2>
              <RiskBadge score={selected.overall_risk_score} />
            </div>

            <div className="flex items-center gap-2">
              <div className="h-2 flex-1 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${selected.overall_risk_score}%`,
                    backgroundColor:
                      selected.overall_risk_score >= 80 ? '#dc2626'
                      : selected.overall_risk_score >= 60 ? '#ea580c'
                      : selected.overall_risk_score >= 40 ? '#ca8a04'
                      : '#16a34a',
                  }}
                />
              </div>
              <span className="text-sm font-bold text-gray-700">{selected.overall_risk_score}</span>
            </div>

            {selected.disaster_risks.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Thiên tai</p>
                <div className="space-y-1">
                  {selected.disaster_risks.map((d) => (
                    <div key={d.type} className="flex items-center justify-between text-xs">
                      <span className="text-gray-600 capitalize">{d.type}</span>
                      <span className="font-medium text-gray-800">{d.risk_score}/100</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selected.recommendations.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2 flex items-center gap-1">
                  <Shield size={11} /> {t('recommendations')}
                </p>
                <div className="space-y-2">
                  {selected.recommendations.slice(0, 3).map((rec, i) => (
                    <div key={i} className="bg-blue-50 rounded-lg px-3 py-2">
                      <p className="text-xs font-medium text-blue-800">{rec.insurance_type}</p>
                      <p className="text-xs text-blue-600 mt-0.5">{rec.reason}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-sm border p-4 text-center text-gray-400">
            <Info size={24} className="mx-auto mb-2 opacity-40" />
            <p className="text-sm">{t('clickProvince')}</p>
          </div>
        )}
      </div>
    </div>
  );
}
