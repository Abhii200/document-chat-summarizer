import React from 'react';
import { FileText, Copy, Check } from 'lucide-react';
import { useState } from 'react';

const Summary = ({ summary }) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-gray-800 flex items-center">
          <FileText className="w-5 h-5 mr-2 text-blue-500" />
          Document Summary
        </h3>
        <button
          onClick={copyToClipboard}
          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          title="Copy summary"
        >
          {copied ? (
            <Check className="w-4 h-4 text-green-500" />
          ) : (
            <Copy className="w-4 h-4" />
          )}
        </button>
      </div>
      
      <div className="prose max-w-none">
        <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-blue-500">
          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
            {summary}
          </p>
        </div>
      </div>
    </div>
  );
};

export default Summary;
