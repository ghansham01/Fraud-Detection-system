import { useState } from "react"
import axios from "axios"

const API_URL = "http://127.0.0.1:8000"

const FRAUD_SAMPLE = {
  Time: 406.0, Amount: 149.62,
  V1: -1.359807, V2: -0.072781, V3: 2.536347,  V4: 1.378155,
  V5: -0.338321, V6: 0.462388,  V7: 0.239599,  V8: 0.098698,
  V9: 0.363787,  V10: 0.090794, V11: -0.551600, V12: -0.617801,
  V13: -0.991390, V14: -0.311169, V15: 1.468177, V16: -0.470401,
  V17: 0.207971, V18: 0.025791, V19: 0.403993,  V20: 0.251412,
  V21: -0.018307, V22: 0.277838, V23: -0.110474, V24: 0.066928,
  V25: 0.128539, V26: -0.189115, V27: 0.133558,  V28: -0.021053
}

const LEGIT_SAMPLE = {
  Time: 1000.0, Amount: 25.00,
  V1: 1.191857,  V2: 0.266151,  V3: 0.166480,  V4: 0.448154,
  V5: 0.060018,  V6: -0.082361, V7: -0.078803, V8: 0.085102,
  V9: -0.255425, V10: -0.166974, V11: 1.612727, V12: 1.065235,
  V13: 0.489095, V14: -0.143772, V15: 0.635558, V16: 0.463917,
  V17: -0.114805, V18: -0.183361, V19: -0.145783, V20: -0.069083,
  V21: -0.225775, V22: -0.638672, V23: 0.101288, V24: -0.339846,
  V25: 0.167170, V26: 0.125895,  V27: -0.008983, V28: 0.014724
}

// Empty form — saare fields 0
const EMPTY_FORM = Object.fromEntries([
  "Time", "Amount",
  ...Array.from({ length: 28 }, (_, i) => `V${i + 1}`)
].map(k => [k, ""]))

export default function PredictForm({ setResult, setLoading, setError, loading }) {
  const [form, setForm] = useState(EMPTY_FORM)
  const [mode, setMode] = useState("simple")

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const loadSample = (type) => {
    const sample = type === "fraud" ? FRAUD_SAMPLE : LEGIT_SAMPLE
    // Numbers ko string mein convert karo — input fields ke liye
    const stringified = Object.fromEntries(
      Object.entries(sample).map(([k, v]) => [k, String(v)])
    )
    setForm(stringified)
  }

  const handleSubmit = async () => {
    setError(null)
    setResult(null)
    setLoading(true)

    try {
      // V fields ke liye default value 0 use karo agar empty ho
      const payload = Object.fromEntries(
        Object.entries(form).map(([k, v]) => {
          if (v === "" || v === null || v === undefined) {
            return [k, k.startsWith("V") ? 0.0 : 0.0]  // Default 0 for V fields
          }
          return [k, parseFloat(v)]
        })
      )

      // NaN check (excluding V fields which default to 0)
      const nanFields = Object.entries(payload)
        .filter(([k, v]) => isNaN(v) && !k.startsWith("V"))
        .map(([k]) => k)

      if (nanFields.length > 0) {
        setError(`Invalid numbers: ${nanFields.join(", ")}`)
        setLoading(false)
        return
      }

      const res = await axios.post(`${API_URL}/predict`, payload)
      setResult(res.data)

    } catch (err) {
      if (err.response?.status === 422) {
        setError("422 — Input validation failed. Sample load karke try karo.")
      } else {
        setError(err.response?.data?.detail || "API connect nahi ho rahi")
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-medium text-white">Transaction input</h2>
        <div className="flex gap-2">
          <button
            onClick={() => loadSample("fraud")}
            className="text-xs px-3 py-1.5 rounded-lg bg-red-950 text-red-400 border border-red-800 hover:bg-red-900 transition"
          >
            Load fraud sample
          </button>
          <button
            onClick={() => loadSample("legit")}
            className="text-xs px-3 py-1.5 rounded-lg bg-green-950 text-green-400 border border-green-800 hover:bg-green-900 transition"
          >
            Load legit sample
          </button>
        </div>
      </div>

      {/* Time + Amount */}
      <div className="grid grid-cols-2 gap-4">
        {["Time", "Amount"].map((field) => (
          <div key={field} className="space-y-1.5">
            <label className="text-xs text-gray-400">{field}</label>
            <input
              name={field}
              value={form[field]}
              onChange={handleChange}
              placeholder={field === "Time" ? "406.0" : "149.62"}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-blue-500"
            />
          </div>
        ))}
      </div>

      {/* V fields toggle */}
      <button
        onClick={() => setMode(mode === "simple" ? "advanced" : "simple")}
        className="text-xs text-blue-400 hover:text-blue-300 transition"
      >
        {mode === "simple"
          ? `Show V1–V28 fields ${Object.entries(form).filter(([k, v]) => k.startsWith("V") && v !== "").length}/28 filled`
          : "Hide V1–V28 fields"
        }
      </button>

      {/* V1-V28 grid */}
      {mode === "advanced" && (
        <div className="grid grid-cols-4 gap-2">
          {Array.from({ length: 28 }, (_, i) => `V${i + 1}`).map((v) => (
            <div key={v} className="space-y-1">
              <label className="text-xs text-gray-500">{v}</label>
              <input
                name={v}
                value={form[v]}
                onChange={handleChange}
                placeholder="0.0"
                className={`w-full bg-gray-800 border rounded-lg px-2 py-1.5 text-xs text-white placeholder-gray-600 focus:outline-none focus:border-blue-500 ${
                  form[v] === ""
                    ? "border-gray-700"
                    : "border-green-700"
                }`}
              />
            </div>
          ))}
        </div>
      )}

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={loading}
        className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-sm font-medium text-white transition"
      >
        {loading ? "Analyzing..." : "Analyze transaction"}
      </button>
    </div>
  )
}