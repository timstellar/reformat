import { useState } from 'react';
import { getFilePath } from '../api';

const FilePathGetter = () => {
  const [requestNumber, setRequestNumber] = useState('');
  const [fileInfo, setFileInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!requestNumber.trim()) return;
    
    setIsLoading(true);
    setError(null);
    setFileInfo(null);
    
    const { success, data, error: fetchError } = await getFilePath(requestNumber);
    
    if (success) {
      setFileInfo(data);
    } else {
      setError(fetchError);
    }
    
    setIsLoading(false);
  };

  return (
    <div className="file-path-getter">
      <h2>Get File Path by Request Number</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="requestNumber">Request Number:</label>
          <input
            type="text"
            id="requestNumber"
            value={requestNumber}
            onChange={(e) => setRequestNumber(e.target.value)}
            placeholder="Enter request number (e.g., ЗВО-2025-04-18-002)"
            required
          />
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Searching...' : 'Get File Path'}
        </button>
      </form>

      {isLoading && <p>Loading...</p>}
      
      {error && (
        <div className="error">
          Error: {error}
        </div>
      )}

      {fileInfo && (
        <div className="file-info">
          <h3>File Information</h3>
          <p><strong>Request Number:</strong> {fileInfo.request_number}</p>
          <p><strong>File Path:</strong> {fileInfo.file_path}</p>
          <p><strong>File Name:</strong> {fileInfo.file_name}</p>
          {fileInfo.exists ? (
            <>
              <p><strong>Status:</strong> File exists</p>
              <p><strong>Size:</strong> {(fileInfo.file_size / 1024).toFixed(2)} KB</p>
              <a 
                href={`/api/download/${fileInfo.request_number}`} 
                className="download-link"
              >
                Download File
              </a>
            </>
          ) : (
            <p className="warning">File not found at specified path</p>
          )}
        </div>
      )}
    </div>
  );
};

export default FilePathGetter;