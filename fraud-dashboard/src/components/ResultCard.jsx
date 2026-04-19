import React from 'react'

function ResultCard({ result }) {
  const isFraud = result.final_verdict === "Fraud"

  const riskColors = {
    High: "text-red-400 bg-red-950 border-red-800",
    Medium: "text-yellow-400 bg-yellow-950 border-yellow-800",
    Low: "text-green-400 bg-green-950 border-green-800",
  }


  return (
    <div className={`border rounded-xl p-6 space-y-4 ${isFraud
      ? "bg-red-950 border-red-800"
      : "bg-green-950 border-green-800"
      }`}>

      <div className="flex items-center justify-between">
        <div >
          <p className="text-sm text-gray-400 mb-1">Final verdict</p>
          <h2 className={`text-3xl font-semibold ${isFraud ? "text-red-400" : "text-green-400"
            }`}>
            {result.final_verdict}</h2>
        </div>

        <div className=' text-right'>
          <p className="text-sm text-gray-400 mb-1">Fraud probability</p>
          <p className={`text-3xl font-semibold ${isFraud ? "text-red-400" : "text-green-400"
            }`}>
            {(result.fraud_probability * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      
      {/* Probability bar */}
      <div className="w-full bg-gray-800 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all ${isFraud ? "bg-red-500" : "bg-green-500"
            }`}
          style={{ width: `${result.fraud_probability * 100}%` }}
        />
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className={`text-xs px-3 py-1 rounded-full border font-medium ${riskColors[result.risk_level]}`}>
            {result.risk_level} risk
          </span>
          <span className="text-xs text-gray-400">
            {result.agreement}
          </span>
        </div>
        <p className="text-sm text-gray-400">
          Amount: <span className="text-white font-medium">
            ${result.transaction_amount.toFixed(2)}
          </span>
        </p>
      </div>

    </div>

  )
}

export default ResultCard