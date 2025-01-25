import { connect } from "../database/database.js";
import moment from "moment";  
function getCurrentDateTime() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');

    // Return as an object with a date property
    return { date: `${year}-${month}-${day} ${hours}:${minutes}:${seconds}` };
}

const connection = connect;
export const getAllStations = (req,res)=>{
    connection.execute(`SELECT * FROM station_table`,(err,data)=>{
        return res.status(200).json({data})
    })
}
 
export const addEvent=async (req,res)=>{
    const { station_id, acceleration,velocity,displacement,richter } = req.body; 
    const {date}=getCurrentDateTime()

    await connection.execute(`INSERT INTO events (station_id,acceleration,velocity,displacement,richter,date) VALUES('${station_id}','${acceleration}','${velocity}','${displacement}','${richter}','${date}')`)
    return res.status(200).json({message:"added event"})
}
export const getStationLastRead=(req,res)=>{
    const {id}=req.params;
    connection.execute(`
            SELECT events.station_id, events.acceleration, events.date, station_table.location,velocity,displacement,richter
            FROM station_table
            LEFT JOIN events ON events.station_id = station_table.station_id
            WHERE station_table.station_id = '${id}'
            ORDER BY events.date DESC
            LIMIT 1
        `,(err, data) => {
            if (err) {
                console.error(err);
                return res.status(500).json({ message: "Database query failed" });
            }
            
            // Format data with a maximum of 5 decimal places
            const formattedData = data.map((row) => ({
                ...row,
                acceleration: row.acceleration ? parseFloat(row.acceleration).toFixed(8) : row.acceleration,
                velocity: row.velocity ? parseFloat(row.velocity).toFixed(8) : row.velocity,
                displacement: row.displacement ? parseFloat(row.displacement).toFixed(8) : row.displacement,
                richter: row.richter ? parseFloat(row.richter).toFixed(8) : row.richter,
                date: moment.utc(row.date).utcOffset(2).format("hh:mm:ss A"),
            }));

            return res.status(200).json({ data: formattedData });
        })
        
}


export const getStationHistory = (req, res) => {
    const { id } = req.params;

    const lastReadQuery = `
        SELECT acceleration, velocity, displacement, richter, date
        FROM events
        WHERE station_id = ?
        ORDER BY date DESC
        LIMIT 1;
    `;

    const maxRichterQuery = `
        SELECT DISTINCT 
            events.acceleration, 
            events.velocity, 
            events.displacement, 
            events.richter, 
            events.date
        FROM events
        WHERE events.station_id = ?
        AND events.richter IN (
            SELECT MAX(richter)
            FROM events AS sub_events
            WHERE sub_events.station_id = events.station_id 
            AND DATE(sub_events.date) = DATE(events.date)
            GROUP BY DATE(sub_events.date)
        )
        ORDER BY events.date DESC;
    `;

    connection.execute(lastReadQuery, [id], (err1, lastReadData) => {
        if (err1) return res.status(500).json({ error: "Failed to fetch last read." });

        connection.execute(maxRichterQuery, [id], (err2, richterData) => {
            if (err2) return res.status(500).json({ error: "Failed to fetch station history." });

            const formattedLastRead = lastReadData[0]
                ? {
                      ...lastReadData[0],
                      acceleration: parseFloat(lastReadData[0].acceleration).toFixed(8),
                      velocity: parseFloat(lastReadData[0].velocity).toFixed(8),
                      displacement: parseFloat(lastReadData[0].displacement).toFixed(8),
                      richter: parseFloat(lastReadData[0].richter).toFixed(8),
                      date: lastReadData[0].date, // Preserving full date and time
                  }
                : null;

            const formattedRichterData = richterData.map((row) => ({
                ...row,
                acceleration: row.acceleration ? parseFloat(row.acceleration).toFixed(8) : row.acceleration,
                velocity: row.velocity ? parseFloat(row.velocity).toFixed(8) : row.velocity,
                displacement: row.displacement ? parseFloat(row.displacement).toFixed(8) : row.displacement,
                richter: row.richter ? parseFloat(row.richter).toFixed(8) : row.richter,
                date: row.date, // Preserving full date and time
            }));

            const combinedData = formattedLastRead
                ? [formattedLastRead, ...formattedRichterData]
                : [...formattedRichterData];

            // Save all the data (including last read) to the database
            connection.execute(`DELETE FROM events WHERE station_id = ?`, [id]);

            const insertQuery = `
                INSERT INTO events (station_id, acceleration, velocity, displacement, richter, date)
                VALUES (?, ?, ?, ?, ?, ?)
            `;

            for (const row of combinedData) {
                connection.execute(insertQuery, [
                    id,
                    row.acceleration,
                    row.velocity,
                    row.displacement,
                    row.richter,
                    row.date,
                ]);
            }

            // Exclude the last read entry from the response
            const responseData = formattedRichterData; // Remove formattedLastRead from the response

            // Send the response
            return res.status(200).json({ data: responseData });
        });
    });
};