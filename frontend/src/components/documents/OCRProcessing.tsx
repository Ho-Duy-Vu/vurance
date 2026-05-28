'use client';

import { CheckCircle, Circle, Loader2 } from 'lucide-react';

interface Step {
  label: string;
  status: 'pending' | 'active' | 'done';
}

interface Props {
  steps?: Step[];
}

const DEFAULT_STEPS: Step[] = [
  { label: 'Nhận tài liệu', status: 'pending' },
  { label: 'OCR nhận diện văn bản', status: 'pending' },
  { label: 'AI phân tích & trích xuất', status: 'pending' },
];

export function OCRProcessing({ steps = DEFAULT_STEPS }: Props) {
  return (
    <div className="flex flex-col gap-3 p-4">
      {steps.map((step, i) => (
        <div key={i} className="flex items-center gap-3">
          {step.status === 'done' ? (
            <CheckCircle className="text-green-500 shrink-0" size={20} />
          ) : step.status === 'active' ? (
            <Loader2 className="text-blue-500 animate-spin shrink-0" size={20} />
          ) : (
            <Circle className="text-gray-300 shrink-0" size={20} />
          )}
          <span
            className={`text-sm ${
              step.status === 'done'
                ? 'text-green-700'
                : step.status === 'active'
                  ? 'text-blue-600 font-medium'
                  : 'text-gray-400'
            }`}
          >
            {step.label}
          </span>
        </div>
      ))}
    </div>
  );
}
