import React, { useState } from 'react';
import { Upload, FileText, MessageCircle, Loader2, X, Download } from 'lucide-react';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import Summary from './components/Summary';
import ChatInterface from './components/ChatInterface';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

function App() {
  const [currentDocument, setCurrentDocument] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);

  const handleFileUpload = async (file) => {
    setIsProcessing(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setCurrentDocument(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error uploading file');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleNewDocument = () => {
    setCurrentDocument(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            📄 DocuMind
          </h1>
          <p className="text-gray-600">
            Upload PDFs or images to get AI-powered summaries and ask questions
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg flex items-center">
            <X className="w-5 h-5 mr-2" />
            {error}
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-500 hover:text-red-700"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {!currentDocument ? (
            /* File Upload Section */
            <div className="bg-white rounded-xl shadow-lg p-8">
              <div className="text-center mb-6">
                <Upload className="w-16 h-16 text-blue-500 mx-auto mb-4" />
                <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                  Upload Your Document
                </h2>
                <p className="text-gray-600">
                  Support for PDF files and images (JPEG, PNG)
                </p>
              </div>

              <FileUpload 
                onFileUpload={handleFileUpload} 
                isProcessing={isProcessing}
              />

              {isProcessing && (
                <div className="mt-6 text-center">
                  <Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-2" />
                  <p className="text-gray-600">Processing your document...</p>
                </div>
              )}
            </div>
          ) : (
            /* Document Summary and Chat Section */
            <div className="space-y-6">
              {/* Header with New Document Button */}
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-semibold text-gray-800 flex items-center">
                  <FileText className="w-6 h-6 mr-2" />
                  Document Analysis
                </h2>
                <button
                  onClick={handleNewDocument}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  New Document
                </button>
              </div>

              {/* Summary Section */}
              <Summary summary={currentDocument.summary} />

              {/* Chat Interface */}
              <ChatInterface documentId={currentDocument.document_id} />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500">
          <p>AI-Powered Document Analysis</p>
        </div>
      </div>
    </div>
  );
}

export default App;
