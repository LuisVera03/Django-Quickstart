// Change these values if you want different demo credentials
const DEMO_USER = 'demo@example.com';
const DEMO_PASS = 'demo1234';

const DEMO_USER_NO_PERM = 'user@example.com';
const DEMO_PASS_NO_PERM = 'demo1234';
// Function triggered by your link: <a onclick="Test_Credential()">Click here</a>
function Test_Credential(event,number) {
    // Prevent default behavior if the <a> has href
    if (event && event.preventDefault) event.preventDefault();

    const userInput = document.getElementById('id_username');
    const passInput = document.getElementById('id_password');

    if (!userInput || !passInput) {
        console.warn('Could not find #username or #password fields');
        return;
    }

    // Autofill fields
    if (number == 0){
        userInput.value = DEMO_USER;
        passInput.value = DEMO_PASS;
    }
    else{
        userInput.value = DEMO_USER_NO_PERM;
        passInput.value = DEMO_PASS_NO_PERM;
    }

    // Focus and select username (useful if user wants to edit)
    userInput.focus();
    userInput.select();

    // Temporary highlight effect for both inputs
    [userInput, passInput].forEach(el => {
        el.classList.add('highlight');
        // Remove class after animation
        setTimeout(() => el.classList.remove('highlight'), 1200);
    });

    // Short feedback on the link (finds <a> with onclick attribute)
    try {
        var link = null;
        if (number == 0){
            link = document.querySelector("a[onclick^='Test_Credential(event, 0)']");
        }
        else{
            link = document.querySelector("a[onclick^='Test_Credential(event, 1)']");
        }
        if (link) {
            const original = link.innerHTML;
            link.innerHTML = 'Filled ✓';
            // Restore original text after delay
            setTimeout(() => { link.innerHTML = original; }, 500);
        }
    } catch (e) {
        // Non-critical if it fails
        console.error(e);
    }

    return false; // Just in case inline onclick is used
}

