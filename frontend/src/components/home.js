import React, { useState, useEffect } from 'react';
import Station_info from './station_info';
import Introduction from './Introduction';

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const [colapse_all, colapse_all_setter] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [data, setData] = useState([]);
  const stationsPerPage = 5;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:3001/stations/');
        const result = await response.json();
        console.log("Fetched data:", result.data); // Log fetched data for debugging
        setData(result.data);
      } catch (error) {
        console.error('Error fetching station data:', error);
      }
    };

    fetchData(); // Call the fetch function
  }, []);

  // Filter the data based on the search query
  const filteredData = data.filter((item) => {
    return item.location.toLowerCase().includes(searchQuery.toLowerCase());
  });

  // Calculate the index of the first and last item on the current page
  const indexOfLastStation = currentPage * stationsPerPage;
  const indexOfFirstStation = indexOfLastStation - stationsPerPage;

  // Get the current stations to display based on the page
  const currentStations = filteredData.slice(indexOfFirstStation, indexOfLastStation);
 
  // Handle next and previous page
  const nextPage = () => {
    if (currentPage < Math.ceil(filteredData.length / stationsPerPage)) {
      setCurrentPage(currentPage + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  return (
    <div>
      <Introduction></Introduction>
      <div className="m-2 bg-gray-300 pb-2 h-full">
        <div className="m-2 text-2xl text-white text-center flex justify-between py-2 items-center gap-16 search_bar">
          <p className="text-sky-900">Available Stations</p>
          <input
            type="text"
            placeholder="Search by location"
            className="text-xl h-10 w-1/2 text-black rounded-full"
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button
            className="flex items-center bg-sky-900 p-2 text-base hover:bg-gray-800"
            onClick={() => {
              colapse_all_setter(!colapse_all);
            }}
          >
            Collapse All
          </button>
        </div>

        <div className="m-2 flex flex-col gap-1">
          {currentStations.map((station) => (
            <Station_info
              key={station.station_id} // Ensure each station has a unique key
              station_id={station.station_id}
              location={station.location}
              data={station} // Ensure data is passed properly
              colapse={colapse_all}
              coordinates={station.coordinates}
            />
            
          ))}
        </div>

        {/* Pagination Controls */}
        <div className="flex justify-between mx-2">
          <button
            onClick={prevPage}
            className="bg-sky-900 text-white p-2 hover:bg-gray-800"
            disabled={currentPage === 1}
          >
            Previous
          </button>
          <button
            onClick={nextPage}
            className="bg-sky-900 text-white p-2 hover:bg-gray-800"
            disabled={currentPage === Math.ceil(filteredData.length / stationsPerPage)}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
