import { getTranslations } from 'next-intl/server';

export default async function LoginPage() {
  const t = await getTranslations('auth');
  return (
    <div className="bg-white rounded-2xl shadow-lg p-8">
      <h1 className="text-2xl font-bold text-center mb-6">{t('loginTitle')}</h1>
      <p className="text-center text-gray-500 text-sm">— TASK-008 —</p>
    </div>
  );
}
