import { useEffect, useState } from "react"
import axios from "axios"

const API_URL = "http://127.0.0.1:8000"

export default function LogsSummary() {
  const [summary, setSummary] = useState(null)

  const fetchSummary = async () => {
    try {
      const res = await axios.get(`${API_URL}/logs/summary`)
      if (res.data.total_predictions !== undefined) {
        setSummary(res.data)
      }
    } catch (err) {
      console.error("Logs fetch failed", err)
    }
  }

  useEffect(() => {
    fetchSummary()
    // Har 10 seconds pe refresh
    const interval = setInterval(fetchSummary, 10000)
    return () => clearInterval(interval)
  }, [])

  const stats = summary ? [
    { label: "Total predictions", value: summary.total_predictions, color: "text-blue-400" },
    { label: "Fraud detected", value: summary.fraud_detected, color: "text-red-400" },
    { label: "Legit transactions", value: summary.legit_detected, color: "text-green-400" },
    { label: "Avg fraud prob", value: `${(summary.avg_fraud_probability * 100).toFixed(1)}%`, color: "text-yellow-400" },
    { label: "High risk count", value: summary.high_risk_count, color: "text-orange-400" },
  ] : []

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-medium text-white">Live summary</h2>
        <button
          onClick={fetchSummary}
          className="text-xs text-blue-400 hover:text-blue-300 transition"
        >
          Refresh
        </button>
      </div>

      {!summary ? (
        <p className="text-sm text-gray-500">No predictions yet</p>
      ) : (
        <div className="space-y-3">
          {stats.map((stat) => (
            <div key={stat.label} className="flex items-center justify-between">
              <span className="text-xs text-gray-400">{stat.label}</span>
              <span className={`text-sm font-medium ${stat.color}`}>
                {stat.value}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}