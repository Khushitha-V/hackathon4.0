// scripts.js
document.getElementById('search-button').addEventListener('click', async () => {
    const formData = new FormData(document.getElementById('search-form'));
    const queryParams = new URLSearchParams(formData).toString();
    
    try {
        const response = await fetch(/search?${queryParams});
        const data = await response.json();
        
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = '';
        
        if (data.results && data.results.length > 0) {
            data.results.forEach(result => {
                const resultItem = document.createElement('div');
                resultItem.innerHTML = <h3>${result.title}</h3><p>${result.abstract}</p>;
                resultsDiv.appendChild(resultItem);
            });
        } else {
            resultsDiv.innerHTML = '<p>No results found.</p>';
        }
    } catch (error) {
        console.error('Error fetching search results:', error);
    }
});