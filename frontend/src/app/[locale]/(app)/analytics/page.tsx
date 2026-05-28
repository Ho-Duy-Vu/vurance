import { getTranslations } from 'next-intl/server';

export default async function AnalyticsPage() {
  const t = await getTranslations('nav');
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">{t('analytics')}</h1>
      <p className="text-gray-400 text-sm">— TASK-021 —</p>
    </div>
  );
}
