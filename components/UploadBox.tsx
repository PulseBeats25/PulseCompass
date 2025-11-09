'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, Database, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { useAnalysis } from '@/contexts/AnalysisContext'
import { useRouter } from 'next/navigation'

interface UploadedFile {
  id: string
  name: string
  size: number
  type: 'pdf' | 'excel' | 'csv'
}

export default function UploadBox() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const { startAnalysis, isAnalyzing } = useAnalysis()
  const router = useRouter()

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setIsUploading(true)
    
    try {
      const newFiles: UploadedFile[] = []
      
      // Group files by type
      const pdfFiles = acceptedFiles.filter(f => getFileType(f.name) === 'pdf')
      const excelFiles = acceptedFiles.filter(f => ['excel', 'csv'].includes(getFileType(f.name)))
      
      // Upload PDFs
      if (pdfFiles.length > 0) {
        const formData = new FormData()
        pdfFiles.forEach(file => formData.append('files', file))
        
        const response = await fetch('http://localhost:8000/upload/pdf', {
          method: 'POST',
          body: formData,
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }))
          throw new Error(errorData.detail || `Failed to upload PDF files`)
        }
        
        const result = await response.json()
        
        result.files.forEach((fileResult: any, index: number) => {
          const pdfFile = pdfFiles[index]
          if (pdfFile) {
            newFiles.push({
              id: fileResult.file_id,
              name: pdfFile.name,
              size: pdfFile.size,
              type: 'pdf'
            })
          }
        })
      }
      
      // Upload Excel/CSV files
      if (excelFiles.length > 0) {
        const formData = new FormData()
        excelFiles.forEach(file => formData.append('files', file))
        
        const response = await fetch('http://localhost:8000/upload/excel', {
          method: 'POST',
          body: formData,
        })
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }))
          throw new Error(errorData.detail || `Failed to upload Excel files`)
        }
        
        const result = await response.json()
        
        result.files.forEach((fileResult: any, index: number) => {
          const excelFile = excelFiles[index]
          if (excelFile) {
            newFiles.push({
              id: fileResult.file_id,
              name: excelFile.name,
              size: excelFile.size,
              type: getFileType(excelFile.name)
            })
          }
        })
      }
      
      setUploadedFiles(prev => {
        const updated = [...prev, ...newFiles]
        console.log(`📁 Total files in UI: ${updated.length}`, updated.map(f => f.name))
        return updated
      })
      toast.success(`${acceptedFiles.length} file(s) uploaded and processed successfully`)
    } catch (error) {
      console.error('Upload error:', error)
      const errorMessage = error instanceof Error ? error.message : 'Upload failed. Please try again.'
      toast.error(errorMessage)
    } finally {
      setIsUploading(false)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
      'text/csv': ['.csv']
    },
    multiple: true
  })

  const getFileType = (filename: string): 'pdf' | 'excel' | 'csv' => {
    const ext = filename.toLowerCase().split('.').pop()
    if (ext === 'pdf') return 'pdf'
    if (ext === 'csv') return 'csv'
    return 'excel'
  }

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf':
        return <FileText className="w-5 h-5 text-red-500" />
      case 'csv':
        return <Database className="w-5 h-5 text-green-500" />
      default:
        return <Database className="w-5 h-5 text-blue-500" />
    }
  }

  const removeFile = (id: string) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== id))
    toast.success('File removed')
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const loadSampleData = async () => {
    try {
      toast.loading('Loading sample data...')
      const response = await fetch('http://localhost:8000/upload/seed-sample-data', {
        method: 'POST'
      })
      
      if (response.ok) {
        const result = await response.json()
        toast.success('Sample data loaded successfully!')
        
        // Add sample files to the UI (append to existing files)
        const sampleFiles = [
          {
            id: result.files[0].file_id,
            name: 'Sample Company - Q3 2024 Earnings Call.pdf',
            size: 50000,
            type: 'pdf' as const
          },
          {
            id: result.files[1].file_id,
            name: 'Sample Company Financial Data.xlsx',
            size: 25000,
            type: 'excel' as const
          }
        ]
        setUploadedFiles(prev => [...prev, ...sampleFiles])
      } else {
        toast.error('Failed to load sample data')
      }
    } catch (error) {
      console.error('Sample data error:', error)
      toast.error('Failed to load sample data')
    }
  }

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`upload-zone cursor-pointer ${
          isDragActive ? 'border-primary-500 bg-primary-100' : ''
        } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} disabled={isUploading} />
        
        <div className="flex flex-col items-center">
          <motion.div
            animate={isUploading ? { rotate: 360 } : { rotate: 0 }}
            transition={{ duration: 1, repeat: isUploading ? Infinity : 0 }}
          >
            <Upload className={`w-8 h-8 mb-3 ${
              isDragActive ? 'text-primary-600' : 'text-gray-400'
            }`} />
          </motion.div>
          
          {isUploading ? (
            <p className="text-gray-600">Uploading files...</p>
          ) : isDragActive ? (
            <p className="text-primary-600 font-medium">Drop files here</p>
          ) : (
            <div className="text-center">
              <p className="text-gray-600 mb-1">
                Drag & drop files here, or <span className="text-primary-600 font-medium">browse</span>
              </p>
              <p className="text-sm text-gray-500">
                Supports PDF, Excel, and CSV files
              </p>
            </div>
          )}
        </div>
      </div>

      {uploadedFiles.length === 0 && (
        <div className="text-center">
          <button
            onClick={loadSampleData}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium underline"
            disabled={isUploading}
          >
            Or load sample data to try the app
          </button>
        </div>
      )}
      
      {uploadedFiles.length > 0 && (
        <div className="text-center mt-2">
          <button
            onClick={async () => {
              try {
                const response = await fetch('http://localhost:8000/upload/debug/state')
                const data = await response.json()
                console.log('🔍 Backend state:', data)
                if (data.total_files === 0) {
                  toast.error(`Backend has 0 files! Please re-upload your ${uploadedFiles.length} files.`)
                } else {
                  toast.success(`Backend has ${data.total_files} files ready for analysis!`)
                }
              } catch (error) {
                toast.error('Could not check backend state')
              }
            }}
            className="text-xs text-gray-500 hover:text-gray-700 underline"
          >
            🔍 Check if backend has files
          </button>
        </div>
      )}

      <AnimatePresence>
        {uploadedFiles.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-2"
          >
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-700">Uploaded Files</h4>
              <p className="text-xs text-gray-500">
                {uploadedFiles.filter(f => f.type === 'pdf').length} transcript(s), {' '}
                {uploadedFiles.filter(f => ['excel', 'csv'].includes(f.type)).length} financial file(s)
              </p>
            </div>
            {uploadedFiles.map((file) => (
              <motion.div
                key={file.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border"
              >
                <div className="flex items-center space-x-3">
                  {getFileIcon(file.type)}
                  <div>
                    <p className="text-sm font-medium text-gray-900">{file.name}</p>
                    <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                
                <button
                  onClick={() => removeFile(file.id)}
                  className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </motion.div>
            ))}
            
            {uploadedFiles.length > 0 && (
              <>
                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-xs text-blue-800">
                    <strong>💡 Tip:</strong> You can upload any combination of files:
                    <br />• Transcript only → Analysis with default financial metrics
                    <br />• Financial data only → Analysis with default transcript
                    <br />• Both → Complete comprehensive analysis
                  </p>
                </div>
                
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full btn-primary mt-4"
                  disabled={isAnalyzing}
                  onClick={async () => {
                  try {
                    // Use a default company ID for now - in production this would come from user selection
                    await startAnalysis('default-company')
                    
                    // Wait longer to ensure sessionStorage is saved
                    await new Promise(resolve => setTimeout(resolve, 500))
                    
                    toast.success('Analysis completed! Redirecting to results...')
                    // Navigate to analysis page after successful analysis
                    setTimeout(() => {
                      router.push('/analysis')
                    }, 100)
                  } catch (error) {
                    const errorMsg = error instanceof Error ? error.message : 'Unknown error'
                    
                    // If no files were processed, try to seed sample data
                    if (errorMsg.includes('No files have been processed')) {
                      toast.loading('No files found. Loading sample data...')
                      try {
                        const seedResponse = await fetch('http://localhost:8000/upload/seed-sample-data', {
                          method: 'POST'
                        })
                        
                        if (seedResponse.ok) {
                          toast.success('Sample data loaded! Starting analysis...')
                          // Retry analysis with sample data
                          await startAnalysis('default-company')
                          toast.success('Analysis completed! Redirecting to results...')
                          setTimeout(() => {
                            router.push('/analysis')
                          }, 500)
                        } else {
                          toast.error('Failed to load sample data. Please upload files.')
                        }
                      } catch (seedError) {
                        toast.error('Failed to load sample data. Please upload files.')
                      }
                    } else {
                      toast.error('Analysis failed. Please try again.')
                    }
                  }
                }}
              >
                {isAnalyzing ? 'Analyzing...' : 'Start Analysis'}
              </motion.button>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
