import React, { useEffect, useState } from 'react';
import History from './history';
 

export default function Station_info(props) {
  let id = props.station_id;

  let [arrow, arrow_setter] = useState(
    <div className="rounded-full ml-2 bg-black h-4 w-4"></div>
  );
  let [iscollapsed, iscollapsed_setter] = useState(false);
  let [stationinfo, setstationinfo] = useState([]);
  let [history, setHistory] = useState([]);
  let [loading, setLoading] = useState(true); // Added loading state for station info
  let [loadingHistory, setLoadingHistory] = useState(true); // Added loading state for history

  // Function to fetch station data
  const fetchStationData = async () => {
    try {
      const response = await fetch(`http://localhost:3001/stations/${id}`);
      const result = await response.json();
      setstationinfo(result.data);
      setLoading(false); // Set loading to false when station data is fetched
    } catch (error) {
      console.error('Error fetching station data:', error);
      setLoading(false); // Handle loading state even on error
    }
  };

  // Function to fetch history data
  const fetchHistoryData = async () => {
    try {
      const response = await fetch(`http://localhost:3001/history/${id}`);
      const result = await response.json();
      setHistory(result.data);
      setLoadingHistory(false); // Set loading to false when history data is fetched
    } catch (error) {
      console.error('Error fetching history data:', error);
      setLoadingHistory(false); // Handle loading state even on error
    }
  };

  // Periodic fetching for station info (more frequent)
  useEffect(() => {
    fetchStationData(); // Initial fetch for station info
    const interval = setInterval(() => {
      fetchStationData();
    }, 100); // Station data updates every 1 second

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, [id]);

  // Periodic fetching for history data (less frequent)
  useEffect(() => {
    fetchHistoryData(); // Initial fetch for history data

    const interval = setInterval(() => {
      fetchHistoryData();
    }, 5000); // History data updates every 5 seconds

    return () => clearInterval(interval); // Cleanup interval on unmount
  }, []);

  useEffect(() => {
    iscollapsed_setter(false);
    arrow_setter(
      <div className="rounded-full ml-2 block bg-black h-4 w-4"></div>
    );
  }, [props.colapse]);

  function toggle_collapse() {
    iscollapsed_setter(!iscollapsed);
    if (!iscollapsed) {
      arrow_setter(
        <div className="rounded-full ml-2 block bg-sky-900 h-4 w-4"></div>
      );
    } else {
      arrow_setter(
        <div className="rounded-full ml-2 block bg-black h-4 w-4"></div>
      );
    }
  }

  let station = (
    <div
      className="bg-gray-600 text-white px-10 w-full overflow-hidden"
      style={{
        maxHeight: !iscollapsed ? '0' : '500px',
        transition: 'max-height 0.15s ease-in-out',
      }}
    >
      <table className="w-full">
        <thead className="text-center">
          <tr>
            <th>Location</th>
            <th>Acceleration (m/s<sup>2</sup>)</th>
            <th>Velocity (m/s)</th>
            <th>Displacement (m)</th>
            <th>Richter's Magnitude</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody className="text-center">
          {loading ? (
            <tr>
              <td colSpan="6">Loading...</td>
            </tr>
          ) : stationinfo.length > 0 ? (
            <tr>
              <td>{stationinfo[0]['location']}</td>
              <td>{stationinfo[0]['acceleration']}</td>
              <td>{stationinfo[0]['velocity']}</td>
              <td>{stationinfo[0]['displacement']}</td>
              <td>{stationinfo[0]['richter']}</td>
              <td>{stationinfo[0]['date']}</td>
            </tr>
          ) : (
            <tr>
              <td colSpan="6">No Data Available</td>
            </tr>
          )}
        </tbody>
      </table>
      <div>
        <p className="bg-gray-300 text-black text-center">History</p>
        <History info={history}></History> {/* Passing the history data to the component */}
      </div>
    </div>
  );

  return (
    <div className="flex flex-col justify-center items-center border border-black">
      <button
        className="flex w-full bg-gray-300 h-full items-center gap-2 text-lg hover:bg-gray-500 "
        onClick={toggle_collapse}
      >
        {arrow} Station ({id})
      </button>
      {station}
    </div>
  );
}
