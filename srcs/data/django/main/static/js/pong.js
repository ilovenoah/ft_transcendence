let scene, camera, renderer, overlayCanvas, paddle1, paddle2, paddle3, paddle4, ball, score;
// let player1Y = 0;
// let player2Y = 0;
let paddle1length = 6;
let paddle2length = 6;
let paddle3length = 6;
let paddle4length = 6;
let gameSocket;

let player_id = 0;
let player_no = 0;
let game_id;
let is_doubles = 0;

let moveUp1 = false;
let moveDown1 = false;
let moveUp2 = false;
let moveDown2 = false;
let moveUp3 = false;
let moveDown3 = false;
let moveUp4 = false;
let moveDown4 = false;
let wrate = 0.0;

let score_player1;
let score_player2;

let speedrate = 5.0;

let game_state = 0;

let score_match = 10;
let paddleflag = 0;

let lastUpdateTime = Date.now();
const updateInterval = 1000;  // 1秒
const animationInterval = 100;  // 10ms

let reconnectInterval = 100; // 再接続の間隔
let first_flag;

function init() {
    
    wwidth = window.innerWidth * 0.8;
    wheight = window.innerHeight * 0.8;
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
    overlayCanvas.width = screen.width;
    overlayCanvas.height = window.innerHeight * 0.9;
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

    const paddle3Geometry = new THREE.BoxGeometry(0.5, paddle3length, 0.5);
    const paddle3Material = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
    paddle3 = new THREE.Mesh(paddle3Geometry, paddle3Material);
    paddle3.position.x = 18.75;
    if (is_doubles == 1){
        scene.add(paddle3);
    }

    const paddle4Geometry = new THREE.BoxGeometry(0.5, paddle4length, 0.5);
    const paddle4Material = new THREE.MeshPhongMaterial({ color: 0xff0000 });
    paddle4 = new THREE.Mesh(paddle4Geometry, paddle4Material);
    paddle4.position.x = -18.75;
    if (is_doubles == 1){
        scene.add(paddle4);
    }
    



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

    if (paddleflag > 0){
        if (moveUp1 && player_no == 1) {
            paddle1.position.y += 0.1 * speedrate;
        } else if (moveDown1 && player_no == 1) {
            paddle1.position.y -= 0.1 * speedrate;
        } else if (moveUp2 && player_no == 2) {
            paddle2.position.y += 0.1 * speedrate;
        } else if (moveDown2 && player_no == 2) {
            paddle2.position.y -= 0.1 * speedrate;
        } else if (moveUp1 && player_no == 2) {
            paddle2.position.y += 0.1 * speedrate;
        } else if (moveDown1 && player_no == 2) {
            paddle2.position.y -= 0.1 * speedrate;
        } else if (moveUp1 && player_no == 3) {
            paddle3.position.y += 0.1 * speedrate;
        } else if (moveDown1 && player_no == 3) {
            paddle3.position.y -= 0.1 * speedrate;
        } else if (moveUp1 && player_no == 4) {
            paddle4.position.y += 0.1 * speedrate;
        } else if (moveDown1 && player_no == 4) {
            paddle4.position.y -= 0.1 * speedrate;
        }


        if (gameSocket.readyState === WebSocket.OPEN) {
            if (player_no == 1) {
                gameSocket.send(JSON.stringify({
                    'message': 'update_position',
                    'player1_y': paddle1.position.y * 100,  // サーバーでのスケーリングを考慮
                }));
            }
            else if (player_no == 2) {
                gameSocket.send(JSON.stringify({
                    'message': 'update_position',
                    'player2_y': paddle2.position.y * 100,  // サーバーでのスケーリングを考慮        
                }));
            }
            else if (player_no == 3) {
                gameSocket.send(JSON.stringify({
                    'message': 'update_position',
                    'player3_y': paddle3.position.y * 100,  // サーバーでのスケーリングを考慮        
                }));
            }
            else if (player_no == 4) {
                gameSocket.send(JSON.stringify({
                    'message': 'update_position',
                    'player4_y': paddle4.position.y * 100,  // サーバーでのスケーリングを考慮        
                }));
            }




        } else {
            // 接続が確立されるまで再試行
            // setTimeout(() => sendMessage(message), 100);  // 100ms後に再試行
        }

    }
        
    // } else {
    //     ball.position.x = targetBallPosition.x;
    //     ball.position.y = targetBallPosition.y;

    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

function updateGameState(data) {
   //#endregion console.log(data);
    paddleflag = 1;


    if (data.info === 'paddle'){
        if (player_no != 1){
            paddle1.position.y = data.paddle_1[1] / 100;
        }
        if (player_no != 2){
            paddle2.position.y = data.paddle_2[1] / 100;    
        }
        if (player_no != 3 && data.paddle_3){
            paddle3.position.y = data.paddle_3[1] / 100;
        }
        if (player_no != 4 && data.paddle_4){
            paddle4.position.y = data.paddle_4[1] / 100;
        }
    } else if (data.info === 'ball'){        
        ball.position.x = data.ball[0] / 100;
        ball.position.y = data.ball[1] / 100;
    } else if (data.info === 'score'){        
        if (score_player1 != data.scores[0]){
            score_player1 = data.scores[0];
            displayScore(score_player1,score_player2);
        }
        if (score_player2 != data.scores[1]){
            score_player2 = data.scores[1];
            displayScore(score_player1,score_player2);
        }
    } else {
        if (player_no != 1){
            paddle1.position.y = data.paddle_1[1] / 100;
        }
        if (player_no != 2){
            paddle2.position.y = data.paddle_2[1] / 100;
        }
        if (player_no != 3 && data.paddle_3){
            paddle3.position.y = data.paddle_3[1] / 100;
        }
        if (player_no != 4 && data.paddle_4){
            paddle4.position.y = data.paddle_4[1] / 100;
        }
        
        ball.position.x = data.ball[0] / 100;
        ball.position.y = data.ball[1] / 100;

        game_state = data.status;
        
        if (first_flag) {
            score_player1 = data.scores[0];
            score_player2 = data.scores[1];
            displayScore(score_player1,score_player2);
            first_flag = false;
        } else {
            if (score_player1 != data.scores[0]){
                score_player1 = data.scores[0];
                displayScore(score_player1,score_player2);
            }
            if (score_player2 != data.scores[1]){
                score_player2 = data.scores[1];
                displayScore(score_player1,score_player2);
            }
        }
    }

//    renderer.render(scene, camera);
}

function displayScore(score1, score2){
    // オーバーレイCanvasの2Dコンテキストを取得
    const context = overlayCanvas.getContext('2d');

    // テキストの設定
    const canvas_top = document.getElementById('gameCanvas').getBoundingClientRect().top;
    const canvas_left = document.getElementById('gameCanvas').getBoundingClientRect().left;
    const canvas_width = document.getElementById('gameCanvas').getBoundingClientRect().width;
//    const canvas_height = document.getElementById('gameCanvas').getBoundingClientRect().height;
    const canvas_height = window.innerHeight;
    
    const txt_score1 = score1;
    const txt_score1_x = Math.trunc(canvas_left + canvas_width / 50.0 * 47.0); // テキストの描画位置（x座標）
    const txt_score1_y = Math.trunc(canvas_top + canvas_height / 10.0); // テキストの描画位置（y座標）
    const txt_score2 = score2;
    const txt_score2_x = Math.trunc(canvas_left + canvas_width / 50.0 * 1.0); // テキストの描画位置（x座標）
    const txt_score2_y = Math.trunc(canvas_top + canvas_height / 10.0 ); // テキストの描画位置（y座標）




    // フォントとスタイルを設定
    context.font = canvas_width / 20.0 + 'px Arial';
    context.fillStyle = 'white';
    
    context.clearRect(0, 0, screen.width, screen.height);
    // テキストを描画
    context.fillText(txt_score2, txt_score2_x, txt_score2_y);
    context.fillText(txt_score1, txt_score1_x, txt_score1_y);   

    if (score1 >= score_match || score2 >= score_match) {
        txt_win = "Win!";
        txt_lose = "Lose!";
        txt_win_x = 0;
        txt_win_y = Math.trunc(canvas_top + canvas_height / 3.0 );
        txt_lose_x = 0;
        txt_lose_y = Math.trunc(canvas_top + canvas_height / 3.0 );
        
        if (score1 - score2 > 1) {
            txt_win_x = Math.trunc(canvas_left + canvas_width / 50.0 * 33.0); // テキストの描画位置（x座標）
            txt_lose_x = Math.trunc(canvas_left + canvas_width / 50.0 * 10.0); // テキストの描画位置（x座標）
        } else if (score2 - score1 > 1){
            txt_win_x = Math.trunc(canvas_left + canvas_width / 50.0 * 10.0); // テキストの描画位置（x座標）
            txt_lose_x = Math.trunc(canvas_left + canvas_width / 50.0 * 33.0); // テキストの描画位置（x座標）
        }
        context.fillText(txt_win, txt_win_x, txt_win_y);
        context.fillText(txt_lose, txt_lose_x, txt_lose_y);
    }


    // 一定時間後にテキストを消去
    // setTimeout(() => {
    //     // テキストを消去するために背景色で上書き
    //     context.clearRect(txt_score2_x, txt_score2_y - 30, 50, 40);
    //     context.clearRect(txt_score1_x, txt_score1_y - 30, 50, 40);
    // }, 3000); // 3秒後に消去
}

function onKeyDown(e) {
    if (e.key === 'ArrowUp' || e.key === 'ArrowRight') {
        moveUp3 = true;
    } else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') {
        moveDown3 = true;
    } else if (e.key === 'i' || e.key === 'I' || e.key === 'l' || e.key === 'L') {
        moveUp1 = true;
    } else if (e.key === 'k' || e.key === 'K' || e.key === 'j' || e.key === 'J') {
        moveDown1 = true;
    } else if (e.key === 'w' || e.key === 'W' || e.key === 'd' || e.key === 'D') {
        moveUp2 = true;
    } else if (e.key === 's' || e.key === 'S' || e.key === 'a' || e.key === 'A') {
        moveDown2 = true;
    }}

