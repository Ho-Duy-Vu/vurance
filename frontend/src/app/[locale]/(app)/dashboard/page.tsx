import { getTranslations } from 'next-intl/server';

export default async function DashboardPage() {
  const t = await getTranslations('nav');

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">{t('dashboard')}</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {['Tổng yêu cầu', 'Đã duyệt', 'Đang xử lý', 'Từ chối'].map((label, i) => (
          <div key={i} className="bg-white rounded-xl p-5 shadow-sm border">
            <p className="text-sm text-gray-500">{label}</p>
            <p className="text-3xl font-bold mt-2 text-gray-900">—</p>
          </div>
        ))}
      </div>
    </div>
  );
}
