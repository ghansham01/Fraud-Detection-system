import { useState } from "react"
import PredictForm from "./components/PredictForm"
import ResultCard from "./components/ResultCard"
import ModelCards from "./components/ModelCards"
import LogsSummary from "./components/LogsSummary"


function App() {
  const [result, setresult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <div className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div>
          <h1 className="text-xl font-semibold text-white">
            Fraud Detection System
          </h1>

          <p className="text-sm text-gray-400">
            Ensemble ML — 4 models voting on every transaction
          </p>


        </div>

        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400"></div>
          <span className="text-sm text-gray-400">API Online</span>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8 space-y-8">

        {/* Top row — Form + Summary */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <PredictForm
              setResult={setResult}
              setLoading={setLoading}
              setError={setError}
              loading={loading}
            />
          </div>
          <div>
            <LogsSummary />
          </div>
        </div>


        {/* Error */}
        {error && (
          <div className="bg-red-500 border border-red-600 rounded-xl p-4">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6">
            <ResultCard result={result} />
            <ModelCards models={result.models} />
          </div>
        )}
      </div>
    </div>
  )
}

export default App