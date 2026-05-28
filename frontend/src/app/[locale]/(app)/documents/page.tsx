import { getTranslations } from 'next-intl/server';

export default async function DocumentsPage() {
  const t = await getTranslations('nav');
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">{t('documents')}</h1>
      <p className="text-gray-400 text-sm">— TASK-012 —</p>
    </div>
  );
}
