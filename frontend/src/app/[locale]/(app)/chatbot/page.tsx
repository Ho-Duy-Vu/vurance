import { getTranslations } from 'next-intl/server';

export default async function ChatbotPage() {
  const t = await getTranslations('chatbot');
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">{t('title')}</h1>
      <p className="text-gray-400 text-sm">— TASK-020 —</p>
    </div>
  );
}
