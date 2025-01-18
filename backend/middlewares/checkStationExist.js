import { connect } from "../database/database.js";

export const checkStationExist=(req,res,next)=>{
    const {id}=req.params
    const connection=connect
    connection.execute(`SELECT station_id FROM station_table WHERE station_id='${id}'`,(err,data)=>{
            if (data.length>0){
                next()
            }
            else {
                return res.status(404).json({message:"No Station with this ID found"})
            }
            
    })
    
}