import mysql from 'mysql2'

export const connect=mysql.createConnection({  
        host:'mysql',//mysql
        password:'',
        database:'station',
        user:'root',
        port:3306,
        connectTimeout:10000
    }
)