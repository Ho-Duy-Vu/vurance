import { getTranslations } from 'next-intl/server';
import dynamic from 'next/dynamic';
import { Skeleton } from '@/components/ui/skeleton';

const LeafletMap = dynamic(() => import('@/components/risk-map/LeafletMap'), {
  ssr: false,
  loading: () => <Skeleton className="h-[500px] w-full rounded-xl" />,
});

export default async function RiskMapPage() {
  const t = await getTranslations('geo');

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">{t('riskMap')}</h1>
      <div className="bg-white rounded-xl shadow-sm border overflow-hidden" style={{ height: 500 }}>
        <LeafletMap />
      </div>
    </div>
  );
}
