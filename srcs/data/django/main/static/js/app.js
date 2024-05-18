// ページの初期コンテンツを取得して表示
fetch(window.location.href)
  .then(function (response) {
    return response.text();
  })
  .then(function (html) {
    // 取得したHTMLからコンテンツを抽出
    var parser = new DOMParser();
    var doc = parser.parseFromString(html, 'text/html');
    var content = doc.querySelector('#content').innerHTML;

    // ページのコンテンツを更新
    document.querySelector('#content').innerHTML = content;
  });

// リンククリック時のイベントハンドラ
document.addEventListener('click', function (event) {
  // クリックされた要素が <a> タグであるかどうかを確認
  if (event.target.tagName.toLowerCase() === 'a') {
    event.preventDefault();

    // クリックされたリンクの href 属性値を取得
    // var href = event.target.getAttribute('href');
    var href = event.target.getAttribute('data-url');



    // 非同期通信でページのコンテンツを取得
    fetch(href)
      .then(function (response) {
        return response.text();
      })
      .then(function (html) {
        loadPage(html);

        // 取得したコンテンツのURLを配列に追加
        history.pushState({ url: href }, '', '');
      });
  }
});

// popstate イベントのハンドリング
window.addEventListener('popstate', function (event) {
  // 直前のページのURLを取得
  var url = event.state ? event.state.url : window.location.href;

  // 非同期通信でページのコンテンツを取得
  fetch(url)
    .then(function (response) {
      return response.text();
    })
    .then(function (html) {
      loadPage(html);
    });
});

function loadPage(html) {
  var parser = new DOMParser();
  var doc = parser.parseFromString(html, 'text/html');
  var content = doc.querySelector('#content').innerHTML;
  var contenthead = doc.querySelector('#head').innerHTML;
  var contentfoot = doc.querySelector('#foot').innerHTML;
  var content_title = doc.querySelector('title');

  // ページのコンテンツを更新
  document.querySelector('#content').innerHTML = content;
  document.querySelector('#head').innerHTML = contenthead;
  document.querySelector('#foot').innerHTML = contentfoot;
  document.title = content_title.textContent;

  //ここからheaderにscriptをいれる
  newCode = doc.querySelector('#headerscript').innerHTML;
  // <head> タグを取得
  const head = document.head;
  // 既存のスクリプトタグを削除
  const scripts = head.querySelectorAll('script');
  scripts.forEach(script => script.remove());
  // 新しいスクリプトタグを作成してコードを追加
  const newScript = document.createElement('script');
  newScript.textContent = newCode;
  // <head> タグに新しいスクリプトタグを挿入
  head.appendChild(newScript);

  //ここからheaderにscriptをいれる
  rawFile = doc.querySelector('#headerscriptfile').innerHTML;
  scriptFiles = rawFile.trim().split("\n");

  for (i = 0; i < scriptFiles.length; i++) {
    if (scriptFiles[i] === "")
      continue;
    // 新しいスクリプトタグを作成してコードを追加
    let arrayScript = document.createElement('script');
    arrayScript.src = scriptFiles[i].trim() + "?timestamp=" + new Date().getTime();
    // <foot> タグに新しいスクリプトタグを挿入
    foot.appendChild(arrayScript);
  }


}