const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');

// Set canvas size
canvas.width = 800;
canvas.height = 400;

// Ball object
const ball = {
    x: canvas.width / 2,
    y: canvas.height / 2,
    radius: 10,
    velocityX: 5,
    velocityY: 5,
    speed: 7,
    color: 'WHITE',
    visible: true
};

let ballMoving = false;

// Paddles
const user1 = {
    x: 0, // left side of canvas
    y: (canvas.height - 100) / 2,
    width: 10,
    height: 100,
    score: 0,
    color: 'WHITE'
};

const user2 = {
    x: canvas.width - 10, // right side of canvas
    y: (canvas.height - 100) / 2,
    width: 10,
    height: 100,
    score: 0,
    color: 'WHITE'
};

// Control the paddles
window.addEventListener('keydown', function(event) {
    switch(event.keyCode) {
        case 87: // W key for User1 up
            user1.y = Math.max(0, user1.y - 20); // Prevent moving above the canvas
            break;
        case 83: // S key for User1 down
            user1.y = Math.min(canvas.height - user1.height, user1.y + 20); // Prevent moving below the canvas
            break;
        case 38: // Up Arrow for User2 up
            user2.y = Math.max(0, user2.y - 20); // Prevent moving above the canvas
            break;
        case 40: // Down Arrow for User2 down
            user2.y = Math.min(canvas.height - user2.height, user2.y + 20); // Prevent moving below the canvas
            break;
        case 32: // Space key to start ball movement
        if (!ballMoving) {
            ballMoving = true;
        }
        break;
    }
});

// Draw paddles and background
function drawRect(x, y, w, h, color) {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, w, h);
}

// Draw ball
function drawArc(x, y, r, color) {
    if (ball.visible) { // Check if the ball is visible before drawing it
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2, true);
        ctx.closePath();
        ctx.fill();
    }
}

// Draw center line
function drawDashedLine() {
    ctx.beginPath();
    ctx.setLineDash([10, 10]);  // Set the dash array as [dash length, gap length]
    ctx.moveTo(canvas.width / 2, 0);
    ctx.lineTo(canvas.width / 2, canvas.height);
    ctx.strokeStyle = 'WHITE';
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.setLineDash([]);  // Reset to solid line
}

// Game functions (collision detection, update, render) remain the same

// Render the game
function render() {
    // clear the canvas
    drawRect(0, 0, canvas.width, canvas.height, 'BLACK');
    drawDashedLine();
    // draw the paddles and ball
    drawRect(user1.x, user1.y, user1.width, user1.height, user1.color);
    drawRect(user2.x, user2.y, user2.width, user2.height, user2.color);
    drawArc(ball.x, ball.y, ball.radius, ball.color);
    // update game objects
    update();
    requestAnimationFrame(render);
}

function update() {
    // Check for collision with the top and bottom walls
    if (ball.y - ball.radius <= 0 || ball.y + ball.radius >= canvas.height) {
        ball.velocityY = -ball.velocityY; // Invert the ball's y-velocity
    }
    // Check for collision with paddles
    if ((ball.x - ball.radius <= user1.x + user1.width && ball.y >= user1.y && ball.y <= user1.y + user1.height)
        || (ball.x + ball.radius >= user2.x && ball.y >= user2.y && ball.y <= user2.y + user2.height)) {
        ball.velocityX = -ball.velocityX; // Reverse the ball's horizontal direction
    }
    // Check if ball hits the left or right walls
    if (ball.x - ball.radius <= 0 || ball.x + ball.radius >= canvas.width) {
        ball.visible = false;  // Make the ball invisible
        ball.velocityX = 0;    // Stop the ball's horizontal movement
        ball.velocityY = 0;    // Stop the ball's vertical movement
    }
    if (ball.visible && ballMoving) {
        ball.x += ball.velocityX;
        ball.y += ball.velocityY;
    }
}

// Start the game
requestAnimationFrame(render);
