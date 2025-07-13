// assets/dash_clientside_functions.js

// Define the clientside functions directly under window.dash_clientside
// Dash expects clientside functions to be directly accessible under this namespace
window.dash_clientside = window.dash_clientside || {};

window.dash_clientside.copy_to_clipboard = function(n_clicks, modal_content_id) {
    if (!n_clicks || n_clicks === 0) {
        return ""; // Do nothing on initial load
    }

    const element = document.getElementById(modal_content_id);
    if (element) {
        const textToCopy = element.innerText || element.textContent;
        try {
            // Use a temporary textarea to copy text, as navigator.clipboard.writeText might be restricted in iframes
            const textarea = document.createElement('textarea');
            textarea.value = textToCopy;
            textarea.style.position = 'fixed'; // Avoid scrolling to bottom
            textarea.style.opacity = '0'; // Make it invisible
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            return "Copied to clipboard!";
        } catch (err) {
            console.error('Failed to copy text: ', err);
            return "Failed to copy text.";
        }
    }
    return "Element not found for copying.";
};
