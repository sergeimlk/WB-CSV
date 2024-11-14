const fetch = require('node-fetch');

const API_KEY = 'AIzaSyBO2n-TzeF3WRlNlVzN-rn8SzBL_1xym7I'
const cache = new Map();

async function getAddressInfo(lat, lon) {
    const cacheKey = `${lat},${lon}`;
    
    if (cache.has(cacheKey)) {
        return cache.get(cacheKey);
    }
    
    try {
        const url = `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lon}&key=${API_KEY}`;
        const response = await fetch(url);
        const data = await response.json();

        if (data.status === 'OK' && data.results.length > 0) {
            const addressComponents = data.results[0].address_components;
            let city = null, postalCode = null, country = null;
            
            for (const component of addressComponents) {
                if (component.types.includes('locality')) {
                    city = component.long_name;
                } else if (component.types.includes('postal_code')) {
                    postalCode = component.long_name;
                } else if (component.types.includes('country')) {
                    country = component.long_name;
                }
            }
            
            const result = { city, postalCode, country };
            cache.set(cacheKey, result);
            return result;
        }
    } catch (error) {
        console.error(`Error for coordinates (${lat}, ${lon}):`, error);
    }
    
    return { city: null, postalCode: null, country: null };
}

module.exports = { getAddressInfo };