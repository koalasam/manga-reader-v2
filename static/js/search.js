document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('searchForm');
    const queryInput = document.getElementById('searchQuery');
    const sourceSelect = document.getElementById('sourceSelect');
    const resultsContainer = document.getElementById('results');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        const query = queryInput.value.trim();
        const source = sourceSelect.value;
        if (!query) return;

        const res = await fetch(`/api/search?q=${encodeURIComponent(query)}&source=${encodeURIComponent(source)}&limit=20`);
        const data = await res.json();
        if (data.error) {
            resultsContainer.innerHTML = `<p>Error: ${data.error}</p>`;
            return;
        }
        if (data.results.length === 0) {
            resultsContainer.innerHTML = `<p>No results found.</p>`;
            return;
        }
        resultsContainer.innerHTML = data.results.map(item => `
            <div class="result-item">
                <a href="/series/${item.id}?source=${encodeURIComponent(source)}">
                    ${item.cover_url ? `<img src="${item.cover_url}" alt="${item.title}" loading="lazy">` : ''}
                    <h3>${item.title}</h3>
                    <p>${item.description ? item.description.substring(0, 80) + '...' : ''}</p>
                </a>
            </div>
        `).join('');
    });
});