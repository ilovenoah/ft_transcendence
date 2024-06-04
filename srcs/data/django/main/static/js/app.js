document.addEventListener("DOMContentLoaded", function() {

  // 3分ごとにheartbeatを送信
  setInterval(sendHeartbeat, 3 * 60 * 1000);
  // ページ読み込み時に初回heartbeatを送信
  sendHeartbeat();

  var postData = {};
  postData['page'] = 'top'; 
  postData['data_url']= 'process-post/';
  send_ajax(postData);


  var links = document.querySelectorAll(".post-link");

  // CSRFトークンをmetaタグから取得
  var csrfToken = getCSRFToken();
  
  links.forEach(function(link) {
    link.addEventListener("click", function(event) {
      event.preventDefault();
  // 属性を取得し、オブジェクトに変換
      var postData = {};
      Array.from(link.attributes).forEach(function(attr) {
        postData[attr.name] = attr.value;
      });


      send_ajax(postData);
    });
  });


  document.addEventListener('submit', function(event) {
    //ファイルをアップロードするときのform
    if (event.target.matches('.ajax-upload'))
    {
        event.preventDefault();

        var image = document.getElementById('image').files[0];

        var maxSize = 5 * 1024 * 1024;  // 5MB
        if (image.size > maxSize) {
            document.getElementById('result').innerText = "ファイルサイズが5MBを超えています。";
            return;
        }

        var formData = new FormData();
        formData.append('image', image);
        formData.append('imgtagid', 'uploaded');
        formData.append('msgtagid', 'result');

        var xhr = new XMLHttpRequest();
        xhr.open('POST', 'upload/', true);

        xhr.onload = function() {
            if (xhr.status === 200) {
              const response = JSON.parse(xhr.responseText);
              document.getElementById('result').innerText = response.message;
              document.getElementById('uploaded').src = response.imgsrc;
              document.getElementById('descimage').innertext ="画像";
              if (typeof response.exec !== 'undefined') {     
                eval(response.exec);
              }
            } else {
                document.getElementById('result').innerText = JSON.parse(xhr.responseText).error;
            }
        };
        xhr.send(formData);

    //textデータを送信するときのform
    } else if (event.target.matches('.ajax-form')) {
      event.preventDefault();
      
      const form = event.target;
      const formData = new FormData(form);
      const formJSON = Object.fromEntries(formData.entries());


      const xhr = new XMLHttpRequest();
      xhr.open('POST', form.action, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
  
      csrfToken = getCSRFToken();
      // CSRFトークンの変数が未定義でないことを確認
      if (typeof csrfToken !== 'undefined') {
        xhr.setRequestHeader('X-CSRFToken', csrfToken);
      } else {
        console.error('CSRF token is not defined.');
        return;
      }
  
      xhr.onload = function() {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          // データを更新する
          updateContent(response);
          // 履歴にページを登録
          history.pushState({ data: response }, response.title, '');
        } else {
          console.error('Error:', xhr.statusText);
            // エラー処理をここに追加します     
        }
      };
  
      xhr.onerror = function() {
        console.error('Request failed');
        // ネットワークエラーの処理をここに追加します
      };

      xhr.send(JSON.stringify(formJSON));
    }
  });
});

// popstateイベントをリッスン
window.addEventListener("popstate", function(event) {
  if (event.state) {
    // 状態オブジェクトが存在する場合、表示内容を更新
    updateContent(event.state.data);
  }
});
  
function updateContent(data) {
  // 表示内容をデータに基づいて更新する処理
  // ここに実際の更新ロジックを記述

  //本来は失敗したときのことを記述したりすべき
  updateCSRFToken()

  // ページのコンテンツを更新
  if (typeof data.content !== 'undefined') {     
    document.querySelector('#content').innerHTML = data.content;
  }
  if (typeof data.head !== 'undefined') {     
    document.querySelector('#head').innerHTML = data.head;
  }
  if (typeof data.foot !== 'undefined') {     
    document.querySelector('#foot').innerHTML = data.foot;
  }
  if (typeof data.title !== 'undefined') {     
    document.title = data.title;
  } else {
    document.title = '42tokyo';
  }



  if (typeof data.rawscripts !== 'undefined') {     
    //ここからheaderにscriptをいれる <data.rawscripts> 
    jsCode = data.rawscripts;
    // <head> タグを取得
    const head = document.head;
    // 既存のスクリプトタグを削除
    const scripts = head.querySelectorAll('script');
    scripts.forEach(script => script.remove());
    // 新しいスクリプトタグを作成してコードを追加
    const jsScript = document.createElement('script');
    jsScript.textContent = jsCode;
    // <head> タグに新しいスクリプトタグを挿入
    head.appendChild(jsScript);
  }

  //ここからfootにscriptfileをいれる <data.scriptfiles>
  if (typeof data.scriptfiles !== 'undefined') {     
    jsFiles = data.scriptfiles;
    scriptFiles = jsFiles.trim().split("\n");
    for (i = 0; i < scriptFiles.length; i++) {
      //値が空のときは実行しない
      if (scriptFiles[i] === "")
        continue;
      // 新しいスクリプトタグを作成してコードを追加
      let arrayScript = document.createElement('script');
      //キャッシュされたjsファイルが利用されないようにtimestampを付加する
      arrayScript.src = scriptFiles[i].trim() + "?ts=" + new Date().getTime();
      // <foot> タグに新しいスクリプトタグを挿入
      foot.appendChild(arrayScript);
    }
  }
}

function send_ajax(data)
{
  // CSRFトークンをmetaタグから取得
  const csrfToken = getCSRFToken();

  var xhr = new XMLHttpRequest();
  xhr.open("POST", data.data_url, true);
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.setRequestHeader("X-CSRFToken", csrfToken);  // CSRFトークンをヘッダーに設定
  xhr.onreadystatechange = function() {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      var parser = new DOMParser();
      if (xhr.status === 200) {
        var response = JSON.parse(xhr.responseText);
        //データを更新する
        updateContent(response);
        //履歴にページを登録
        history.pushState({ data: response }, response.title, '');
      } else {
        console.error('There was a problem with the request:', xhr.statusText);
      }
    }
  };  
  xhr.send(JSON.stringify(data));
}

// CSRFトークンを取得する関数
function getCSRFToken() {
  return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// CSRFトークンを更新する関数
function updateCSRFToken(callback) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', 'get-csrf-token/', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onreadystatechange = function() {
      if (xhr.readyState === 4 && xhr.status === 200) {
          var data = JSON.parse(xhr.responseText);
          document.querySelector('meta[name="csrf-token"]').setAttribute('content', data.csrfToken);
          if (callback) callback();
      }
  };
  xhr.send();
}


function sendHeartbeat() {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', 'heartbeat/', true);
  xhr.withCredentials = true;

  xhr.onreadystatechange = function() {
      if (xhr.readyState === 4) {
          if (xhr.status === 200) {
              var response = JSON.parse(xhr.responseText);
              console.log('User is:', response.status);
              // ログイン状態に応じた処理
          } else {
              console.error('Error: ', xhr.status);
              // ログアウト状態に応じた処理
          }
      }
  };

  xhr.send();
}

