const express = require('express');
const app = express();
const PORT = 3000;

// Middleware for parsing JSON
app.use(express.json());

// Middleware to simulate Bearer token validation (optional)
app.use((req, res, next) => {
    if (req.headers.authorization) {
        console.log("Authorization Header:", req.headers.authorization);
    } else {
        console.log("No Authorization header provided.");
    }
    next();
});

// ✅ Mock route for posting invoice data (PRAL PostInvoiceData)
app.post('/di_data/v1/di/postinvoicedata', (req, res) => {
    console.log('Received POST Invoice Data:', req.body);

    // ✅ Simulate success response
    res.json({
        invoiceNumber: "FBR-TEST-INV-001",
        statusCode: "00", // "00" means valid in FBR
        status: "Valid",
        errorCode: null,
        exception: null
    });
});

// ✅ Mock route for validating invoice data
app.post('/di_data/v1/di/validateinvoicedata_sb', (req, res) => {
    console.log('Received Validate Invoice Data:', req.body);

    // ✅ Simulate validation success
    res.json({
        validationStatus: "Passed",
        statusCode: "00",
        remarks: "Invoice validation successful"
    });
});

// ✅ Health check route
app.get('/', (req, res) => {
    res.send('Mock FBR API Server is running!');
});

app.listen(PORT, () => {
    console.log(`✅ Mock FBR API server running on http://localhost:${PORT}`);
});
