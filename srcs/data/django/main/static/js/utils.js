document.addEventListener("DOMContentLoaded", function() {
  var links = document.querySelectorAll(".post-link");

  // CSRFトークンをmetaタグから取得
  var csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

  links.forEach(function(link) {
    link.addEventListener("click", function(event) {
      event.preventDefault();

      // 属性を取得し、オブジェクトに変換
      var postData = {};
      Array.from(link.attributes).forEach(function(attr) {
        postData[attr.name] = attr.value;
      });

      var xhr = new XMLHttpRequest();
      xhr.open("POST", link.getAttribute("data-url"), true);
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
      xhr.send(JSON.stringify(postData));
    });
  });
});

//formの送信スクリプトを挿入







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

  // ページのコンテンツを更新
  document.querySelector('#content').innerHTML = data.content;
  document.querySelector('#head').innerHTML = data.head;
  document.querySelector('#foot').innerHTML = data.foot;
  document.title = data.title;

  //ここからheaderにscriptをいれる <data.jscripts> 
  jsCode = data.jscripts;
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
  
  //ここからfootにscriptfileをいれる <data.jsfiles>
  jsFiles = data.jsfiles;
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
