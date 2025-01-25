import React, { useState } from 'react';

export default function History(props) {
  const info = props.info;
  const [currentPage, setCurrentPage] = useState(0); // Track the current page
  const recordsPerPage = 5; // Number of records to display per page

  // Calculate the index of the first and last record on the current page
  const startIndex = currentPage * recordsPerPage;
  const endIndex = startIndex + recordsPerPage;

  // Get the records to display on the current page
  const currentRecords = info.slice(startIndex, endIndex);

  // Function to handle page change
  const goToNextPage = () => {
    if (endIndex < info.length) {
      setCurrentPage(currentPage + 1);
    }
  };

  const goToPreviousPage = () => {
    if (startIndex > 0) {
      setCurrentPage(currentPage - 1);
    }
  };

  return (
    <div>
      {info && info.length > 0 ? (
        <div>
          <table className="w-full border-collapse border border-gray-400">
            <thead>
              <tr>
                <th className="border border-gray-400 px-4 py-2">Date</th>
                <th className="border border-gray-400 px-4 py-2">Acceleration</th>
                <th className="border border-gray-400 px-4 py-2">Velocity</th>
                <th className="border border-gray-400 px-4 py-2">Displacement</th>
                <th className="border border-gray-400 px-4 py-2">Richter</th>
              </tr>
            </thead>
            <tbody>
              {currentRecords.map((item, index) => (
                <tr key={index}>
                  <td className="border border-gray-400 px-4 py-2">{String(item.date).slice(0,10)}</td>
                  <td className="border border-gray-400 px-4 py-2">{item.acceleration}</td>
                  <td className="border border-gray-400 px-4 py-2">{item.velocity}</td>
                  <td className="border border-gray-400 px-4 py-2">{item.displacement}</td>
                  <td className="border border-gray-400 px-4 py-2">{String(item.richter).slice(0,5)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination Controls */}
          <div className="flex justify-between mt-4">
            <button
              onClick={goToPreviousPage}
              disabled={startIndex === 0}
              className="bg-sky-900 text-white px-4 py-2 disabled:bg-gray-300 disabled:text-black"
            >
              Previous
            </button>
            <button
              onClick={goToNextPage}
              disabled={endIndex >= info.length}
              className="bg-sky-900 text-white px-4 py-2 disabled:bg-gray-300 disabled:text-black"
            >
              Next
            </button>
          </div>
        </div>
      ) : (
        <p>No data available</p>
      )}
    </div>
  );
}
