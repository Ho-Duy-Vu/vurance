import { getTranslations } from 'next-intl/server';
import { RiskMapClient } from './RiskMapClient';

export default async function RiskMapPage() {
  const t = await getTranslations('geo');
  return (
    <div className="flex flex-col gap-4 h-full">
      <h1 className="text-2xl font-bold text-gray-900">{t('riskMap')}</h1>
      <RiskMapClient />
    </div>
  );
}
