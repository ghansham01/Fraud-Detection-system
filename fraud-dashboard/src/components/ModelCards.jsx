export default function ModelCards({ models }) {
  return (
    <div>
      <h3 className="text-sm font-medium text-gray-400 mb-3">
        Individual model results
      </h3>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {models.map((model) => {
          const isFraud = model.prediction === "Fraud"
          return (
            <div
              key={model.model_name}
              className="bg-gray-900 border border-gray-800 rounded-xl p-4 space-y-3"
            >
              <p className="text-xs text-gray-400 font-medium">
                {model.model_name}
              </p>

              <p className={`text-xl font-semibold ${isFraud ? "text-red-400" : "text-green-400"
                }`}>
                {model.prediction}
              </p>

              {/* Probability bar */}
              <div className="space-y-1">
                <div className="w-full bg-gray-800 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full ${isFraud ? "bg-red-500" : "bg-green-500"
                      }`}
                    style={{ width: `${model.probability * 100}%` }}
                  />
                </div>
                <p className="text-xs text-gray-500">
                  {(model.probability * 100).toFixed(1)}% probability
                </p>
              </div>

              <span className={`text-xs px-2 py-0.5 rounded-full border inline-block ${model.confidence === "High"
                  ? "text-red-400 bg-red-950 border-red-800"
                  : model.confidence === "Medium"
                    ? "text-yellow-400 bg-yellow-950 border-yellow-800"
                    : "text-green-400 bg-green-950 border-green-800"
                }`}>
                {model.confidence} confidence
              </span>

            </div>
          )
        })}
      </div>
    </div>
  )
}