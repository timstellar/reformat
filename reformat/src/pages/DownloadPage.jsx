import { useParams } from 'react-router-dom';
import axios from 'axios';
import { useState, useEffect } from 'react';

const DownloadPage = () => {
  const { id } = useParams(); // Get the ID from URL like /download/123
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [fileInfo, setFileInfo] = useState(null);

  // Fetch file info when component mounts
  useEffect(() => {
    const fetchFileInfo = async () => {
      try {
        const response = await axios.get(`http://localhost:3000/api/get-file-info/${id}`);
        setFileInfo(response.data);
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to fetch file information');
      }
    };

    if (id) {
      fetchFileInfo();
    }
  }, [id]);

  const handleDownload = async () => {
    if (!id) return;
    
    setIsLoading(true);
    setError(null);

    try {
      // Request the file from Flask server
      const response = await axios.get(`http://localhost:3000/api/download/${id}`, {
        responseType: 'blob' // Important for file downloads
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Set filename from response headers or use default
      const contentDisposition = response.headers['content-disposition'];
      let fileName = `document_${id}.pdf`;
      
      if (contentDisposition) {
        const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
        if (fileNameMatch.length === 2) {
          fileName = fileNameMatch[1];
        }
      }
      
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to download file');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="page">
      <h1>Скачать файл</h1>
      
      {error && (
        <div className="error-message">
          Ошибка: {error}
        </div>
      )}

      {fileInfo ? (
        <>
          <p>Документ: {fileInfo.fileName || `Запрос ${id}`}</p>
          <p>Размер: {fileInfo.fileSize ? `${(fileInfo.fileSize / 1024).toFixed(2)} KB` : 'Неизвестно'}</p>
          
          <button 
            onClick={handleDownload} 
            className="download-btn"
            disabled={isLoading}
          >
            {isLoading ? 'Идет загрузка...' : 'Скачать файл'}
          </button>
        </>
      ) : (
        <p>Загрузка информации о файле...</p>
      )}
    </div>
  );
};

export default DownloadPage;