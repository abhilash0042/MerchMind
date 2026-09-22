import { useState, useRef, useEffect } from "react";
import { Upload, FileSpreadsheet, AlertCircle, CheckCircle2, BarChart3, List, Database, LayoutDashboard, Layers } from "lucide-react";
import * as xlsx from "xlsx";
import { useNavigate } from "react-router";
import { apiClient, ensureSeller } from "../services/api";

export function DataImportPage() {
  const [hasExistingData, setHasExistingData] = useState<boolean | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [parsedData, setParsedData] = useState<any[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [detectedSheets, setDetectedSheets] = useState<string[]>([]);  // Bug 4: track all sheet names
  const [isProcessing, setIsProcessing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let isMounted = true;
    const timeoutId = setTimeout(() => {
      if (isMounted && hasExistingData === null) {
        console.warn("Database check timed out, allowing manual upload.");
        setHasExistingData(false);
      }
    }, 10000); // 10s timeout

    async function checkExistingData() {
      try {
        const sellerId = await ensureSeller();
        // Add a small delay to avoid race conditions with backend startup
        // Bug 12 Fix: endpoint was /analytics/dashboard (404) — correct endpoint is /analytics/dashboard/summary
        const data = await apiClient.get(`/analytics/dashboard/summary?seller_id=${sellerId}&days=365`);
        if (isMounted) {
          if (data && data.total_orders > 0) {
            setHasExistingData(true);
          } else {
            setHasExistingData(false);
          }
        }
      } catch (err) {
        console.error("Failed to check existing data:", err);
        if (isMounted) setHasExistingData(false);
      } finally {
        clearTimeout(timeoutId);
      }
    }
    checkExistingData();
    return () => { isMounted = false; clearTimeout(timeoutId); };
  }, []);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file: File) => {
    const validTypes = [
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
      "application/vnd.ms-excel",
      "text/csv"
    ];
    
    if (!validTypes.includes(file.type) && !file.name.match(/\.(xlsx|xls|csv)$/)) {
      setError("Please upload a valid Excel (.xlsx, .xls) or CSV file.");
      return;
    }

    setFile(file);
    setError(null);
    setIsProcessing(true);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = e.target?.result;
        // Bug 3 Fix: readAsArrayBuffer produces ArrayBuffer, not a binary string.
        // Must use type: "array" to match. Using type: "binary" with ArrayBuffer caused silent parse errors.
        const workbook = xlsx.read(data, { type: "array", cellDates: true });

        // Bug 4 Fix: detect ALL sheet names (for multi-sheet workbooks like Orders/Inventory/etc.)
        // Previously only Sheet 1 was parsed, giving no indication other sheets exist.
        const allSheets = workbook.SheetNames;
        setDetectedSheets(allSheets);

        // Preview from the first sheet only (for table display)
        const firstSheetName = allSheets[0];
        const worksheet = workbook.Sheets[firstSheetName];
        
        // Convert sheet to JSON — dateNF formats Date objects as readable strings
        const jsonData = xlsx.utils.sheet_to_json(worksheet, { defval: "", dateNF: "yyyy-mm-dd" });
        
        if (jsonData.length > 0) {
          setColumns(Object.keys(jsonData[0] as object));
          setParsedData(jsonData);
        } else {
          setError("The uploaded file appears to be empty.");
        }
      } catch (err) {
        console.error(err);
        setError("Failed to parse the file. Ensure it's a valid spreadsheet.");
      } finally {
        setIsProcessing(false);
      }
    };
    
    reader.onerror = () => {
      setError("An error occurred while reading the file.");
      setIsProcessing(false);
    };

    reader.readAsArrayBuffer(file);
  };

  const triggerUpload = () => {
    inputRef.current?.click();
  };

  const resetUpload = () => {
    setFile(null);
    setParsedData([]);
    setColumns([]);
    setDetectedSheets([]);  // Bug 4: also reset sheets on new upload
    setUploadSuccess(false);
    setError(null);
  };

  const submitToDatabase = async () => {
    if (!file) return;
    
    setIsUploading(true);
    setError(null);
    
    try {
      // Make sure we have a seller before uploading
      const sellerId = await ensureSeller();

      const formData = new FormData();
      formData.append("seller_id", sellerId);
      formData.append("file", file);
      
      // Send to the /full endpoint which processes multiple sheets
      const response = await apiClient.postForm("/upload/full", formData);
      
      console.log("Upload successful:", response);
      setUploadSuccess(true);
      setHasExistingData(true); // Update state to show existing data view
    } catch (err: any) {
      console.error("Upload error:", err);
      setError(err.message || "Failed to upload data to the backend database.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Data Import</h1>
          <p className="text-sm text-gray-600 mt-1">
            Upload and analyze your custom datasets instantly.
          </p>
        </div>
        {hasExistingData === false && parsedData.length > 0 && (
          <div className="flex gap-3">
            <button 
              onClick={resetUpload}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 font-medium transition-colors"
            >
              Upload New File
            </button>
            {!uploadSuccess && (
              <button 
                onClick={submitToDatabase}
                disabled={isUploading}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-xl hover:bg-purple-700 disabled:bg-purple-400 font-medium transition-colors shadow-sm"
              >
                <Database className="w-4 h-4" />
                {isUploading ? "Uploading..." : "Save to Database"}
              </button>
            )}
          </div>
        )}
      </div>

      {hasExistingData === null && (
        <div className="w-full max-w-xl mx-auto mt-20 text-center">
          <div className="inline-block animate-spin w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full mb-4"></div>
          <p className="text-gray-600 font-medium">Checking database status...</p>
        </div>
      )}

      {hasExistingData === true && (
        <div className="w-full max-w-3xl mx-auto mt-12 bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
          <div className="p-12 text-center">
            <div className="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
              {uploadSuccess ? <CheckCircle2 className="w-10 h-10" /> : <Database className="w-10 h-10" />}
            </div>
            <h3 className="text-2xl font-semibold text-gray-900 mb-3">
              {uploadSuccess ? "Upload Successful!" : "Active Dataset Running"}
            </h3>
            <p className="text-gray-500 mb-10 max-w-md mx-auto text-lg">
              {uploadSuccess 
                ? "Your data has been successfully imported to the CommercePulse database. The AI is now analyzing your records."
                : "Your CommercePulse database is populated and ready. The dashboard and AI insights are actively analyzing your data."}
            </p>
            <div className="flex gap-4 justify-center">
              <button 
                onClick={() => navigate("/")}
                className="px-8 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 font-medium transition-colors shadow-sm flex items-center gap-2"
              >
                <LayoutDashboard className="w-5 h-5" />
                Go to Dashboard
              </button>
              <button 
                onClick={() => {
                  setHasExistingData(false);
                  resetUpload();
                }}
                className="px-8 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 font-medium transition-colors"
              >
                Upload New Dataset
              </button>
            </div>
          </div>
        </div>
      )}

      {hasExistingData === false && !file && (
        <div 
          className={`w-full max-w-3xl mx-auto mt-12 bg-white rounded-2xl border-2 border-dashed transition-all duration-200 ${
            dragActive ? "border-purple-500 bg-purple-50" : "border-gray-300 hover:border-purple-400"
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
            <div className="w-16 h-16 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center mb-6">
              <Upload className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Upload your spreadsheet</h3>
            <p className="text-gray-500 mb-8 max-w-md">
              Excel with Orders, Inventory, Pricing, Traffic, Logistics. Settlements and Bank sheets are optional — if missing, we build Brew Boulevard Razorpay cash files from Orders.
            </p>
            <input 
              ref={inputRef}
              type="file" 
              className="hidden" 
              accept=".xlsx,.xls,.csv" 
              onChange={handleChange} 
            />
            <button 
              onClick={triggerUpload}
              className="px-6 py-3 bg-purple-600 text-white rounded-xl hover:bg-purple-700 font-medium transition-colors shadow-sm"
            >
              Select File to Upload
            </button>

            {error && (
              <div className="mt-6 flex items-center gap-2 text-red-600 bg-red-50 px-4 py-3 rounded-lg text-sm">
                <AlertCircle className="w-4 h-4" />
                {error}
              </div>
            )}
          </div>
        </div>
      )}

      {hasExistingData === false && isProcessing && (
        <div className="w-full max-w-xl mx-auto mt-20 text-center">
          <div className="inline-block animate-spin w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full mb-4"></div>
          <p className="text-gray-600 font-medium">Analyzing document and extracting insights...</p>
        </div>
      )}

      {hasExistingData === false && isUploading && (
        <div className="w-full max-w-xl mx-auto mt-20 text-center animate-in fade-in duration-500">
          <div className="inline-block animate-spin w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full mb-6"></div>
          <h3 className="text-2xl font-semibold text-gray-900 mb-2">Uploading to Database...</h3>
          <p className="text-gray-600 font-medium text-lg">
            Please wait while we securely store and index your records. 
            <br/><span className="text-sm text-gray-400 mt-2 block">This may take a minute for large datasets.</span>
          </p>
        </div>
      )}

      {hasExistingData === false && file && !isProcessing && !isUploading && parsedData.length > 0 && (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
          
          {/* Analysis Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
             <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 flex items-center gap-4">
               <div className="p-3 bg-purple-50 text-purple-600 rounded-xl">
                 <FileSpreadsheet className="w-6 h-6" />
               </div>
               <div>
                 <p className="text-sm text-gray-500 font-medium">Filename</p>
                 <p className="text-lg font-semibold text-gray-900 truncate max-w-[200px]" title={file.name}>{file.name}</p>
               </div>
             </div>
             
             <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 flex items-center gap-4">
               <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
                 <List className="w-6 h-6" />
               </div>
               <div>
                 <p className="text-sm text-gray-500 font-medium">Records Extracted</p>
                 <p className="text-2xl font-semibold text-gray-900">{parsedData.length.toLocaleString()}</p>
               </div>
             </div>

             <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 flex items-center justify-between">
               <div className="flex items-center gap-4">
                 <div className="p-3 bg-green-50 text-green-600 rounded-xl">
                   <BarChart3 className="w-6 h-6" />
                 </div>
                 <div>
                   <p className="text-sm text-gray-500 font-medium">Data Dimensions</p>
                   <p className="text-lg font-semibold text-gray-900">{columns.length} columns</p>
                 </div>
               </div>
               <div className="flex items-center text-green-600 text-sm font-medium gap-1 bg-green-50 px-3 py-1 rounded-full">
                 <CheckCircle2 className="w-4 h-4" /> Validated
               </div>
             </div>
          </div>

          {/* Bug 4 Fix: show detected sheet names for multi-sheet workbooks */}
          {detectedSheets.length > 1 && (
            <div className="mb-6 flex items-start gap-3 bg-blue-50 border border-blue-100 px-4 py-3 rounded-xl">
              <Layers className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-semibold text-blue-800">{detectedSheets.length} sheets detected — all will be uploaded</p>
                <p className="text-xs text-blue-600 mt-0.5">{detectedSheets.join(" · ")}</p>
                <p className="text-xs text-blue-500 mt-0.5">Preview below shows Sheet 1 only.</p>
              </div>
            </div>
          )}

          {error && (
            <div className="mb-6 flex items-center gap-2 text-red-600 bg-red-50 px-4 py-4 rounded-xl border border-red-100 font-medium">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              {error}
            </div>
          )}

          {/* Data Preview Table */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            <div className="p-6 border-b border-gray-100 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Data Preview</h3>
                <p className="text-sm text-gray-500 mt-1">Showing the first 10 recorded entries.</p>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50/80 border-b border-gray-200">
                  <tr>
                    {columns.map((col, idx) => (
                      <th key={idx} className="text-left px-6 py-4 text-xs font-semibold text-gray-600 uppercase tracking-wider whitespace-nowrap">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {parsedData.slice(0, 10).map((row, rowIdx) => (
                    <tr key={rowIdx} className="hover:bg-gray-50/50 transition-colors">
                      {columns.map((col, colIdx) => (
                        <td key={colIdx} className="px-6 py-4 text-sm text-gray-700 whitespace-nowrap max-w-[200px] truncate">
                          {row[col] instanceof Date
                            ? row[col].toISOString().split("T")[0]
                            : (row[col]?.toString() || "-")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
