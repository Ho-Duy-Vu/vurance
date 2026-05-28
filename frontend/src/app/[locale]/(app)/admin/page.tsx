import { getTranslations } from 'next-intl/server';

export default async function AdminPage() {
  const t = await getTranslations('admin');
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">{t('users')}</h1>
      <p className="text-gray-400 text-sm">— TASK-020d —</p>
    </div>
  );
}
