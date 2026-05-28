import { Sidebar } from '@/components/layout/Sidebar';
import { LanguageSwitcher } from '@/components/layout/LanguageSwitcher';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <header className="h-14 border-b bg-white flex items-center justify-end px-6 gap-4 shadow-sm">
          <LanguageSwitcher />
        </header>
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
