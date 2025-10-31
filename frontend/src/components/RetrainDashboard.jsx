import { useState } from 'react';
import { RefreshCw, Upload, Loader2, CheckCircle, XCircle, AlertCircle, FileText } from 'lucide-react';
import { API } from '../App_new';

export default function RetrainDashboard() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a valid CSV file');
      setFile(null);
    }
  };

  const handleRetrain = async () => {
    if (!file) {
      setError('Please select a CSV file first');
      return;
    }

    setLoading(true);
    setProgress([]);
    setResult(null);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(API.forecast.retrain, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.status === 'progress') {
                setProgress(prev => [...prev, data.message]);
              } else if (data.status === 'complete') {
                setResult(data);
                setProgress(prev => [...prev, '✅ Retraining completed successfully!']);
              } else if (data.status === 'error') {
                setError(data.message || 'Retraining failed');
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (err) {
      setError(err.message || 'Failed to retrain model');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Retrain Form */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center space-x-2 mb-6">
          <RefreshCw className="text-purple-600" size={24} />
          <h2 className="text-2xl font-bold text-gray-800">Retrain Model</h2>
        </div>

        <div className="space-y-6">
          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Training Data (CSV)
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-purple-500 transition-colors">
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
                disabled={loading}
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center space-y-2"
              >
                <Upload className="text-gray-400" size={48} />
                <div>
                  <span className="text-purple-600 font-semibold">Click to upload</span>
                  <span className="text-gray-600"> or drag and drop</span>
                </div>
                <p className="text-xs text-gray-500">CSV file with columns: date, sales</p>
              </label>
            </div>

            {file && (
              <div className="mt-3 flex items-center space-x-2 text-sm text-gray-700 bg-purple-50 px-4 py-2 rounded-lg">
                <FileText size={16} className="text-purple-600" />
                <span className="font-medium">{file.name}</span>
                <span className="text-gray-500">({(file.size / 1024).toFixed(2)} KB)</span>
              </div>
            )}
          </div>

          {/* Instructions */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-800 mb-2">CSV Format Requirements:</h4>
            <ul className="text-sm text-blue-700 space-y-1 ml-4">
              <li>• Must contain columns: <code className="bg-blue-100 px-1 rounded">date</code> and <code className="bg-blue-100 px-1 rounded">sales</code></li>
              <li>• Date format: YYYY-MM-DD</li>
              <li>• Sales values should be numeric</li>
              <li>• Example: date,sales</li>
              <li>• &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2024-01-01,150</li>
            </ul>
          </div>

          {/* Retrain Button */}
          <button
            onClick={handleRetrain}
            disabled={!file || loading}
            className="w-full bg-gradient-to-r from-purple-500 to-purple-600 text-white py-3 rounded-lg font-semibold hover:from-purple-600 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin" size={20} />
                <span>Retraining Model...</span>
              </>
            ) : (
              <>
                <RefreshCw size={20} />
                <span>Start Retraining</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
          <XCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <h3 className="font-semibold text-red-800">Error</h3>
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Progress Logs */}
      {progress.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center space-x-2">
            <Loader2 className={loading ? "animate-spin text-purple-600" : "text-green-600"} size={20} />
            <span>Progress Logs</span>
          </h3>
          <div className="bg-gray-900 text-green-400 rounded-lg p-4 font-mono text-sm max-h-96 overflow-y-auto">
            {progress.map((msg, index) => (
              <div key={index} className="mb-1">
                <span className="text-gray-500">[{new Date().toLocaleTimeString()}]</span> {msg}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Success Result */}
      {result && result.status === 'complete' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center space-x-2 mb-4">
            <CheckCircle className="text-green-600" size={24} />
            <h3 className="text-xl font-bold text-gray-800">Retraining Completed</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-semibold text-green-800 mb-2">Training Summary</h4>
              <ul className="text-sm text-green-700 space-y-1">
                <li>• Data file uploaded successfully</li>
                <li>• Model retrained with new data</li>
                <li>• Prophet and LSTM models updated</li>
                <li>• Ready for new forecasts</li>
              </ul>
            </div>

            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <h4 className="font-semibold text-purple-800 mb-2">Next Steps</h4>
              <ul className="text-sm text-purple-700 space-y-1">
                <li>• Navigate to Forecast tab</li>
                <li>• Generate new predictions</li>
                <li>• Compare with previous results</li>
                <li>• Monitor model performance</li>
              </ul>
            </div>
          </div>

          {result.message && (
            <div className="mt-4 bg-gray-50 rounded-lg p-3">
              <p className="text-sm text-gray-700 font-mono">{result.message}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
