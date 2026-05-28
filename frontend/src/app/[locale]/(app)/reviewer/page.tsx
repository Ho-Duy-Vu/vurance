import { getTranslations } from 'next-intl/server';

export default async function ReviewerPage() {
  const t = await getTranslations('reviewer');
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">{t('queue')}</h1>
      <p className="text-gray-400 text-sm">— TASK-020e —</p>
    </div>
  );
}
