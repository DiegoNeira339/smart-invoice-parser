"use client";

import { useState, useRef, useEffect } from "react";

const BACKEND_URL = "http://127.0.0.1:5000";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [isBackendOnline, setIsBackendOnline] = useState<boolean | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const checkBackendStatus = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/`, {
        headers: { "ngrok-skip-browser-warning": "69420" },
      });
      setIsBackendOnline(res.ok);
    } catch {
      setIsBackendOnline(false);
    }
  };

  useEffect(() => {
    checkBackendStatus();
    const interval = setInterval(checkBackendStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleProcess = async (selectedFile?: File) => {
    const fileToUpload = selectedFile || file;
    if (!fileToUpload) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", fileToUpload);

    try {
      const res = await fetch(`${BACKEND_URL}/api/process-invoice`, {
        method: "POST",
        headers: { "ngrok-skip-browser-warning": "69420" },
        body: formData,
      });

      if (!res.ok) throw new Error("Error al procesar el documento PDF");
      const json = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err.message || "No se pudo conectar con el servidor Flask");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateInvoice = async () => {
    setLoading(true);
    setError(null);
    setFile(null);

    try {
      const res = await fetch(`${BACKEND_URL}/api/generate-invoice`, {
        method: "POST",
        headers: { "ngrok-skip-browser-warning": "69420" },
      });

      if (!res.ok) throw new Error("Error al generar la factura dinámica");

      const json = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err.message || "No se pudo generar la factura");
    } finally {
      setLoading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      setFile(droppedFile);
      handleProcess(droppedFile);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 font-sans pb-16">
      <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl"></div>
        <div className="absolute top-1/3 -right-40 w-96 h-96 bg-blue-600/15 rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-6 pt-10 space-y-8">
        
        {/* Header con Estado Dinámico de Backend */}
        <header className="flex flex-col md:flex-row md:items-center md:justify-between border-b border-slate-800/80 pb-6 gap-4">
          <div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">
              ClienteCorp S.A. <span className="text-slate-400 font-normal">| Extractor de Facturas</span>
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Procesamiento automatizado de facturas vectoriales con Transformer NER y Módulo 11
            </p>
          </div>

          <div className="flex items-center gap-2">
            {isBackendOnline === null ? (
              <span className="px-3 py-1.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
                Verificando Conexión...
              </span>
            ) : isBackendOnline ? (
              <span className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800/60 shadow-sm">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Backend SQLite Conectado
              </span>
            ) : (
              <span className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-rose-950/80 text-rose-400 border border-rose-800/60 shadow-sm">
                <span className="w-2 h-2 rounded-full bg-rose-500"></span>
                Backend SQLite Desconectado
              </span>
            )}
          </div>
        </header>

        {/* Zona Interactiva Drag & Drop + Generación en 1-Clic */}
        <section className="space-y-4">
          <div
            onClick={() => fileInputRef.current?.click()}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`relative cursor-pointer border-2 border-dashed rounded-2xl p-10 text-center transition-all duration-200 backdrop-blur-sm ${
              dragActive
                ? "border-indigo-500 bg-indigo-950/40 scale-[1.01]"
                : "border-slate-800 bg-slate-900/50 hover:border-indigo-600/60 hover:bg-slate-900/80"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={(e) => {
                if (e.target.files?.[0]) {
                  const selected = e.target.files[0];
                  setFile(selected);
                  handleProcess(selected);
                }
              }}
              className="hidden"
            />

            <div className="flex flex-col items-center space-y-3 pointer-events-none">
              <div className="w-16 h-16 rounded-2xl bg-indigo-950/80 border border-indigo-800/50 flex items-center justify-center text-indigo-400 shadow-lg shadow-indigo-950/50">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>

              <div>
                <p className="text-base font-semibold text-slate-200">
                  {file ? `Seleccionado: ${file.name}` : "Arrastra una factura PDF aquí o haz clic para examinar"}
                </p>
                <p className="text-xs text-slate-400 mt-1">
                  Soporta facturas estructuradas (doc_001.pdf en adelante)
                </p>
              </div>
            </div>

            <div className="mt-6 flex flex-wrap justify-center gap-3">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}
                disabled={loading}
                className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-sm transition border border-slate-700 flex items-center gap-2 cursor-pointer"
              >
                <span>Seleccionar PDF</span>
              </button>

              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  handleGenerateInvoice();
                }}
                disabled={loading}
                className="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm transition shadow-lg shadow-emerald-600/30 flex items-center gap-2 cursor-pointer"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Procesando...</span>
                  </>
                ) : (
                  <>
                    <span>✨ Generar Boleta Nueva</span>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                    </svg>
                  </>
                )}
              </button>
            </div>
          </div>
        </section>

        {error && (
          <div className="p-4 rounded-xl bg-rose-950/50 border border-rose-800/80 text-rose-300 text-sm flex items-center gap-3">
            <svg className="w-5 h-5 text-rose-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>{error}</div>
          </div>
        )}

        {/* Despliegue de Resultados */}
        {data && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-fadeIn">
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-5 backdrop-blur-sm shadow-xl">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  Cabecera & Validación Módulo 11
                </h2>
                <span className="text-xs font-mono text-slate-400 bg-slate-800 px-2.5 py-1 rounded-md">
                  {data.filename}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80">
                  <span className="text-xs text-slate-400 block font-medium">N° Factura</span>
                  <span className="text-sm font-bold text-indigo-300 font-mono mt-0.5 block">
                    {data.normalized_data.factura_num || "N/A"}
                  </span>
                </div>
                <div className="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80">
                  <span className="text-xs text-slate-400 block font-medium">Fecha Emisión (ISO)</span>
                  <span className="text-sm font-semibold text-slate-200 mt-0.5 block font-mono">
                    {data.normalized_data.fecha || "N/A"}
                  </span>
                </div>
              </div>

              <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Empresa Emisora</span>
                  <span className={`px-2.5 py-0.5 text-xs font-bold rounded-full font-mono ${
                    data.validations.rut_empresa_valido
                      ? "bg-emerald-950 text-emerald-400 border border-emerald-800/60"
                      : "bg-rose-950 text-rose-400 border border-rose-800/60"
                  }`}>
                    RUT: {data.normalized_data.empresa_rut} {data.validations.rut_empresa_valido ? "✓ Válido" : "✗ Inválido"}
                  </span>
                </div>
                <p className="text-sm font-bold text-slate-100">{data.normalized_data.empresa_nombre}</p>
                <p className="text-xs text-slate-400">📍 {data.normalized_data.empresa_direccion}</p>
              </div>

              <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Receptor / Cliente</span>
                  <span className={`px-2.5 py-0.5 text-xs font-bold rounded-full font-mono ${
                    data.validations.rut_cliente_valido
                      ? "bg-emerald-950 text-emerald-400 border border-emerald-800/60"
                      : "bg-rose-950 text-rose-400 border border-rose-800/60"
                  }`}>
                    RUT: {data.normalized_data.cliente_rut} {data.validations.rut_cliente_valido ? "✓ Válido" : "✗ Inválido"}
                  </span>
                </div>
                <p className="text-sm font-bold text-slate-100">{data.normalized_data.cliente_nombre}</p>
                <p className="text-xs text-slate-400">📍 {data.normalized_data.cliente_direccion}</p>
              </div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-5 backdrop-blur-sm shadow-xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    Resumen Financiero & Ítems
                  </h2>
                  <span className="text-xs text-emerald-400 font-semibold bg-emerald-950/60 border border-emerald-800 px-2 py-0.5 rounded">
                    SQLite Synced
                  </span>
                </div>

                <div className="mt-4 space-y-2">
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                    Detalle de Productos / Servicios ({data.items.length})
                  </span>
                  <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                    {data.items.map((it: any, idx: number) => (
                      <div key={idx} className="bg-slate-950/80 p-3 rounded-xl border border-slate-800/80 flex items-center justify-between">
                        <div>
                          <p className="text-xs font-bold text-slate-200">{it.producto}</p>
                          <p className="text-[11px] text-slate-400">
                            Cant: <span className="text-indigo-400 font-bold">{it.cantidad}</span> | Unitario: ${it.precio_unitario?.toLocaleString("es-CL")}
                          </p>
                        </div>
                        <span className="text-xs font-bold font-mono text-slate-100 bg-slate-900 px-2.5 py-1 rounded-md border border-slate-800">
                          ${it.subtotal_item?.toLocaleString("es-CL")}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 mt-4">
                <div className="flex justify-between text-xs text-slate-400">
                  <span>Monto Neto:</span>
                  <span className="font-mono text-slate-200">${data.normalized_data.total_neto?.toLocaleString("es-CL")}</span>
                </div>
                <div className="flex justify-between text-xs text-slate-400">
                  <span>IVA (19%):</span>
                  <span className="font-mono text-slate-200">${data.normalized_data.iva?.toLocaleString("es-CL")}</span>
                </div>
                <div className="flex justify-between text-base font-extrabold text-white border-t border-slate-800 pt-2 mt-1">
                  <span className="text-indigo-400">Total Final:</span>
                  <span className="font-mono text-emerald-400 text-lg">${data.normalized_data.total_final?.toLocaleString("es-CL")}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}