const mysql = require('mysql2/promise');


    // Create the connection to the database - pool method
    const pool = mysql.createPool({
        host: 'localhost',
        user: 'root',
        password: '',
        database: 'geofence',
        waitForConnections: true,
        connectionLimit: 10,
        queueLimit: 0});

    // Function to test the connection - WILL REMOVE #1
    async function testConnection() {
        try {
            const connection = await pool.getConnection();
            console.log('Connected to the database successfully!');
            connection.release();
        } catch (error) {
            console.error('Database connection failed: ', error);
            process.exit(1);
        }
    }

    // Call the test connection function - WILL REMOVE #2
    testConnection();

    // Export the pool for use in other modules
    module.exports = pool;