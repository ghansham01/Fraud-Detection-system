import { useState } from "react"
import axios from "axios"

const API_URL = "http://127.0.0.1:8000"

const TRANSACTION_TYPES = [
  { value: "online",   label: "Online",   icon: "" },
  { value: "in-store", label: "In-store", icon: "" },
  { value: "atm",      label: "ATM",      icon: "" },
]

export default function PredictForm({ setResult, setLoading, setError, loading }) {
  const [amount, setAmount]   = useState("")
  const [hour, setHour]       = useState("12")
  const [type, setType]       = useState("online")

  const handleSubmit = async () => {
    setError(null)
    setResult(null)
    setLoading(true)

    try {
      if (!amount || isNaN(parseFloat(amount))) {
        setError("Amount enter karo")
        setLoading(false)
        return
      }

      const payload = {
        amount:           parseFloat(amount),
        time_hour:        parseFloat(hour),
        transaction_type: type
      }

      const res = await axios.post(`${API_URL}/predict/simple`, payload)
      setResult(res.data)

    } catch (err) {
      setError(err.response?.data?.detail || "API connect nahi ho rahi")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-6">
      <div>
        <h2 className="text-base font-medium text-white">Transaction details</h2>
        <p className="text-xs text-gray-500 mt-0.5">
          Sirf basic details fill karo — AI baaki automatically calculate karega
        </p>
      </div>

      {/* Amount */}
      <div className="space-y-2">
        <label className="text-sm text-gray-400">Transaction amount</label>
        <div className="relative">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">$</span>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.00"
            min="0"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-7 pr-4 py-3 text-white text-sm placeholder-gray-600 focus:outline-none focus:border-blue-500"
          />
        </div>
        {/* Amount risk hint */}
        {amount && (
          <p className={`text-xs ${
            parseFloat(amount) > 5000 ? "text-red-400" :
            parseFloat(amount) > 1000 ? "text-yellow-400" :
            "text-green-400"
          }`}>
            {parseFloat(amount) > 5000 ? "Very high amount — higher fraud risk"  :
             parseFloat(amount) > 1000 ? "High amount — moderate fraud risk"     :
             "Normal amount range"}
          </p>
        )}
      </div>

      {/* Time slider */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <label className="text-sm text-gray-400">Time of transaction</label>
          <span className={`text-sm font-medium ${
            parseInt(hour) < 6 || parseInt(hour) > 22
              ? "text-red-400"
              : "text-green-400"
          }`}>
            {String(hour).padStart(2, "0")}:00
            {parseInt(hour) < 6 || parseInt(hour) > 22
              ? " — Late night (suspicious)"
              : " — Normal hours"}
          </span>
        </div>
        <input
          type="range"
          min="0"
          max="23"
          value={hour}
          onChange={(e) => setHour(e.target.value)}
          className="w-full accent-blue-500"
        />
        <div className="flex justify-between text-xs text-gray-600">
          <span>12 AM</span>
          <span>6 AM</span>
          <span>12 PM</span>
          <span>6 PM</span>
          <span>11 PM</span>
        </div>
      </div>

      {/* Transaction type */}
      <div className="space-y-2">
        <label className="text-sm text-gray-400">Transaction type</label>
        <div className="grid grid-cols-3 gap-2">
          {TRANSACTION_TYPES.map((t) => (
            <button
              key={t.value}
              onClick={() => setType(t.value)}
              className={`py-2.5 rounded-lg text-sm border transition ${
                type === t.value
                  ? "bg-blue-600 border-blue-500 text-white"
                  : "bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-500"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Quick test buttons */}
      <div className="space-y-2">
        <label className="text-xs text-gray-500">Quick test scenarios</label>
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => { setAmount("15000"); setHour("3"); setType("online") }}
            className="text-xs px-3 py-2 rounded-lg bg-red-950 text-red-400 border border-red-800 hover:bg-red-900 transition"
          >
            Suspicious scenario
          </button>
          <button
            onClick={() => { setAmount("85"); setHour("14"); setType("in-store") }}
            className="text-xs px-3 py-2 rounded-lg bg-green-950 text-green-400 border border-green-800 hover:bg-green-900 transition"
          >
            Normal scenario
          </button>
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading || !amount}
        className="w-full py-3 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-sm font-medium text-white transition"
      >
        {loading ? "Analyzing transaction..." : "Analyze transaction"}
      </button>
    </div>
  )
}