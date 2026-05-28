'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="p-4 rounded-lg bg-red-50 border border-red-200">
            <p className="text-red-600 font-medium text-sm">Có lỗi xảy ra</p>
            <p className="text-red-400 text-xs mt-1">{this.state.error?.message}</p>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
