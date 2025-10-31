import { useEffect, useRef, useState } from 'react';
import { Html5QrcodeScanner, Html5Qrcode } from 'html5-qrcode';
import { X, Camera, Upload, Image, AlertCircle } from 'lucide-react';

export default function QRScanner({ onScan, onClose }) {
  const scannerRef = useRef(null);
  const fileInputRef = useRef(null);
  const [isScanning, setIsScanning] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [activeTab, setActiveTab] = useState('camera'); // 'camera' or 'upload'
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    if (activeTab !== 'camera' || !scannerRef.current) return;

    const scanner = new Html5QrcodeScanner(
      "qr-reader",
      { 
        fps: 10,
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0,
        rememberLastUsedCamera: true,
        showTorchButtonIfSupported: true,
        useBarCodeDetectorIfSupported: true
      },
      false
    );

    scanner.render(
      (decodedText, decodedResult) => {
        // Success callback
        console.log(`QR Code decoded: ${decodedText}`);
        onScan(decodedText);
        scanner.clear();
        onClose();
      },
      (errorMessage) => {
        // Error callback - we can ignore most errors as they're just "no QR found"
        // console.warn(errorMessage);
      }
    );

    setIsScanning(true);

    return () => {
      if (scanner) {
        scanner.clear().catch(err => console.error("Scanner cleanup error:", err));
      }
    };
  }, [activeTab, onScan, onClose]);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadError(null);
    setIsProcessing(true);

    // Validate file type
    if (!file.type.match('image.*')) {
      setUploadError('Please upload an image file (PNG, JPG, etc.)');
      setIsProcessing(false);
      // Reset file input
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    try {
      // Create a new instance for file scanning
      const html5QrCode = new Html5Qrcode("qr-file-reader");
      
      // Scan the file with showImage = false to avoid rendering issues
      const decodedText = await html5QrCode.scanFile(file, false);
      
      console.log(`✅ QR Code successfully decoded from file: ${decodedText}`);
      
      // Clean up
      await html5QrCode.clear();
      
      // Reset file input
      if (fileInputRef.current) fileInputRef.current.value = '';
      
      // Success - call the onScan callback with decoded text
      onScan(decodedText);
      onClose();
    } catch (err) {
      console.error('❌ Error scanning file:', err);
      setUploadError('Could not read QR code from this image. Please ensure the image contains a clear, visible QR code.');
      setIsProcessing(false);
      // Reset file input
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-2xl max-w-lg w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-2">
            <Camera className="text-blue-600" size={24} />
            <h3 className="text-xl font-bold text-gray-800">Scan Product QR Code</h3>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X size={24} className="text-gray-600" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-200">
          <button
            onClick={() => setActiveTab('camera')}
            className={`flex-1 py-3 px-4 font-medium transition-colors flex items-center justify-center space-x-2 ${
              activeTab === 'camera'
                ? 'border-b-2 border-blue-600 text-blue-600 bg-blue-50'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Camera size={18} />
            <span>Camera Scan</span>
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex-1 py-3 px-4 font-medium transition-colors flex items-center justify-center space-x-2 ${
              activeTab === 'upload'
                ? 'border-b-2 border-blue-600 text-blue-600 bg-blue-50'
                : 'text-gray-600 hover:bg-gray-50'
            }`}
          >
            <Upload size={18} />
            <span>Upload Image</span>
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Camera Scanner Tab */}
          {activeTab === 'camera' && (
            <>
              <div 
                id="qr-reader" 
                ref={scannerRef}
                className="w-full"
              ></div>
              
              <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-800">
                  <strong>📷 Instructions:</strong>
                </p>
                <ul className="text-sm text-blue-700 mt-2 space-y-1 list-disc list-inside">
                  <li>Allow camera permissions when prompted</li>
                  <li>Point your camera at the Product QR code</li>
                  <li>Hold steady until the code is scanned</li>
                  <li>The Product ID will be automatically entered</li>
                </ul>
              </div>
            </>
          )}

          {/* Upload Tab */}
          {activeTab === 'upload' && (
            <>
              <div id="qr-file-reader" className="hidden"></div>
              
              <div className="space-y-4">
                {/* Upload Button */}
                <div 
                  onClick={!isProcessing ? triggerFileInput : undefined}
                  className={`border-2 border-dashed border-gray-300 rounded-lg p-8 text-center transition-all ${
                    isProcessing 
                      ? 'cursor-not-allowed opacity-50' 
                      : 'cursor-pointer hover:border-blue-500 hover:bg-blue-50'
                  }`}
                >
                  {isProcessing ? (
                    <>
                      <div className="animate-spin mx-auto mb-3 h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full"></div>
                      <p className="text-lg font-semibold text-blue-700 mb-1">
                        Processing Image...
                      </p>
                      <p className="text-sm text-blue-600">
                        Decoding QR code, please wait
                      </p>
                    </>
                  ) : (
                    <>
                      <Image className="mx-auto text-gray-400 mb-3" size={48} />
                      <p className="text-lg font-semibold text-gray-700 mb-1">
                        Click to Upload QR Code Image
                      </p>
                      <p className="text-sm text-gray-500">
                        Supports PNG, JPG, JPEG, GIF, BMP, WEBP
                      </p>
                    </>
                  )}
                </div>

                {/* Hidden File Input */}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />

                {/* Error Message */}
                {uploadError && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start space-x-2">
                    <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={18} />
                    <p className="text-sm text-red-700">{uploadError}</p>
                  </div>
                )}

                {/* Instructions */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <p className="text-sm text-green-800">
                    <strong>📁 Upload Instructions:</strong>
                  </p>
                  <ul className="text-sm text-green-700 mt-2 space-y-1 list-disc list-inside">
                    <li>Take a photo of the QR code with your phone</li>
                    <li>Or screenshot a QR code from your screen</li>
                    <li>Click the upload area and select the image</li>
                    <li>The QR code will be decoded automatically</li>
                  </ul>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
