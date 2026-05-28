'use client';

import { useLocale } from 'next-intl';
import { usePathname, useRouter } from 'next/navigation';

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const toggle = () => {
    const next = locale === 'vi' ? 'en' : 'vi';
    router.replace(pathname.replace(`/${locale}`, `/${next}`));
  };

  return (
    <button
      onClick={toggle}
      className="text-sm font-medium px-3 py-1.5 rounded-md border border-gray-200 hover:bg-gray-50 transition-colors"
    >
      {locale === 'vi' ? '🇻🇳 VI' : '🇺🇸 EN'}
    </button>
  );
}
