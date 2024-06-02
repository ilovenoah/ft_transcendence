let scene, camera, renderer, paddle1, paddle2, ball;
let player1Y = 0;
let moveUp = false;
let moveDown = false;

function init() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer();
    
    wwidth = window.innerWidth;
    wheight = window.innerHeight;
    // console.log (wwidth);
    // console.log(wheight);
    if ( wwidth >= 2 * wheight)
        wwidth = wheight * 2;
    else if(wwidth < 2 * wheight)
        wheight = wwidth * 0.5;        
    renderer.setSize(wwidth, wheight);
    //renderer.setSize(window.innerWidth, window.innerHeight);

    document.body.appendChild(renderer.domElement);

    const geometry = new THREE.BoxGeometry(1, 3, 1);
    const material = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
    
    paddle1 = new THREE.Mesh(geometry, material);
    paddle1.position.x = -10;
    scene.add(paddle1);

    const material2 = new THREE.MeshPhongMaterial({ color: 0xff0000 });
    paddle2 = new THREE.Mesh(geometry, material2);
    paddle2.position.x = 10;
    scene.add(paddle2);

    const ballGeometry = new THREE.SphereGeometry(0.5, 24, 24);
    const ballMaterial = new THREE.MeshPhongMaterial({ color: 0xffff00 });
    ball = new THREE.Mesh(ballGeometry, ballMaterial);
    scene.add(ball);

//    const light = new THREE.AmbientLight(0xFFFFFF, 1.0);

    //const light = new THREE.DirectionalLight(0xFFFFFF, 10);
    const light = new THREE.HemisphereLight(0xFFFFFF, 0x0000FF, 1.0);
    scene.add(light);


    camera.position.z = 20;
}

function animate() {
    if (moveUp) {
        player1Y += 0.1;
    } else if (moveDown) {
        player1Y -= 0.1;
    }

    gameSocket.send(JSON.stringify({
        'message': 'update_position',
        'player1_y': player1Y * 100  // サーバーでのスケーリングを考慮
    }));

    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

function updateGameState(data) {
    paddle1.position.y = data.player1_y / 100;
    paddle2.position.y = data.player2_y / 100;
    ball.position.x = data.ball_x / 100;
    ball.position.y = data.ball_y / 100;
}

function onKeyDown(e) {
    if (e.key === 'ArrowUp') {
        moveUp = true;
    } else if (e.key === 'ArrowDown') {
        moveDown = true;
    }
}

function onKeyUp(e) {
    if (e.key === 'ArrowUp') {
        moveUp = false;
    } else if (e.key === 'ArrowDown') {
        moveDown = false;
    }
}


const gameSocket = new WebSocket('wss://' + window.location.host + '/ws/game/');



gameSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    updateGameState(data);
};

gameSocket.onopen = function(e) {
    console.log("WebSocket connection established");

    //ゲームが始まったらやればいい
    animate();
};

gameSocket.onclose = function(e) {
    console.log("WebSocket connection closed");
};

document.addEventListener('keydown', onKeyDown);
document.addEventListener('keyup', onKeyUp);

init();
