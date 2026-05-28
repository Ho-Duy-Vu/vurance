'use client';

import { useLocale, useTranslations } from 'next-intl';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  BarChart3,
  ClipboardList,
  FileText,
  LayoutDashboard,
  Map,
  MessageCircle,
  ShieldCheck,
  Users,
} from 'lucide-react';

export function Sidebar() {
  const t = useTranslations('nav');
  const locale = useLocale();
  const pathname = usePathname();

  const links = [
    { href: `/${locale}/dashboard`, label: t('dashboard'), icon: LayoutDashboard },
    { href: `/${locale}/documents`, label: t('documents'), icon: FileText },
    { href: `/${locale}/risk-map`, label: t('riskMap'), icon: Map },
    { href: `/${locale}/claims`, label: t('claims'), icon: ClipboardList },
    { href: `/${locale}/analytics`, label: t('analytics'), icon: BarChart3 },
    { href: `/${locale}/chatbot`, label: t('chatbot'), icon: MessageCircle },
    { href: `/${locale}/reviewer`, label: t('reviewer'), icon: ShieldCheck },
    { href: `/${locale}/admin`, label: t('admin'), icon: Users },
  ];

  return (
    <aside className="w-60 bg-gray-900 text-white min-h-screen flex flex-col shrink-0">
      <div className="p-5 border-b border-gray-700">
        <h1 className="text-lg font-bold text-blue-400 tracking-tight">ClaimFlow</h1>
        <p className="text-xs text-gray-400 mt-0.5">AI Insurance Platform</p>
      </div>
      <nav className="flex-1 p-3 space-y-0.5">
        {links.map(({ href, label, icon: Icon }) => {
          const isActive = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon size={17} />
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
