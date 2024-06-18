let scene, camera, renderer, overlayCanvas, paddle1, paddle2, ball, score;
let player1Y = 0;
let player2Y = 0;
let paddle1length = 6;
let paddle2length = 6  ;
let moveUpX = false;
let moveDownX = false;
let moveUpY = false;
let moveDownY = false;
let wrate = 0.0;

let score_player1 = 0;
let score_player2 = 0;

let speedrate = 5.0;

let lastUpdateTime = Date.now();
const updateInterval = 1000;  // 1秒
const animationInterval = 100;  // 10ms

let reconnectInterval = 100; // 再接続の間隔

function init() {

    wwidth = window.innerWidth * 0.9;
    wheight = window.innerHeight * 0.9;
    // console.log (wwidth);
    // console.log(wheight);
    if ( wwidth >= 2 * wheight)
        wwidth = wheight * 2;
    else if(wwidth < 2 * wheight)
        wheight = wwidth * 0.5;        

    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, wwidth / wheight, 20, 60);
//    camera = new THREE.PerspectiveCamera(75, wwidth / wheight, 0.5, 1000);

    renderer = new THREE.WebGLRenderer();
    renderer.setSize(wwidth, wheight);
    document.getElementById('gameCanvas').appendChild(renderer.domElement);


    // オーバーレイCanvasを作成
    overlayCanvas = document.createElement('canvas');
    overlayCanvas.id = 'overlayCanvas';
    overlayCanvas.width = wwidth;
    overlayCanvas.height = wheight;
    document.getElementById('gameCanvas').appendChild(overlayCanvas);    

        
    wrate = wwidth * 0.001;
    wrate = 1;

    const wallgeometry = new THREE.BoxGeometry(77, 0.5, 0.5);
    const wallmaterial = new THREE.MeshPhongMaterial({ color: 0xffffff });
    
    wallupper = new THREE.Mesh(wallgeometry, wallmaterial);
    wallupper.position.y =  20.5
    wallupper.position.z =  0;
    scene.add(wallupper);

    walllower = new THREE.Mesh(wallgeometry, wallmaterial);
    walllower.position.y = -20.5;
    walllower.position.z =  0;
    scene.add(walllower);

    const wallcentergeometry = new THREE.BoxGeometry(0.5, 40.5, 0.5);
    const wallcentermaterial = new THREE.MeshPhongMaterial({ color: 0xffffff });
    
    wallcenter = new THREE.Mesh(wallcentergeometry, wallcentermaterial);
    wallcenter.position.z = 0;
    scene.add(wallcenter);


    // const walllinegeometry = new THREE.BoxGeometry(60, 1.01, 1.01);
    // const walllinematerial = new THREE.MeshPhongMaterial({ color: 0x999999 });
    // walllineupper = new THREE.Mesh(walllinegeometry, walllinematerial);
    // walllineupper.position.y = 20;
    // scene.add(walllineupper);
    // walllinelower = new THREE.Mesh(walllinegeometry, walllinematerial);
    // walllinelower.position.y = -20;
    // scene.add(walllinelower);


    const paddle1Geometry = new THREE.BoxGeometry(0.5, paddle1length, 0.5);
    const paddle1Material = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
    
    paddle1 = new THREE.Mesh(paddle1Geometry, paddle1Material);
    paddle1.position.x = 38.75;
    scene.add(paddle1);

    const paddle2Geometry = new THREE.BoxGeometry(0.5, paddle2length, 0.5);
    const paddle2Material = new THREE.MeshPhongMaterial({ color: 0xff0000 });
    paddle2 = new THREE.Mesh(paddle2Geometry, paddle2Material);
    paddle2.position.x = -38.75;
    scene.add(paddle2);

    const ballGeometry = new THREE.SphereGeometry(0.5, 32, 32);
    const ballMaterial = new THREE.MeshPhongMaterial({ color: 0xffff00 });
    ball = new THREE.Mesh(ballGeometry, ballMaterial);
    scene.add(ball);

    //const light = new THREE.AmbientLight(0xFFFFFF, 1.0);
    //const light = new THREE.DirectionalLight(0xFFFFFF, 10);
    const light = new THREE.HemisphereLight(0xFFFFFF, 0x0000FF, 1.0);
    scene.add(light);

    camera.position.z = 30;

//    scene.fog = new THREE.fog(0xFFFFFF, 100, 200);



    // // 形状データを作成
    // const SIZE = 1500;
    // // 配置する個数
    // const LENGTH = 1000;
    // // 頂点情報を格納する配列
    // const vertices = [];
    // for (let i = 0; i < LENGTH; i++) {
    //     const x = SIZE * (Math.random() - 0.5);
    //     const y = SIZE * (Math.random() - 0.5);
    //     const z = SIZE * (Math.random() - 1.0);

    //     vertices.push(x, y, z);
    // }

    // // 形状データを作成
    // const particlegeometry = new THREE.BufferGeometry();
    // particlegeometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));

    // // マテリアルを作成
    // const particlematerial = new THREE.PointsMaterial({
    // // 一つ一つのサイズ
    // size: 2,
    // // 色
    // color: 0xFFFFCC,
    // });

    // 物体を作成
    // const mesha = new THREE.Points(particlegeometry, particlematerial);
    // scene.add(mesha); // シーンは任意の THREE.Scene インスタンス

}

