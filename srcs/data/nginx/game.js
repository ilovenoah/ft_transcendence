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

// Paddles
const user1 = {
    x: 0, // left side of canvas
    y: (canvas.height - 100) / 2,
    width: 10,
    height: 100,
    score: 0, //今後使用
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

const socket = new WebSocket('ws://localhost:8000/');

socket.onopen = function(event) {
    console.log("WebSocket is open now.");
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    user2.y = data.y;
    ball.x = data.ballX;
    ball.y = data.ballY;
    ball.velocityX = data.ballVelocityX;
    ball.velocityY = data.ballVelocityY;
};

socket.onerror = function(error) {
    console.log("WebSocket error: " + error.message);
};

// // Control the paddles
window.addEventListener('keydown', function(event) {
    switch (event.keyCode) {
        case 87: // W key
            user1.y = Math.max(0, user1.y - 20);
            break;
        case 83: // S key
            user1.y = Math.min(canvas.height - user1.height, user1.y + 20);
            break;
    }
    socket.send(JSON.stringify({
        y: user1.y,
        ballX: ball.x,
        ballY: ball.y,
        ballVelocityX: ball.velocityX,
        ballVelocityY: ball.velocityY
    }));
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

// Game functions (collision detection, update, render) remain the same

// Render the game
function render() {
    // clear the canvas
    drawRect(0, 0, canvas.width, canvas.height, 'BLACK');
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
    if (ball.visible == true) {
        ball.x += ball.velocityX;
        ball.y += ball.velocityY;
    }
}

// Start the game
requestAnimationFrame(render);
