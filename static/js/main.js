function formatMD(text) {
    if (!text) return '';
    return text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
        .replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>').replace(/\*(.*?)\*/g,'<em>$1</em>')
        .replace(/### (.*)/g,'<h3>$1</h3>').replace(/## (.*)/g,'<h3>$1</h3>')
        .replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\n/g,'<br>');
}
