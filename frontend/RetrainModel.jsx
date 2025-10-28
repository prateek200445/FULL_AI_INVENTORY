import React, { useState } from 'react';

export default function RetrainModel() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setStatus('');
  };

  const handleRetrain = async () => {
    if (!file) {
      setStatus('Please select a CSV file to upload.');
      return;
    }

    setStatus('Uploading and retraining...');
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/retrain', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();

      if (res.ok) {
        setStatus(`Retrain successful: ${JSON.stringify(data.meta)}`);
      } else {
        setStatus(`Retrain failed: ${data.message || JSON.stringify(data)}`);
      }
    } catch (err) {
      setStatus(`Error: ${err.message}`);
    }
  };

  return (
    <div style={{ padding: 16 }}>
      <h3>Retrain Model</h3>
      <input type="file" accept=".csv" onChange={handleFileChange} />
      <div style={{ marginTop: 8 }}>
        <button onClick={handleRetrain}>Retrain Model</button>
      </div>
      <div style={{ marginTop: 12 }}>{status}</div>
    </div>
  );
}
