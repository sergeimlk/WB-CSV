const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const createCsvWriter = require('csv-writer').createObjectCsvWriter;
const { processCSV } = require('./services/csvProcessor');

const app = express();
const port = 3000;

// Configure multer for file upload
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        if (!fs.existsSync('uploads')) {
            fs.mkdirSync('uploads');
        }
        cb(null, 'uploads');
    },
    filename: function (req, file, cb) {
        cb(null, Date.now() + '-' + file.originalname);
    }
});

const upload = multer({ 
    storage: storage,
    fileFilter: (req, file, cb) => {
        if (file.originalname.toLowerCase().endsWith('.csv')) {
            cb(null, true);
        } else {
            cb(new Error('Only CSV files are allowed'));
        }
    }
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

app.use('/static', express.static('static'));

app.post('/upload', upload.single('file'), async (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }

    try {
        const filePath = req.file.path; // Assuming the file path is available in req.file.path
        const processedData = await processCSV(filePath);
        
        if (!processedData || processedData.length === 0) {
            throw new Error('No data processed');
        }

        const processedFilename = `processed_${req.file.originalname}`;
        const processedPath = path.join('uploads', processedFilename);

        const csvWriter = createCsvWriter({
            path: processedPath,
            header: Object.keys(processedData[0]).map(key => ({ id: key, title: key })),
            delimiter: ';'
        });

        await csvWriter.writeRecords(processedData);

        // Clean up original file
        fs.unlinkSync(req.file.path);
        
        res.json({ filename: processedFilename });
    } catch (error) {
        console.error('Error processing file:', error);
        // Clean up uploaded file in case of error
        if (req.file && fs.existsSync(req.file.path)) {
            fs.unlinkSync(req.file.path);
        }
        res.status(500).json({ error: 'Error processing file: ' + error.message });
    }
});

app.get('/download/:filename', (req, res) => {
    const filePath = path.join('uploads', req.params.filename);
    
    if (!fs.existsSync(filePath)) {
        return res.status(404).json({ error: 'File not found' });
    }
    
    res.download(filePath, req.params.filename, (err) => {
        if (err) {
            console.error('Download error:', err);
            if (!res.headersSent) {
                res.status(500).json({ error: 'Error downloading file' });
            }
        }
    });
});

app.listen(port, () => {
    console.log(`Server running at http://127.0.0.1:${port}/`);
});