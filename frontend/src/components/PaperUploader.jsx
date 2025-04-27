import React, { useState } from 'react';
import { Box, Button, Typography, CircularProgress, Alert } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const PaperUploader = () => {
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [progress, setProgress] = useState(0);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a PDF file');
      setFile(null);
    }
  };

  const checkTaskStatus = async (taskId) => {
    try {
      const response = await fetch(`http://localhost:9000/api/v1/task-status/${taskId}`);
      const data = await response.json();
      
      if (data.status === 'completed') {
        setIsProcessing(false);
        setResult(data.result);
        setProgress(100);
      } else if (data.status === 'error') {
        setIsProcessing(false);
        setError(data.error);
      } else {
        // Update progress based on elapsed time (assuming 2 minutes max processing time)
        const elapsedTime = data.elapsed_time;
        const progress = Math.min(Math.round((elapsedTime / 120) * 100), 95);
        setProgress(progress);
        
        // Continue polling
        setTimeout(() => checkTaskStatus(taskId), 2000);
      }
    } catch (error) {
      setIsProcessing(false);
      setError('Failed to check task status');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResult(null);
    setProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:9000/api/v1/upload-paper', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload file');
      }

      const data = await response.json();
      
      if (data.task_id) {
        // Start polling for status
        checkTaskStatus(data.task_id);
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      setIsProcessing(false);
      setError(error.message);
    }
  };

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Upload Research Paper
      </Typography>
      
      <Box sx={{ mb: 3 }}>
        <input
          accept=".pdf"
          style={{ display: 'none' }}
          id="raised-button-file"
          type="file"
          onChange={handleFileChange}
        />
        <label htmlFor="raised-button-file">
          <Button
            variant="contained"
            component="span"
            startIcon={<CloudUploadIcon />}
            disabled={isProcessing}
          >
            Select PDF
          </Button>
        </label>
        {file && (
          <Typography variant="body1" sx={{ mt: 1 }}>
            Selected: {file.name}
          </Typography>
        )}
      </Box>

      {isProcessing && (
        <Box sx={{ width: '100%', mb: 2 }}>
          <CircularProgress variant="determinate" value={progress} />
          <Typography variant="body2" color="text.secondary">
            Processing: {progress}%
          </Typography>
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {result && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="h6" gutterBottom>
            Analysis Results:
          </Typography>
          <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </Box>
      )}

      <Button
        variant="contained"
        color="primary"
        onClick={handleUpload}
        disabled={!file || isProcessing}
        sx={{ mt: 2 }}
      >
        {isProcessing ? 'Processing...' : 'Upload and Analyze'}
      </Button>
    </Box>
  );
};

export default PaperUploader; 