function onKeyUp(e) {
    if (e.key === 'i' || e.key === 'I' || e.key === 'l' || e.key === 'L') {
        moveUp1 = false;
    } else if (e.key === 'k' || e.key === 'K' || e.key === 'j' || e.key === 'J') {
        moveDown1 = false;
    } else if (e.key === 'w' || e.key === 'W' || e.key === 'd' || e.key === 'D') {
        moveUp2 = false;
    } else if (e.key === 's' || e.key === 'S' || e.key === 'a' || e.key === 'A') {
        moveDown2 = false;
    }
}


function connect(roomName){
    
    gameSocket = new WebSocket('wss://' + window.location.host + '/ws/pong/' + roomName + "/");
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
        if (game_state < 2){
            setTimeout( connect(game_id), reconnectInterval);
        }
    };
}

document.addEventListener('keydown', onKeyDown);
document.addEventListener('keyup', onKeyUp);

window.addEventListener('click', (event) => {
    // クリックされた要素を取得
    var link = event.target;
    while (link && link.tagName !== 'A') {
        link = link.parentElement;
    }
    if (link != null && link.tagName === 'A') {
        if (link.getAttribute('ready') && link.getAttribute('ready') == '1') {
            event.preventDefault();
            const message = {
                'message': 'ready_state',
                'data': player_id
            };
            gameSocket.send(JSON.stringify(message));
        }
        // 要素が属性 page="ponggame" を持っているか確認
        else if (link.getAttribute('page') && link.getAttribute('page') !== 'ponggame2') {
            if (gameSocket) {
                gameSocket.close();
            }
        }
    }
});

window.addEventListener('beforeunload', () => {
    if (gameSocket) {
        gameSocket.close();
    }
});

window.addEventListener('popstate', function(event) {
    if (gameSocket) {
        gameSocket.close();
    }
});



function startGame(gameid, playno, playid, dobules_flag){
    game_id = gameid;
    player_id = playid;
    player_no = playno;
    is_doubles = dobules_flag;
    init();

    
    console.log(playno);
    console.log(playid);

    // let regexp = /\?gameid=(\d+)/
    // let match = document.currentScript.src.match(regexp);
    // let gameid = match[1];
    if (gameSocket) {
        gameSocket.close();
    }
    first_flag = true;
    connect(game_id);
}