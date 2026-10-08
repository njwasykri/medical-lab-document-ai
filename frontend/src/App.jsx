import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [ocrResult, setOcrResult] = useState("");
  const [result, setResult] = useState("");
  const [vlmMissedResult, setVlmMissedResult] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setOcrResult("");
    setResult("");
    setVlmMissedResult("");
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a PDF file first.");
      return;
    }

    setLoading(true);
    setOcrResult("");
    setResult("");
    setVlmMissedResult("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      setOcrResult(data.ocr_text);

      const cleanedResult = data.qwen_result.replace(/\\\|/g, "|");
      setResult(cleanedResult);

      setVlmMissedResult(data.vlm_missed_result);

      // Debug: check that table rows are separated by real newlines
      console.log(JSON.stringify(data.qwen_result));

      setResult(
        data.qwen_result
          .replace(/\\\|/g, "|")
          .replace(/\\n/g, "\n")
      );
    } catch (error) {
      setResult("Error: " + error.message);
    }

    setLoading(false);
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Document AI</h1>
        </div>
      </header>

      <main className="container">
        <section className="upload-card">
          <div className="upload-icon">📄</div>

          <h2>Upload Your Document</h2>

          <p>
            Upload a PDF document and let AI extract the information for you.
          </p>

          <label className="file-button">
            Choose PDF
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
            />
          </label>

          {file && (
            <div className="file-info">
              <span>📎</span>
              <div>
                <strong>{file.name}</strong>
                <p>PDF document selected</p>
              </div>
            </div>
          )}

          <button
            className="extract-button"
            onClick={handleUpload}
            disabled={loading}
          >
            {loading ? "Processing..." : "Extract Data"}
          </button>
        </section>

        {loading && (
          <section className="status-card">
            <div className="spinner"></div>
            <div>
              <h3>AI is processing your document</h3>
              <p>
                The document is being analyzed using OCR and AI.
                This may take a little while.
              </p>
            </div>
          </section>
        )}

        {ocrResult && !loading && (
  <section className="result-card">
    <div className="result-header">
      <div>
        <h2>OCR Result</h2>
        <p>Text extracted from the document using OCR</p>
      </div>
    </div>

    <div className="result-content">
      <pre>{ocrResult}</pre>
    </div>
  </section>
)}

        {result && !loading && (
          <section className="result-card">
            <div className="result-header">
              <div>
                <h2>Extraction Result</h2>
                <p>Information extracted from your document</p>
              </div>
            </div>

            <div className="result-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {result}
              </ReactMarkdown>
            </div>
          </section>
        )}

        {vlmMissedResult && !loading && (
  <section className="result-card">
    <div className="result-header">
      <div>
        <h2>OCR Missed Information Extracted by VLM</h2>
        <p>
          Information missed, incomplete, or incorrectly extracted by OCR
          and identified using VLM
        </p>
      </div>
    </div>

    <div className="result-content">
      <pre>{vlmMissedResult}</pre>
    </div>
  </section>
)}
      </main>
    </div>
  );
}

export default App;
