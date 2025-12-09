import { FiChevronDown } from "react-icons/fi";
import CountryList from "./CountryList";
import WorldMap from "./WorldMap";

export default function CountriesCard({ range, countryStats, mapData }) {

  return (
    <div className="rounded-2xl border bg-white p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Top Countries</h3>

        {/* <button className="flex items-center gap-1 bg-gray-100 px-3 py-1.5 rounded-lg text- text-black">
          {range} <FiChevronDown />
        </button> */}
      </div>

      {/* World Map */}
      <div className="border-b pb-4 mb-4">
        <WorldMap data={mapData} />
      </div>

      {/* Country List */}
      <CountryList countries={countryStats} />
    </div>
  );
}
