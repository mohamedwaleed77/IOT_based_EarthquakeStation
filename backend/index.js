import express from 'express'
import cors from 'cors'
import stationRouter from './stationsModule/routes.js'


const app=express()
const port=3001
app.use(cors())
app.use(express.json())
app.use(stationRouter)
app.listen(port,()=>console.log('success'))