const canvas = document.getElementById('pongCanvas');
const context = canvas.getContext('2d');
const socket = new WebSocket('wss://' + window.location.host + '/ws/pong/');

// Pongゲームの基本設定
const paddleWidth = 10, paddleHeight = 100, ballSize = 10;
let playerPaddle = { x: 10, y: canvas.height / 2 - paddleHeight / 2 };
let aiPaddle = { x: canvas.width - paddleWidth - 10, y: canvas.height / 2 - paddleHeight / 2 };
let ball = { x: canvas.width / 2, y: canvas.height / 2, dx: 2, dy: 2 };

function drawRect(x, y, width, height, color) {
    context.fillStyle = color;
    context.fillRect(x, y, width, height);
}

function drawCircle(x, y, radius, color) {
    context.fillStyle = color;
    context.beginPath();
    context.arc(x, y, radius, 0, Math.PI * 2, false);
    context.closePath();
    context.fill();
}

function render() {
    context.clearRect(0, 0, canvas.width, canvas.height);
    drawRect(playerPaddle.x, playerPaddle.y, paddleWidth, paddleHeight, 'white');
    drawRect(aiPaddle.x, aiPaddle.y, paddleWidth, paddleHeight, 'white');
    drawCircle(ball.x, ball.y, ballSize, 'white');
}

function update() {
    ball.x += ball.dx;
    ball.y += ball.dy;

    // 壁の衝突判定
    if (ball.y + ball.dy > canvas.height || ball.y + ball.dy < 0) {
        ball.dy = -ball.dy;
    }

    // パドルの衝突判定
    if (ball.x + ball.dx < playerPaddle.x + paddleWidth) {
        if (ball.y > playerPaddle.y && ball.y < playerPaddle.y + paddleHeight) {
            ball.dx = -ball.dx;
        } else {
            // AIの勝ち
        }
    } else if (ball.x + ball.dx > aiPaddle.x) {
        if (ball.y > aiPaddle.y && ball.y < aiPaddle.y + paddleHeight) {
            ball.dx = -ball.dx;
        } else {
            // プレイヤーの勝ち
        }
    }
}

function gameLoop() {
    update();
    render();
    requestAnimationFrame(gameLoop);
}

gameLoop();

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log(data.message);
};

document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowUp' && playerPaddle.y > 0) {
        playerPaddle.y -= 10;
    } else if (e.key === 'ArrowDown' && playerPaddle.y < canvas.height - paddleHeight) {
        playerPaddle.y += 10;
    }

    socket.send(JSON.stringify({
        'message': 'Player moved'
    }));
});