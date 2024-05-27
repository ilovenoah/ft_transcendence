document.addEventListener("DOMContentLoaded", function() {


  var postData = {};
  postData['page'] = 'top'; 
  postData['data_url']= '/process-post/';
  send_ajax(postData);


  var links = document.querySelectorAll(".post-link");

  // CSRFトークンをmetaタグから取得
  var csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  //const csrftoken = getCookie('csrftoken');


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
    if (event.target.matches('.ajax-form')) {
      event.preventDefault();
      
      const form = event.target;
      const formData = new FormData(form);
      const formJSON = Object.fromEntries(formData.entries());


      const xhr = new XMLHttpRequest();
      xhr.open('POST', form.action, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
  
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

 
  
function updateContent(data) {
  // 表示内容をデータに基づいて更新する処理
  // ここに実際の更新ロジックを記述


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

// popstateイベントをリッスン
window.addEventListener("popstate", function(event) {
  if (event.state) {
    // 状態オブジェクトが存在する場合、表示内容を更新
    updateContent(event.state.data);
  }
});

function send_ajax(data)
{
  // CSRFトークンをmetaタグから取得
  var csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

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