function animate() {
    if (moveUpX) {
        paddle1.position.y += 0.1 * speedrate;
    } else if (moveDownX) {
        paddle1.position.y -= 0.1 * speedrate;
    } else if (moveUpY) {
        paddle2.position.y += 0.1 * speedrate;
    } else if (moveDownY) {
        paddle2.position.y -= 0.1 * speedrate;
    }

    gameSocket.send(JSON.stringify({
        'message': 'update_position',
        'player1_y': paddle1.position.y * 100,  // サーバーでのスケーリングを考慮
        'player2_y': paddle2.position.y * 100,  // サーバーでのスケーリングを考慮        
    }));
        
    // } else {
    //     ball.position.x = targetBallPosition.x;
    //     ball.position.y = targetBallPosition.y;

    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

function updateGameState(data) {
   //#endregion console.log(data);
    if (data.info === 'paddle'){
        paddle1.position.y = data.player1_y / 100;
        paddle2.position.y = data.player2_y / 100;    
    } else if (data.info === 'ball'){        
        ball.position.x = data.ball_x / 100;
        ball.position.y = data.ball_y / 100;
    } else if (data.info === 'score'){        
        if (score_player1 != data.score_player1){
            score_player1 = data.score_player1;
            displayScore(score_player1,score_player2);
        }
        if (score_player2 != data.score_player2){
            score_player2 = data.score_player2;
            displayScore(score_player1,score_player2);
        }
    } else {
        paddle1.position.y = data.player1_y / 100;
        paddle2.position.y = data.player2_y / 100;    
        ball.position.x = data.ball_x / 100;
        ball.position.y = data.ball_y / 100;
        if (score_player1 != data.score_player1){
            score_player1 = data.score_player1;
            displayScore(score_player1,score_player2);
        }
        if (score_player2 != data.score_player2){
            score_player2 = data.score_player2;
            displayScore(score_player1,score_player2);
        }
    }

//    renderer.render(scene, camera);
}

function displayScore(score1, score2){
    // オーバーレイCanvasの2Dコンテキストを取得
    const context = overlayCanvas.getContext('2d');

    // テキストの設定
    const txt_score1 = score1;
    const txt_score1_x = 10; // テキストの描画位置（x座標）
    const txt_score1_y = 180; // テキストの描画位置（y座標）
    const txt_score2 = score2;
    const txt_score2_x = 750; // テキストの描画位置（x座標）
    const txt_score2_y = 180; // テキストの描画位置（y座標）

    // フォントとスタイルを設定
    context.font = '30px Arial';
    context.fillStyle = 'white';

    console.log(context.canvas.width);
    console.log(context.canvas.height);
    

    context.clearRect(0, 0, context.canvas.width, context.canvas.height);
// テキストを描画
    context.fillText(txt_score2, txt_score2_x, txt_score2_y);
    context.fillText(txt_score1, txt_score1_x, txt_score1_y);   

        // 一定時間後にテキストを消去
    setTimeout(() => {
        // テキストを消去するために背景色で上書き
        context.clearRect(txt_score2_x, txt_score2_y - 10, context.measureText(txt_score2.width), 40);
        context.clearRect(txt_score1_x, txt_score1_y - 10, context.measureText(txt_score1.width), 40);
    }, 100); // 3秒後に消去
}

function onKeyDown(e) {
    if (e.key === 'ArrowUp') {
        moveUpX = true;
    } else if (e.key === 'ArrowDown') {
        moveDownX = true;
    } else if (e.key === 'a' || e.key === 'A') {
        moveUpY = true;
    } else if (e.key === 'z' || e.key === 'Z') {
        moveDownY = true;
    }
}

function onKeyUp(e) {
    if (e.key === 'ArrowUp') {
        moveUpX = false;
    } else if (e.key === 'ArrowDown') {
        moveDownX = false;
    } else if (e.key === 'a' || e.key === 'A') {
        moveUpY = false;
    } else if (e.key === 'z' || e.key === 'Z') {
        moveDownY = false;
    }
}

function connect(){
    gameSocket = new WebSocket('wss://' + window.location.host + '/ws/game/');
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
        // 自動再接続
        setTimeout(connect, reconnectInterval);
    };
}

document.addEventListener('keydown', onKeyDown);
document.addEventListener('keyup', onKeyUp);

init();
connect();