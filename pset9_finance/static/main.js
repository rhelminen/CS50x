// Assigns a point value to passwords based on how strong they are
function checkStrength(password) {

    // Store the length of user input in a different variable since password.length might be modified
    let trueLength = password.length;

    // Ignore the word 'password' by removing it from the string
    if (password.includes('password')) {
        password = password.replace('password', '')
    }

    // Give 2 points for all characters in password
    let points = password.length * 2;

    // Find matches for different types of characters using regular expressions
    const uppercase = password.match(/[A-Z]/g);
    const number = password.match(/[0-9]/g);

    // Treat everything but characters in the English alphabet, numbers and spaces as special characters
    const special = password.replace(/[a-zA-Z0-9 ]/g, '')

    // Give points for first occurrence of a character type and extra points for each subsequent match
    if (uppercase) {
        points += 10;
        points += uppercase.length * 2;
    }

    if (number) {
        points += 5;
        points += number.length;
    }

    if (special) {
        points += 15;
        points += special.length * 4;
    }

    // Extra points if password includes all character types
    if (uppercase && number && special) {
        points += 15;
    }

    // Extra points for longer passwords, which get exponentially harder to crack with each new character
    if (password.length > 7) {
        points += 10;
        points += (password.length - 7) * 4;
    }

    // Show password strength bar when user starts inputting a password
    let strengthText = document.querySelector('.strength-text');
    let strengthBar = document.querySelector('.strength-bar');
    strengthText.parentNode.style.display = 'block';
    strengthBar.style.display = 'flex';

    if (points < 25) {
        strengthText.innerHTML = '<strong>Very weak</strong>';
        strengthBar.innerHTML = '<div class="progress-bar bg-danger" role="progressbar" style="width: 0%" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>';
    } else if (points < 50) {
        strengthText.innerHTML = '<strong class="text-danger">Weak</strong>';
        strengthBar.innerHTML = '<div class="progress-bar bg-danger" role="progressbar" style="width: 25%" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100"></div>';
    } else if (points < 75) {
        strengthText.innerHTML = '<strong class="text-warning">Okay</strong>';
        strengthBar.innerHTML = '<div class="progress-bar bg-warning" role="progressbar" style="width: 50%" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100"></div>';
    } else if (points < 100) {
        strengthText.innerHTML = '<strong class="text-info">Strong</strong>';
        strengthBar.innerHTML = '<div class="progress-bar bg-info" role="progressbar" style="width: 75%" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100"></div>';
    } else {
        strengthText.innerHTML = '<strong class="text-success">Very strong</strong>';
        strengthBar.innerHTML = '<div class="progress-bar bg-success" role="progressbar" style="width: 100%" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100"></div>';
    }

    // Hide strength info if user erases password
    if (trueLength === 0) {
        strengthText.parentNode.style.display = 'none';
        strengthBar.style.display = 'none';
    }
}

// Convert UTC timestamps to local time and local time format
let utcDate = document.querySelectorAll('.datetime');
for (let i of utcDate) {
    // Add 'T' after date and 'Z' after time according to ISO 8601 standard for automatic conversion
    let date = i.innerHTML.split(' ');
    let isoDate = date[0] + 'T' + date[1] + 'Z';
    let localDate = new Date(isoDate);
    i.innerHTML = localDate.toLocaleString();
}
