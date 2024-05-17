// ページの初期コンテンツを取得して表示
fetch(window.location.href)
  .then(function(response) {
    return response.text();
  })
  .then(function(html) {
    // 取得したHTMLからコンテンツを抽出
    var parser = new DOMParser();
    var doc = parser.parseFromString(html, 'text/html');
    var content = doc.querySelector('#content').innerHTML;

    // ページのコンテンツを更新
    document.querySelector('#content').innerHTML = content;
  });

// リンククリック時のイベントハンドラ
document.addEventListener('click', function(event) {
  // クリックされた要素が <a> タグであるかどうかを確認
  if (event.target.tagName.toLowerCase() === 'a') {
    event.preventDefault();

    // クリックされたリンクの href 属性値を取得
    // var href = event.target.getAttribute('href');
    var href = event.target.getAttribute('data-url');



    // 非同期通信でページのコンテンツを取得
    fetch(href)
      .then(function(response) {
        return response.text();
      })
      .then(function(html) {
        // 取得したHTMLからコンテンツを抽出
        var parser = new DOMParser();
        var doc = parser.parseFromString(html, 'text/html');
        var content = doc.querySelector('#content').innerHTML;

        // ページのコンテンツを更新
        document.querySelector('#content').innerHTML = content;

        // 取得したコンテンツのURLを配列に追加
        history.pushState({url: href}, '', '');
      });
  }
});

// popstate イベントのハンドリング
window.addEventListener('popstate', function(event) {
  // 直前のページのURLを取得
  var url = event.state ? event.state.url : window.location.href;

  // 非同期通信でページのコンテンツを取得
  fetch(url)
    .then(function(response) {
      return response.text();
    })
    .then(function(html) {
      // 取得したHTMLからコンテンツを抽出
      var parser = new DOMParser();
      var doc = parser.parseFromString(html, 'text/html');
      var content = doc.querySelector('#content').innerHTML;

      // ページのコンテンツを更新
      document.querySelector('#content').innerHTML = content;
    });
});
