export default function CountryList({ countries }) {
  
  return (
    <div className="space-y-3 mt-4">
      {countries.map((c) => (
        <div key={c.name} className="text-xs">
          {/* Country Label Row */}
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <span className={`fi fi-${c.flag.toLowerCase()}`}></span>
              <span className="text-gray-600">{c.name}</span>
            </div>
            <span className="text-gray-600 font-medium">{c.percent}%</span>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="h-2 rounded-full bg-blue-500 transition-all"
              style={{ width: `${c.percent}%` }}
            ></div>
          </div>
        </div>
      ))}
    </div>
  );
}
