const Papa = require('papaparse');
const chardet = require('chardet');
const iconv = require('iconv-lite');
const fs = require('fs');
const { getAddressInfo } = require('./geocoding');

async function readCSV(filePath) {
    // Detect file encoding
    const buffer = fs.readFileSync(filePath);
    const encoding = chardet.detect(buffer);
    const fileContent = iconv.decode(buffer, encoding);

    // Parse CSV content
    return await new Promise((resolve, reject) => {
        Papa.parse(fileContent, {
            header: true,
            delimiter: ';',
            skipEmptyLines: true,
            complete: (results) => resolve(results.data),
            error: (error) => reject(error)
        });
    });
}

function chunkArray(array, size) {
    const chunkedArray = [];
    for (let i = 0; i < array.length; i += size) {
        chunkedArray.push(array.slice(i, i + size));
    }
    return chunkedArray;
}

async function processCSV(filePath) {
    try {
        const rows = await readCSV(filePath);
        const processedRows = [];

        for (const batch of chunkArray(rows, 100)) {
            const promises = batch.map(async (row) => {
                try {
                    const { lat, lon } = row;
                    if (!lat || !lon) {
                        console.warn(`Invalid coordinates for row: ${JSON.stringify(row)}`);
                        return { ...row };
                    }

                    const { city, postalCode, country } = await getAddressInfo(lat, lon);
                    return {
                        ...row,
                        City: city || row.City || '',
                        'ZIP code': postalCode || row['ZIP code'] || '',
                        Country: country || row.Country || ''
                    };
                } catch (error) {
                    console.error('Error processing row:', error);
                    return row; // Return original row if processing fails
                }
            });

            const processedBatch = await Promise.all(promises);
            processedRows.push(...processedBatch);
        }

        return processedRows;
    } catch (error) {
        console.error('Error in processCSV:', error);
        throw error;
    }
}

module.exports = {
    processCSV
};