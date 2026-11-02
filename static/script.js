// With the help of A, create a stopwatch
// 1. Grab all the HTML elements we need to interact with
const display = document.getElementById("stopwatch-display");
const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");
const resetBtn = document.getElementById("reset-btn");
const amountInput = document.getElementById("amount");
const hobbySelect = document.getElementById("hobby_id");
const logCard = document.getElementById("log-card");

// 2. Define state variables to track the timer's memory
let startTime = 0;
let elapsedTime = 0;
let timerInterval = null; // Holds the ID of our repeating loop

// 3. Helper Function: Convert raw milliseconds into a clean HH:MM:SS string
function formatTime(timeInMs) {
    // Math.floor rounds down to the nearest whole number
    let totalSeconds = Math.floor(timeInMs / 1000);
    
    let hours = Math.floor(totalSeconds / 3600);
    let minutes = Math.floor((totalSeconds % 3600) / 60);
    let seconds = totalSeconds % 60;

    // .toString().padStart(2, "0") ensures single digits become "09" instead of "9"
    return (
        hours.toString().padStart(2, "0") + ":" +
        minutes.toString().padStart(2, "0") + ":" +
        seconds.toString().padStart(2, "0")
    );
}

// 4. The main loop that runs every 10 milliseconds
function updateTimer() {
    const currentTime = Date.now();
    // Calculate how much time has passed since we clicked start, plus any previously saved time
    const timeToDisplay = elapsedTime + (currentTime - startTime);
    
    // Update the HTML text inside the display div
    display.textContent = formatTime(timeToDisplay);
}

// 5. Button Click Listeners (The Triggers)

startBtn.addEventListener("click", function() {
    // Prevent multiple clicks from speeding up the timer
    if (timerInterval === null) {
        startTime = Date.now();
        // setInterval runs the updateTimer function every 10 milliseconds
        timerInterval = setInterval(updateTimer, 10); 
    }
});

stopBtn.addEventListener("click", function() {
    if (timerInterval !== null) {
        // clearInterval stops the repeating loop
        clearInterval(timerInterval);
        timerInterval = null;
        
        // Save the exact elapsed time so we can resume if needed
        elapsedTime += Date.now() - startTime;

        // AUTOMATION: Convert to minutes and inject into the form's amount input
        let totalMinutes = Math.floor(elapsedTime / 60000);
        // Ensure at least 1 minute is logged if they stopped it early
        amountInput.value = totalMinutes > 0 ? totalMinutes : 1; 
    }
});

resetBtn.addEventListener("click", function() {
    // Stop the loop and wipe the memory variables back to zero
    clearInterval(timerInterval);
    timerInterval = null;
    startTime = 0;
    elapsedTime = 0;
    
    // Reset the HTML displays
    display.textContent = "00:00:00";
    amountInput.value = "";
});

// Change background in log page depending on hobby chosen - AI was used to help me in this section

if (hobbySelect && logCard) {
    hobbySelect.addEventListener("change", function () {
        // Find the selected <option> element
        const selectedOption = this.options[this.selectedIndex];
        const imageUrl = selectedOption.getAttribute("data-image");

        if (imageUrl) {
            // Apply gradient and image, forcing it past the CSS !important rule
            logCard.style.setProperty("background-image", `linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), url("${imageUrl}")`, "important");
            logCard.style.backgroundSize = "cover";
            logCard.style.backgroundPosition = "center";
        } else {
            // Revert back to standard glass card background if unselected
            logCard.style.backgroundImage = "none";
        }
    });
}
