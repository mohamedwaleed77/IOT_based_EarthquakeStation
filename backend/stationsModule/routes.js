import { Router } from "express";
import { checkStationExist } from "../middlewares/checkStationExist.js";
import {  getAllStations, getStationHistory } from "./controller.js";

const stationRouter=Router()

stationRouter.get('/history/:id',checkStationExist,getStationHistory)
stationRouter.get('/stations',getAllStations)
//stationRouter.post('/addevent',addEvent) //commented for websocket
//stationRouter.get('/stations/:id',checkStationExist,getStationLastRead)

export default stationRouter