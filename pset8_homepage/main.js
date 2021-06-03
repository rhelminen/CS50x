// A sleep function for asynchronous functions
// Source of the function: https://www.sitepoint.com/delay-sleep-pause-wait/
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Show hidden text elements one by one using async / await
async function showText() {

    // Store all elements with the class 'hidden-text' in an array
    let hiddenTextArray = document.querySelectorAll('.hidden-text');

    for (let index of hiddenTextArray) {

        // Store the hidden text in a variable and delete the original text
        let text = index.innerHTML;
        index.innerHTML = '';

        // Remove the 'hidden-text' class to make the element visible
        index.classList.remove('hidden-text');

        // Call the typewriter function if needed and wait for it to finish before showing other text
        if (index.classList.contains('typewriter-effect')) {
            await typewriter(text, index);
        } else {
            await sleep(500);
            index.innerHTML = text;
        }
    }
}

// Typewriter effect - This idea is familiar from various sources, but the function is my own
// Skips <br> tags and adds them to innerHTML all at once, otherwise they wouldn't be processed correctly
async function typewriter(text, index) {
    for (let i = 0; i < text.length; i++) {
        if (text.slice(i, i + 4) === '<br>') {
            await sleep(250);
            index.innerHTML += '<br>';
            i += 3;
        } else {
            index.innerHTML += text[i];
            await sleep(75);
        }
    }
}

// Make an array out of all programming language icons
const iconArray = document.querySelectorAll('.icon-lg');

// Add fade & zoom in animation to icons in iconArray
async function iconEffect() {
    for (let icon of iconArray) {
        icon.style.display = 'inline';

        // Target values for width & height are automatically set to the values in the CSS
        icon.animate([
            {
                width: '0px',
                height: '0px',
                opacity: 0
            },
            {
                opacity: 1
            }
        ], 1000);
        await sleep(350);
    }

    // Show the paragraphs below the icons
    showText();
}

// Show a thank you message when user submits contact form
const form = document.getElementById('contact-form');
if (form) {
    form.onsubmit = () => alert('Thank you for your message!');
}
