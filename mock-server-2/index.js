const express = require('express');
const cors = require('cors');
const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Health
app.get('/', (req, res) => res.send('FBR Mock up'));

// POST Invoice Data
app.post('/di_data/v1/di/postinvoicedata', (req, res) => {
  const body = req.body || {};
  console.log('POST /postinvoicedata\n', JSON.stringify(body, null, 2));
  const total = Number(body.grandTotal || 0);
  const ref = (body.invoiceRefNo || 'INV') + '-' + total.toFixed(2);
  let checksum = 0;
  for (let i = 0; i < ref.length; i++) checksum += ref.charCodeAt(i);
  const invoiceNumber = 'FBR-MOCK-' + checksum;

  res.json({
    invoiceNumber,
    statusCode: "00",
    status: "Valid",
    qrText: `FBR|${invoiceNumber}|${body.invoiceDate || ''}|${total.toFixed(2)}|PKR|GST`,
    errorCode: null,
    exception: null
  });
});

// Validate (optional stub)
app.post('/di_data/v1/di/validateinvoicedata_sb', (req, res) => {
  console.log('POST /validateinvoicedata_sb\n', JSON.stringify(req.body || {}, null, 2));
  res.json({ validationStatus: "Passed", statusCode: "00", remarks: "OK" });
});

app.listen(PORT, () => console.log(`FBR Mock listening on http://127.0.0.1:${PORT}`));
